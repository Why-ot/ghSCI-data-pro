#!/usr/bin/env python3
"""
live_preview.py -- D435 实时取景 + 按需拍摄（单进程独占相机）

为什么是一体式
    RealSense 不能被两个进程同时打开。取景和拍摄分成两个程序，就要在每次
    摆放前后反复启停，25 次摆放会出错。这里让一个进程同时做两件事：
    持续取流 -> 浏览器看实时画面 -> 在网页上点一下就在原目录落盘 30 帧。

用法（Jetson 上）
    python3 live_preview.py --serial 317422072133 --out ~/R3A_CAPTURE/live --port 8080
    然后在 Windows 浏览器打开  http://192.168.31.230:8080

    取景页上：输入标签 -> 点 Capture  ->  落盘到 <out>/<label>/
              标签建议沿用正式命名：S40A_0deg_P01 / S40B_original_P01

设计约束
    * 只读相机，不发送任何机器人指令
    * 深度保存原始 Z16 PNG（不做对齐、不做滤波）
    * 元数据字段与 d435_capture_only.py 保持一致，便于两批数据合并分析
    * 预览是伪彩色，仅用于摆放；判断"有没有深度"要看原始零值比例
"""
import argparse, json, os, sys, threading, time, hashlib
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import shutil

import numpy as np
import cv2
import pyrealsense2 as rs

STATE = {'jpeg': None, 'fps': 0.0, 'valid': 0.0, 'ts': 0.0, 'frames': 0,
         'temp': None, 'busy': False, 'last': None}
BUF = deque(maxlen=40)          # ~40 帧 ≈ 78 MB，Jetson 内存有限，别加大
LOCK = threading.Lock()
ARGS = None


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def depth_preview(raw):
    valid = raw[raw > 0]
    gray = np.zeros(raw.shape, np.uint8)
    if valid.size:
        lo, hi = np.percentile(valid, [2, 98])
        if hi > lo:
            m = raw > 0
            gray[m] = np.clip((raw[m] - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
        return cv2.applyColorMap(gray, cv2.COLORMAP_TURBO)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def intrinsics_dict(p):
    i = p.as_video_stream_profile().get_intrinsics()
    return {'width': int(i.width), 'height': int(i.height), 'fx': float(i.fx),
            'fy': float(i.fy), 'ppx': float(i.ppx), 'ppy': float(i.ppy),
            'model': str(i.model), 'coeffs': list(map(float, i.coeffs))}


def reader():
    """持续取流，最新帧转 JPEG 给网页，同时把原始帧放进环形缓冲。"""
    p = rs.pipeline()
    c = rs.config()
    if ARGS.serial:
        c.enable_device(ARGS.serial)
    c.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
    c.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    prof = p.start(c)
    dev = prof.get_device()
    sensor = dev.first_depth_sensor()
    try:
        device_info = {'name': dev.get_info(rs.camera_info.name),
                       'serial': dev.get_info(rs.camera_info.serial_number),
                       'firmware': dev.get_info(rs.camera_info.firmware_version)}
    except Exception:
        device_info = {}
    STATE['device'] = device_info
    STATE['depth_scale'] = float(sensor.get_depth_scale())
    STATE['intrinsics'] = intrinsics_dict(prof.get_stream(rs.stream.depth))
    try:
        STATE['emitter'] = float(sensor.get_option(rs.option.emitter_enabled))
        STATE['auto_exposure'] = float(sensor.get_option(rs.option.enable_auto_exposure))
    except Exception:
        pass
    print('streaming', device_info, 'scale', STATE['depth_scale'], flush=True)

    t_last, n_last = time.time(), 0
    last_save = {}
    while True:
        try:
            f = p.wait_for_frames(timeout_ms=5000)
        except Exception as e:
            print('frame timeout', e, flush=True)
            time.sleep(0.2)
            continue
        d, col = f.get_depth_frame(), f.get_color_frame()
        if not d or not col:
            continue
        a = np.asanyarray(d.get_data()).copy()
        b = np.asanyarray(col.get_data()).copy()
        with LOCK:
            BUF.append((a, b, int(d.get_frame_number()), float(d.get_timestamp())))
            last_save['depth_meta'] = {'frame_number': int(d.get_frame_number()),
                                       'timestamp_ms': float(d.get_timestamp())}
        # 预览：每 3 帧编码一次，省 CPU
        STATE['frames'] += 1
        if STATE['frames'] % 3 == 0:
            vis = cv2.resize(depth_preview(a), (424, 240))
            col_small = cv2.resize(b, (320, 240))
            canvas = np.zeros((240, 424 + 320, 3), np.uint8)
            canvas[:, :424] = vis
            canvas[:, 424:] = col_small
            cv2.putText(canvas, 'depth (pseudo) %d mm' % int(np.median(a[a > 0]) if (a > 0).any() else 0),
                        (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            cv2.putText(canvas, 'zeros %.1f%%' % (100 * float((a == 0).mean())),
                        (6, 232), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            ok, jpg = cv2.imencode('.jpg', canvas, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                with LOCK:
                    STATE['jpeg'] = jpg.tobytes()
                    STATE['valid'] = 1.0 - float((a == 0).mean())
                    STATE['ts'] = time.time()
        if time.time() - t_last > 1.0:
            STATE['fps'] = (STATE['frames'] - n_last) / (time.time() - t_last)
            t_last, n_last = time.time(), STATE['frames']
            try:
                STATE['temp'] = float(sensor.get_option(rs.option.asic_temperature))
            except Exception:
                pass


def do_capture(label, n):
    """从环形缓冲里取最近 n 帧写盘，结构对齐 d435_capture_only.py。"""
    out = Path(ARGS.out) / label
    if out.exists():
        return {'ok': False, 'error': 'folder exists: %s' % out}
    with LOCK:
        frames = list(BUF)[-n:]
    if len(frames) < n:
        return {'ok': False, 'error': 'buffer has %d/%d frames' % (len(frames), n)}
    (out / 'depth_raw').mkdir(parents=True)
    (out / 'color_raw').mkdir(parents=True)
    recs, qcs = [], []
    for i, (a, b, fn, ts) in enumerate(frames):
        dp = out / 'depth_raw' / ('frame_%03d.png' % i)
        cp = out / 'color_raw' / ('frame_%03d.png' % i)
        if not cv2.imwrite(str(dp), a) or not cv2.imwrite(str(cp), b):
            return {'ok': False, 'error': 'PNG write failed at %d' % i}
        if i == 0:
            cv2.imwrite(str(out / 'preview_depth.png'), depth_preview(a))
            cv2.imwrite(str(out / 'preview_color.png'), b)
        recs.append({'index': i, 'depth': dp.name, 'color': cp.name,
                     'depth_sha256': sha256(dp), 'color_sha256': sha256(cp),
                     'depth_frame': {'frame_number': fn, 'timestamp_ms': ts}})
        qcs.append(1.0 - float((a == 0).mean()))
    meta = {'complete': True, 'captured_at': now_iso(), 'part': label,
            'frames_expected': n, 'frames_saved': len(recs),
            'full_frame_valid_ratio_min': min(qcs),
            'full_frame_valid_ratio_median': float(np.median(qcs)),
            'source': 'live_preview.py', 'device': STATE.get('device'),
            'depth_scale': STATE.get('depth_scale'), 'intrinsics': STATE.get('intrinsics'),
            'sensor_options': {'emitter_enabled': STATE.get('emitter'),
                               'enable_auto_exposure': STATE.get('auto_exposure')},
            'processing': 'none; raw Z16, unaligned to color',
            'quality_note': 'Full-frame QC only; ROI quality must be reviewed on preview images.',
            'frames': recs}
    (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    STATE['last'] = {'label': label, 'valid_median': meta['full_frame_valid_ratio_median'],
                     'at': meta['captured_at']}
    return {'ok': True, 'label': label, 'frames': len(recs),
            'valid_median': meta['full_frame_valid_ratio_median'], 'path': str(out)}


PAGE = """<!doctype html><meta charset=utf-8><title>D435 R3-A</title>
<style>body{background:#111;color:#ddd;font-family:monospace;margin:12px}
img{width:100%;max-width:1100px;border:1px solid #333}
input,button{font-size:16px;padding:6px;margin:4px 4px 4px 0}
.ok{color:#5f5}.bad{color:#f55}pre{background:#000;padding:8px}</style>
<h3>D435 实时取景 &mdash; 只读，不动机器人</h3>
<img src="/stream">
<div>
<input id=lab size=28 placeholder="S40A_0deg_P01" value="__LABEL__">
<button onclick="shoot()">Capture 30 frames</button>
<button onclick="st()">Status</button>
</div>
<pre id=out>ready</pre>
<script>
function shoot(){const l=document.getElementById('lab').value.trim();
 fetch('/shoot?label='+encodeURIComponent(l)).then(r=>r.json()).then(j=>{
  document.getElementById('out').textContent=JSON.stringify(j,null,1);});}
function st(){fetch('/status').then(r=>r.json()).then(j=>{
  document.getElementById('out').textContent=JSON.stringify(j,null,1);});}
setInterval(()=>{fetch('/status').then(r=>r.json()).then(j=>{
  document.title='D435 '+j.fps.toFixed(1)+'fps valid '+(j.valid*100).toFixed(1)+'%';});},3000);
</script>"""


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/':
            body = PAGE.replace('__LABEL__', ARGS.prefix).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    with LOCK:
                        jpg = STATE['jpeg']
                    if jpg:
                        self.wfile.write(b'--frame\r\nContent-Type: image/jpeg\r\n'
                                         b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n')
                        self.wfile.write(jpg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.08)
            except (BrokenPipeError, ConnectionResetError):
                return
        elif u.path == '/status':
            du = shutil.disk_usage(ARGS.out if os.path.isdir(ARGS.out) else str(Path(ARGS.out).parent))
            js = json.dumps({'fps': round(STATE['fps'], 1), 'valid': round(STATE['valid'], 4),
                             'zeros_pct': round(100 * (1 - STATE['valid']), 2),
                             'asic_temp_c': STATE.get('temp'), 'frames_served': STATE['frames'],
                             'disk_free_gib': round(du.free / 1024**3, 2),
                             'device': STATE.get('device'), 'depth_scale': STATE.get('depth_scale'),
                             'last_capture': STATE['last']}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(js)))
            self.end_headers()
            self.wfile.write(js)
        elif u.path == '/shoot':
            q = parse_qs(u.query)
            label = (q.get('label', [''])[0] or '').strip()
            n = int(q.get('n', [str(ARGS.frames)])[0])
            if not label or '/' in label or '..' in label:
                js = json.dumps({'ok': False, 'error': 'bad label'}).encode()
            else:
                STATE['busy'] = True
                try:
                    js = json.dumps(do_capture(label, n)).encode()
                finally:
                    STATE['busy'] = False
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(js)))
            self.end_headers()
            self.wfile.write(js)
        else:
            self.send_error(404)


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument('--serial', default='342222072464')
    ap.add_argument('--out', default=str(Path.home() / 'R3A_CAPTURE' / 'live'))
    ap.add_argument('--port', type=int, default=8080)
    ap.add_argument('--frames', type=int, default=30)
    ap.add_argument('--prefix', default='S40A_0deg_P01')
    ARGS = ap.parse_args()
    Path(ARGS.out).mkdir(parents=True, exist_ok=True)
    th = threading.Thread(target=reader, daemon=True)
    th.start()
    time.sleep(2.5)
    print('preview at http://<jetson-ip>:%d  out=%s' % (ARGS.port, ARGS.out), flush=True)
    ThreadingHTTPServer(('0.0.0.0', ARGS.port), H).serve_forever()


if __name__ == '__main__':
    sys.exit(main())

