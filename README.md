# herdrbot

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [繁體中文](README.zh-TW.md)

[![Herdrbot intro video (click for the mp4)](docs/media/herdrbot-intro.gif)](docs/media/herdrbot-intro.mp4)

The engine for the **Herdrbot** Grok Bot — the scripts and config examples that sit
behind Herdrbot's skills. Skill prose lives in the bot template; anything executable lives here.

Currently: `bin/watchgate.py`, a model-free watch gate. Every `interval` seconds (default 300)
it runs `herdr --machine <label> agent list` for each machine in `~/.herdrbot/config.json`,
compares with the last snapshot, and POSTs to Herdrbot's "Herdr signal" webhook **only when
something meaningful changed** — so the bot wakes up only when there is something to judge.

Compared per pane: new pane, closed pane, `agent_status` change, `completion_seq` change.
Focus and revision are ignored. Machines going unreachable / reachable are reported once each.

## Install

```sh
git clone https://github.com/devicki/herdrbot ~/.herdrbot/engine
cp ~/.herdrbot/engine/examples/gate.conf.example ~/.herdrbot/gate.conf
chmod 600 ~/.herdrbot/gate.conf      # then fill in url and key
# ~/.herdrbot/config.json: see examples/config.example.json (Herdrbot's setup skill writes it)
setsid nohup python3 ~/.herdrbot/engine/bin/watchgate.py >/dev/null 2>&1 </dev/null &
```

Files the gate uses in `~/.herdrbot` (never in the repo): `config.json`, `gate.conf`,
`gate_snapshot.json`, `gate.log`, `gate.pid`. The webhook key is never written to the log.

Environment overrides: `HERDRBOT_HOME` (default `~/.herdrbot`), `HERDR_BIN` (default `~/.local/bin/herdr`).

## Update

```sh
git -C ~/.herdrbot/engine pull --ff-only
```

If anything under `bin/` changed, restart the gate: `kill $(cat ~/.herdrbot/gate.pid)` and start it again
with the command above.

## Payload

`POST <url>` with `Authorization: Bearer <key>` and `Content-Type: application/json`:

```json
{"type": "gate", "changes": [
  {"machine": "laptop", "pane": "p1", "change": "new", "status": "working", "seq": 0, "agent": "claude", "title": "..."},
  {"machine": "laptop", "pane": "p2", "change": "closed"},
  {"machine": "laptop", "pane": "p3", "change": "status", "from": "working", "status": "done", "seq": 4, "agent": "claude", "title": "..."},
  {"machine": "server", "change": "unreachable"},
  {"machine": "server", "change": "reachable"}
]}
```

If the POST fails, the snapshot is not advanced, so the same changes are retried next cycle.

## Migrating from `~/.herdrbot/bin/watchgate.py`

1. Clone the repo as above.
2. `kill $(cat ~/.herdrbot/gate.pid)`
3. Start the gate from `~/.herdrbot/engine/bin/watchgate.py`.
4. `rm ~/.herdrbot/bin/watchgate.py`

`config.json`, `gate.conf` and `gate_snapshot.json` stay where they are, so nothing is reported twice.

## Tests

```sh
python3 -m pytest -q tests
```

## License

MIT
