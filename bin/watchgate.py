#!/usr/bin/env python3
"""Herdrbot watch gate: polls `herdr agent list` per machine (no model) and POSTs one
`{"type":"gate",...}` signal to the Herdr signal webhook only when something meaningful changed.
Config: $HERDRBOT_HOME/config.json (machines[].label); webhook in $HERDRBOT_HOME/gate.conf
(`url = ...`, `key = ...`, optional `interval = 300`). The key is never logged.
Env: HERDRBOT_HOME (default ~/.herdrbot), HERDR_BIN (default ~/.local/bin/herdr).
`--once` runs a single cycle and exits (used by tests)."""
import json, os, subprocess, sys, time, urllib.request
H = os.path.expanduser(os.environ.get("HERDRBOT_HOME", "~/.herdrbot"))
HERDR = os.path.expanduser(os.environ.get("HERDR_BIN", "~/.local/bin/herdr"))
SNAP = f"{H}/gate_snapshot.json"; LOG = f"{H}/gate.log"; PID = f"{H}/gate.pid"
def log(m):
    with open(LOG, "a") as f: f.write(time.strftime("%F %T ") + m + "\n")
def conf():
    c = {}
    for line in open(f"{H}/gate.conf"):
        line = line.split("#", 1)[0].strip()
        if "=" in line: k, v = line.split("=", 1); c[k.strip()] = v.strip()
    return c
def read(label):
    try:
        out = subprocess.run([HERDR, "--machine", label, "agent", "list"], capture_output=True, text=True, timeout=60)
        agents = json.loads(out.stdout)["result"]["agents"]
    except Exception:
        return None
    return {a["pane_id"]: {"status": a.get("agent_status"), "seq": a.get("completion_seq"),
            "agent": a.get("agent"), "title": a.get("terminal_title_stripped", "")[:80]} for a in agents}
def diff(label, old, new):
    ch = []
    if old is None:
        return []
    for p in new.keys() - old.keys(): ch.append({"machine": label, "pane": p, "change": "new", **new[p]})
    for p in old.keys() - new.keys(): ch.append({"machine": label, "pane": p, "change": "closed"})
    for p in new.keys() & old.keys():
        o, n = old[p], new[p]
        if o["status"] != n["status"] or o["seq"] != n["seq"]:
            ch.append({"machine": label, "pane": p, "change": "status", "from": o["status"], **n})
    return ch
def post(c, changes):
    body = json.dumps({"type": "gate", "changes": changes}).encode()
    req = urllib.request.Request(c["url"], body, {"Content-Type": "application/json", "Authorization": f"Bearer {c['key']}"})
    urllib.request.urlopen(req, timeout=30).read()
def main(once=False):
    with open(PID, "w") as f: f.write(str(os.getpid()))
    snap = json.load(open(SNAP)) if os.path.exists(SNAP) else {}
    while True:
        c = conf(); labels = [m["label"] for m in json.load(open(f"{H}/config.json"))["machines"]]
        new = {l: read(l) for l in labels}; changes = []
        down = set(snap.get("_down", []))
        for l in labels:
            if new[l] is None:
                if l not in down: changes.append({"machine": l, "change": "unreachable"}); down.add(l)
                continue
            if l in down: changes.append({"machine": l, "change": "reachable"}); down.discard(l)
            changes += diff(l, snap.get(l), new[l])
        if changes:
            try: post(c, changes); log(f"posted {len(changes)} change(s)")
            except Exception as e:
                log(f"post failed: {type(e).__name__}")
                if once: return
                time.sleep(int(c.get("interval", 300))); continue
        for l in labels:
            if new[l] is not None: snap[l] = new[l]
        snap["_down"] = sorted(down)
        json.dump(snap, open(SNAP, "w"))
        if once: return
        time.sleep(int(c.get("interval", 300)))
if __name__ == "__main__": main(once="--once" in sys.argv)
