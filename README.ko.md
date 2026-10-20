# herdrbot

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [繁體中文](README.zh-TW.md)

[![Herdrbot 소개 영상 (클릭하면 mp4)](docs/media/herdrbot-intro.gif)](docs/media/herdrbot-intro.mp4)

**Herdrbot** Grok Bot의 엔진입니다. Herdrbot 스킬 뒤에서 동작하는 스크립트와 설정 예시를 담고 있어요.
스킬 설명은 봇 템플릿에, 실행되는 것은 모두 이 레포에 있습니다.

현재 포함: `bin/watchgate.py`, 모델을 쓰지 않는 watch 게이트. `interval`초마다(기본 300) `~/.herdrbot/config.json`의
각 머신에 대해 `herdr --machine <label> agent list`를 실행하고, 지난 스냅샷과 비교해서 **의미 있는 변화가 있을 때만**
Herdrbot의 "Herdr signal" 웹훅으로 POST합니다. 그래서 봇은 판단할 일이 있을 때만 깨어나요.

pane별 비교 항목: 새 pane, 닫힌 pane, `agent_status` 변경, `completion_seq` 변경. focus와 revision은 무시합니다.
머신 연결 끊김/복구는 각각 한 번씩만 알립니다.

## 설치

```sh
git clone https://github.com/devicki/herdrbot ~/.herdrbot/engine
cp ~/.herdrbot/engine/examples/gate.conf.example ~/.herdrbot/gate.conf
chmod 600 ~/.herdrbot/gate.conf      # 그다음 url과 key를 채우세요
# ~/.herdrbot/config.json: examples/config.example.json 참고 (Herdrbot 설정 스킬이 작성)
setsid nohup python3 ~/.herdrbot/engine/bin/watchgate.py >/dev/null 2>&1 </dev/null &
```

게이트가 `~/.herdrbot`에서 쓰는 파일(레포에는 절대 없음): `config.json`, `gate.conf`, `gate_snapshot.json`,
`gate.log`, `gate.pid`. 웹훅 키는 로그에 절대 기록되지 않습니다.

환경 변수: `HERDRBOT_HOME`(기본 `~/.herdrbot`), `HERDR_BIN`(기본 `~/.local/bin/herdr`).

## 업데이트

```sh
git -C ~/.herdrbot/engine pull --ff-only
```

`bin/` 아래가 바뀌었다면 게이트를 재시작하세요: `kill $(cat ~/.herdrbot/gate.pid)` 후 위 명령으로 다시 실행.

## 페이로드

`POST <url>`, 헤더 `Authorization: Bearer <key>`, `Content-Type: application/json`:

```json
{"type": "gate", "changes": [
  {"machine": "laptop", "pane": "p1", "change": "new", "status": "working", "seq": 0, "agent": "claude", "title": "..."},
  {"machine": "laptop", "pane": "p2", "change": "closed"},
  {"machine": "laptop", "pane": "p3", "change": "status", "from": "working", "status": "done", "seq": 4, "agent": "claude", "title": "..."},
  {"machine": "server", "change": "unreachable"},
  {"machine": "server", "change": "reachable"}
]}
```

POST가 실패하면 스냅샷을 갱신하지 않으므로 같은 변경이 다음 주기에 다시 전송됩니다.

## `~/.herdrbot/bin/watchgate.py`에서 옮기기

1. 위처럼 레포를 클론합니다.
2. `kill $(cat ~/.herdrbot/gate.pid)`
3. `~/.herdrbot/engine/bin/watchgate.py`로 게이트를 실행합니다.
4. `rm ~/.herdrbot/bin/watchgate.py`

`config.json`, `gate.conf`, `gate_snapshot.json`은 그대로 두므로 중복 알림이 없습니다.

## 테스트

```sh
python3 -m pytest -q tests
```

## 라이선스

MIT
