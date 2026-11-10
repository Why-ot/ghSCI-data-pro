import json, time, sys
import piper_sdk
def read(ch):
    cls = getattr(piper_sdk, "C_PiperInterface_V2", None) or piper_sdk.C_PiperInterface
    p = cls(ch); p.ConnectPort(); time.sleep(0.8)
    raw = p.GetArmJointMsgs().joint_state
    v = [raw.joint_1, raw.joint_2, raw.joint_3, raw.joint_4, raw.joint_5, raw.joint_6]
    out = [x/1000.0 for x in v]
    try:
        en = p.GetArmEnableStatus()
    except Exception:
        en = None
    return out, en
def main():
    old = json.load(open("/home/yuanyou/R3A_CAPTURE/pose_20261105.json"))
    cur = {}
    for name, ch in (("left","can0"), ("right","can1")):
        try:
            v, en = read(ch)
            cur[name] = {"v": v, "en": str(en)}
        except Exception as e:
            cur[name] = {"err": repr(e)}
    print("channel  J1..J6 (current)")
    for k in ("left","right"):
        c = cur[k]
        if "err" in c:
            print(f"  {k:5s} ERROR {c['err'][:80]}"); continue
        print("  %-5s %s  enable=%s" % (k, " ".join("%8.2f"%x for x in c["v"]), c["en"]))
    print("\n  delta vs 2026-11-05 (same unit as printed):")
    for k in ("left","right"):
        c = cur.get(k,{}); o = old.get(k,{})
        if "v" not in c or "deg" not in o: continue
        d = [c["v"][i]-o["deg"][i] for i in range(6)]
        print("  %-5s %s   max|d| = %.2f" % (k, " ".join("%+8.2f"%x for x in d), max(abs(x) for x in d)))
    json.dump(cur, open("/home/yuanyou/R3A_CAPTURE/pose_20261106.json","w"), indent=2)
    print("\nsaved pose_20261106.json")
main()