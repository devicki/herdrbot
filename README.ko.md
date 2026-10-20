# herdrbot

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [繁體中文](README.zh-TW.md)

https://github.com/user-attachments/assets/28e01ed1-a5e3-4248-8aca-34084274f2cc

## Herdrbot이란?

Herdrbot은 내 머신의 [Herdr](https://herdr.dev)에서 돌아가는 AI 코딩 에이전트(Claude Code, Codex 등)의 작업반장 역할을 하는 Grok Bot입니다.

- 무엇을 어디서 만들거나 고칠지 말하면, 에이전트(`hb-...` 이름)를 띄워 작업을 맡기고, 지켜보다가 결과를 가져옵니다.
- 막힌 승인 질문은 나에게 전달하고(권한 대화상자에 스스로 답하지 않음), 끝난 작업을 보고합니다.
- 선택적으로 에이전트가 제안한 안전한 다음 단계(테스트, 문서, 커밋; push/tag는 켰을 때만)를 이어서 진행합니다. 기본값은 꺼짐.
- 머지, 배포, 강제 푸시, 삭제는 항상 내 승인이 필요합니다. 내가 직접 띄운 에이전트는 내 것으로 남습니다.
- 아침 요약을 보내고, 매주 Herdr 업데이트를 확인합니다.
- [away-signal 플러그인](https://github.com/devicki/herdr-away-signal)과 이 레포의 watch 게이트 덕분에 모델 실행 비용은 낮게 유지하면서 즉시 반응합니다.

이 레포는 그 엔진, 즉 봇의 스킬이 쓰는 스크립트입니다.

## 엔진

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
