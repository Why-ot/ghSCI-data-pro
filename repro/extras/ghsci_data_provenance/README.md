# ghSCI-data — R3-A 台阶高度测量数据

2026-11-05 采集。D435 (sn 342222072464, fw 5.13.0.55)，垂直俯视，工作距离约 355 mm，
30 帧/摆放，原始 Z16 深度未对齐、无滤波。

## 结构
| 路径 | 内容 |
|---|---|
| `captures/r3a_live_20261105/chunks/` | 90 MB 分卷 |
| `manifests/` | 原 tar 的 SHA256 |
| `results/r3a_results.csv` | 30 个摆放的台阶测量结果 |
| `scripts/` | 分割与还原脚本 |

## 还原
```bash
cat captures/r3a_live_20261105/chunks/*.part-* > /tmp/r3a.tar.gz
sha256sum -c manifests/r3a_live_20261105.tar.gz.sha256
tar xzf /tmp/r3a.tar.gz   # 得到 live/<标签>/{depth_raw,color_raw,meta.json}
```

## 结果摘要
台阶系统性正偏 +0.91~+1.58 mm；0°/180° 配对差 +0.30±0.07 mm；黑/灰差 −0.09 mm。
