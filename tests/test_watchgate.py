import json, os, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import pytest

GATE = Path(__file__).resolve().parent.parent / "bin" / "watchgate.py"
KEY = "sekrit-test-key-123"


@pytest.fixture
def env(tmp_path):
    posts = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers["Content-Length"])
            posts.append({"auth": self.headers.get("Authorization"),
                          "body": json.loads(self.rfile.read(n))})
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    home = tmp_path / "home"; home.mkdir()
    (home / "config.json").write_text(json.dumps({"machines": [{"label": "m1"}]}))
    (home / "gate.conf").write_text(f"url = http://127.0.0.1:{srv.server_port}/\nkey = {KEY}\ninterval = 1\n")
    state = tmp_path / "agents.json"
    fake = tmp_path / "herdr"
    fake.write_text(f"#!{sys.executable}\nimport sys\np='{state}'\n"
                    "d=open(p).read()\n"
                    "if d=='DOWN': sys.exit(1)\n"
                    "print(d)\n")
    fake.chmod(0o755)

    def set_agents(agents):
        state.write_text("DOWN" if agents is None else json.dumps({"result": {"agents": agents}}))

    def run():
        e = dict(os.environ, HERDRBOT_HOME=str(home), HERDR_BIN=str(fake))
        subprocess.run([sys.executable, str(GATE), "--once"], env=e, check=True, timeout=30)
        out = list(posts); posts.clear(); return out

    yield set_agents, run, home
    srv.shutdown()


def A(pane, status="working", seq=0, focus=False, rev=1):
    return {"pane_id": pane, "agent_status": status, "completion_seq": seq, "agent": "claude",
            "terminal_title_stripped": "t", "focused": focus, "revision": rev}


def changes(posts):
    return sorted((c["change"], c.get("pane")) for p in posts for c in p["body"]["changes"])


def test_diff_logic(env):
    set_agents, run, home = env
    set_agents([A("p1"), A("p2")])
    assert run() == []  # first snapshot: baseline only
    set_agents([A("p1", focus=True, rev=9), A("p2")])
    assert run() == []  # focus/revision ignored
    set_agents([A("p1", status="done"), A("p3")])
    assert changes(run()) == [("closed", "p2"), ("new", "p3"), ("status", "p1")]
    set_agents([A("p1", status="done", seq=1), A("p3")])
    assert changes(run()) == [("status", "p1")]


def test_unreachable_once_then_reachable(env):
    set_agents, run, home = env
    set_agents([A("p1")]); run()
    set_agents(None)
    p = run()
    assert changes(p) == [("unreachable", None)]
    assert p[0]["auth"] == f"Bearer {KEY}"
    assert p[0]["body"]["type"] == "gate"
    assert run() == []  # no repeat
    set_agents([A("p1")])
    assert changes(run()) == [("reachable", None)]
    assert run() == []
    assert KEY not in (home / "gate.log").read_text()
