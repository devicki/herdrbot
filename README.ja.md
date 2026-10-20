# herdrbot

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [繁體中文](README.zh-TW.md)

[![Herdrbot 紹介動画（クリックで mp4）](docs/media/herdrbot-intro.gif)](docs/media/herdrbot-intro.mp4)

**Herdrbot** Grok Bot のエンジンです。Herdrbot のスキルの裏で動くスクリプトと設定例をまとめています。
スキルの説明文はボットテンプレートに、実行されるものはすべてこのリポジトリにあります。

現在の内容：`bin/watchgate.py`、モデルを使わない watch ゲート。`interval` 秒ごと（既定 300）に
`~/.herdrbot/config.json` の各マシンで `herdr --machine <label> agent list` を実行し、前回のスナップショットと比較して、
**意味のある変化があったときだけ** Herdrbot の「Herdr signal」Webhook に POST します。
これにより、ボットは判断すべきことがあるときだけ起動します。

pane ごとの比較項目：新しい pane、閉じた pane、`agent_status` の変化、`completion_seq` の変化。
focus と revision は無視します。マシンの到達不能／復帰はそれぞれ一度だけ通知します。

## インストール

```sh
git clone https://github.com/devicki/herdrbot ~/.herdrbot/engine
cp ~/.herdrbot/engine/examples/gate.conf.example ~/.herdrbot/gate.conf
chmod 600 ~/.herdrbot/gate.conf      # その後 url と key を記入
# ~/.herdrbot/config.json: examples/config.example.json を参照（Herdrbot のセットアップスキルが作成）
setsid nohup python3 ~/.herdrbot/engine/bin/watchgate.py >/dev/null 2>&1 </dev/null &
```

ゲートが `~/.herdrbot` で使うファイル（リポジトリには含めない）：`config.json`、`gate.conf`、
`gate_snapshot.json`、`gate.log`、`gate.pid`。Webhook キーがログに書かれることはありません。

環境変数：`HERDRBOT_HOME`（既定 `~/.herdrbot`）、`HERDR_BIN`（既定 `~/.local/bin/herdr`）。

## 更新

```sh
git -C ~/.herdrbot/engine pull --ff-only
```

`bin/` 以下が変わった場合はゲートを再起動してください：`kill $(cat ~/.herdrbot/gate.pid)` のあと、上のコマンドで再度起動します。

## ペイロード

`POST <url>`、ヘッダー `Authorization: Bearer <key>` と `Content-Type: application/json`：

```json
{"type": "gate", "changes": [
  {"machine": "laptop", "pane": "p1", "change": "new", "status": "working", "seq": 0, "agent": "claude", "title": "..."},
  {"machine": "laptop", "pane": "p2", "change": "closed"},
  {"machine": "laptop", "pane": "p3", "change": "status", "from": "working", "status": "done", "seq": 4, "agent": "claude", "title": "..."},
  {"machine": "server", "change": "unreachable"},
  {"machine": "server", "change": "reachable"}
]}
```

POST に失敗した場合はスナップショットを進めないため、同じ変化が次のサイクルで再送されます。

## `~/.herdrbot/bin/watchgate.py` からの移行

1. 上記のとおりリポジトリをクローンします。
2. `kill $(cat ~/.herdrbot/gate.pid)`
3. `~/.herdrbot/engine/bin/watchgate.py` からゲートを起動します。
4. `rm ~/.herdrbot/bin/watchgate.py`

`config.json`、`gate.conf`、`gate_snapshot.json` はそのまま残るので、二重に通知されることはありません。

## テスト

```sh
python3 -m pytest -q tests
```

## ライセンス

MIT
