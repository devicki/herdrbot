# herdrbot

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [繁體中文](README.zh-TW.md)

[![Herdrbot 介紹影片（點擊觀看 mp4）](docs/media/herdrbot-intro.gif)](https://github.com/devicki/herdrbot/raw/main/docs/media/herdrbot-intro.mp4)

## Herdrbot 是什麼？

Herdrbot 是一個 Grok Bot，擔任在你機器上 [Herdr](https://herdr.dev) 中執行的 AI 程式代理（Claude Code、Codex 等）的工頭。

- 告訴它要在哪裡建置或修正什麼，它會啟動一個代理（名為 `hb-...`）、交付任務、監看進度並帶回結果。
- 它會把卡住的核准問題轉給你（絕不自行回答權限對話框），並回報完成的工作。
- 可選擇讓它繼續執行代理提出的安全後續步驟（測試、文件、commit；push/tag 僅在啟用時）。預設關閉。
- 合併、部署、強制推送與刪除一律需要你核准。你自己啟動的代理仍歸你管。
- 它會發送早晨摘要，並每週檢查 Herdr 更新。
- [away-signal 外掛](https://github.com/devicki/herdr-away-signal)與本儲存庫的 watch 閘道讓它能即時反應，同時壓低模型執行成本。

本儲存庫是它的引擎：機器人技能所使用的腳本。

## 引擎

**Herdrbot** Grok Bot 的引擎：存放 Herdrbot 技能背後使用的腳本與設定範例。
技能說明文字放在機器人範本中；所有可執行的東西都放在這裡。

目前內容：`bin/watchgate.py`，一個不使用模型的 watch 閘道。每隔 `interval` 秒（預設 300），
它會對 `~/.herdrbot/config.json` 中的每台機器執行 `herdr --machine <label> agent list`，與上一次的快照比較，
**只有在發生有意義的變化時**才 POST 到 Herdrbot 的「Herdr signal」webhook，讓機器人只在需要判斷時才被喚醒。

每個 pane 比較的項目：新 pane、關閉的 pane、`agent_status` 變化、`completion_seq` 變化。
忽略 focus 與 revision。機器無法連線／恢復連線各只通知一次。

## 安裝

```sh
git clone https://github.com/devicki/herdrbot ~/.herdrbot/engine
cp ~/.herdrbot/engine/examples/gate.conf.example ~/.herdrbot/gate.conf
chmod 600 ~/.herdrbot/gate.conf      # 接著填入 url 與 key
# ~/.herdrbot/config.json：參考 examples/config.example.json（由 Herdrbot 的設定技能寫入）
setsid nohup python3 ~/.herdrbot/engine/bin/watchgate.py >/dev/null 2>&1 </dev/null &
```

閘道在 `~/.herdrbot` 中使用的檔案（絕不放進儲存庫）：`config.json`、`gate.conf`、`gate_snapshot.json`、
`gate.log`、`gate.pid`。webhook 金鑰絕不會寫入日誌。

環境變數：`HERDRBOT_HOME`（預設 `~/.herdrbot`）、`HERDR_BIN`（預設 `~/.local/bin/herdr`）。

## 更新

```sh
git -C ~/.herdrbot/engine pull --ff-only
```

若 `bin/` 下有變更，請重新啟動閘道：`kill $(cat ~/.herdrbot/gate.pid)`，再用上面的指令啟動。

## 酬載格式

`POST <url>`，標頭為 `Authorization: Bearer <key>` 與 `Content-Type: application/json`：

```json
{"type": "gate", "changes": [
  {"machine": "laptop", "pane": "p1", "change": "new", "status": "working", "seq": 0, "agent": "claude", "title": "..."},
  {"machine": "laptop", "pane": "p2", "change": "closed"},
  {"machine": "laptop", "pane": "p3", "change": "status", "from": "working", "status": "done", "seq": 4, "agent": "claude", "title": "..."},
  {"machine": "server", "change": "unreachable"},
  {"machine": "server", "change": "reachable"}
]}
```

POST 失敗時不會更新快照，因此相同的變化會在下一輪重新送出。

## 從 `~/.herdrbot/bin/watchgate.py` 遷移

1. 依上述方式複製儲存庫。
2. `kill $(cat ~/.herdrbot/gate.pid)`
3. 從 `~/.herdrbot/engine/bin/watchgate.py` 啟動閘道。
4. `rm ~/.herdrbot/bin/watchgate.py`

`config.json`、`gate.conf` 與 `gate_snapshot.json` 保留原位，因此不會重複通知。

## 測試

```sh
python3 -m pytest -q tests
```

## 授權

MIT
