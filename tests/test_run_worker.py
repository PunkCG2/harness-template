import http.server
import importlib.util
import json
import os
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_worker", ROOT / "core" / ".harness" / "run_worker.py")
rw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rw)


def sh(cwd, *args):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=True)


def make_repo(tmp):
    root = Path(tmp)
    sh(root, "git", "init", "-q", "-b", "main")
    sh(root, "git", "config", "user.email", "t@t")
    sh(root, "git", "config", "user.name", "t")
    (root / "src").mkdir()
    (root / "src" / "a.js").write_text("a", encoding="utf-8")
    (root / "docs" / "tasks").mkdir(parents=True)
    sh(root, "git", "add", "-A")
    sh(root, "git", "commit", "-q", "-m", "init")
    return root


TASK = """---
id: 001
estado: pendiente        # pendiente
ejecuta: local
---
# Title

## Archivos en alcance
- src/a.js (modificar)
- `src/new.js` (crear)
- tests/

## No tocar
- data/raw/
"""


class TaskTests(unittest.TestCase):
    def test_parse_task_and_scope(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "001-x.md"
            p.write_text(TASK, encoding="utf-8")
            self.assertEqual(rw.parse_task(p)["front"]["estado"], "pendiente")
            self.assertEqual(rw.parse_scope(p), ["src/a.js", "src/new.js", "tests/"])
            fix = Path(d) / "001-x.fix-2.md"
            fix.write_text("# fix", encoding="utf-8")
            self.assertEqual(rw.parse_scope(fix), ["src/a.js", "src/new.js", "tests/"])
            self.assertEqual(rw.base_task_path(fix).name, "001-x.md")


class ScopeTests(unittest.TestCase):
    def test_removes_temp_flags_outside_and_allows_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "src" / "new.js").write_text("n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "t.js").write_text("t", encoding="utf-8")
            (root / "scripts-tmp").mkdir()
            (root / "scripts-tmp" / "x.mjs").write_text("x", encoding="utf-8")
            (root / "_tmp_debug.mjs").write_text("x", encoding="utf-8")
            (root / "other.txt").write_text("o", encoding="utf-8")
            r = rw.scope_check(root, ["src/a.js", "src/new.js", "tests/"], [], rw.DEFAULTS["scope"]["temp_patterns"])
            self.assertEqual(sorted(r["removed"]), ["_tmp_debug.mjs", "scripts-tmp/x.mjs"])
            self.assertEqual(r["outside"], ["other.txt"])
            self.assertFalse((root / "scripts-tmp").exists(), "empty temp folder is removed too")
            self.assertTrue((root / "tests" / "t.js").exists())

    def test_worker_state_folder_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / ".harness" / "state").mkdir(parents=True)
            (root / ".harness" / "state" / "live.json").write_text("{}", encoding="utf-8")
            self.assertEqual(rw.changed_files(root), [])
            r = rw.scope_check(root, ["src/a.js"], [], [])
            self.assertEqual(r["outside"], [])

    def test_protected_and_companions_and_unknown_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "data" / "raw").mkdir(parents=True)
            (root / "data" / "raw" / "r.txt").write_text("r", encoding="utf-8")
            (root / "package-lock.json").write_text("{}", encoding="utf-8")
            r = rw.scope_check(root, ["package.json"], ["data/raw/**"], [])
            self.assertEqual(r["protected"], ["data/raw/r.txt"])
            self.assertEqual(r["outside"], [])
            r2 = rw.scope_check(root, [], [], [])
            self.assertTrue(r2["unknown"])
            self.assertEqual(r2["outside"], [])

    def test_template_temp_patterns_with_trailing_slash(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "scratch").mkdir()
            (root / "scratch" / "a.js").write_text("x", encoding="utf-8")
            (root / "scripts-tmp").mkdir()
            (root / "scripts-tmp" / "b.mjs").write_text("x", encoding="utf-8")
            r = rw.scope_check(root, ["src/a.js"], [], ["_tmp*", "*.tmp", "scratch/", "scripts-tmp/", "__pycache__/"])
            self.assertEqual(sorted(r["removed"]), ["scratch/a.js", "scripts-tmp/b.mjs"])
            self.assertEqual(r["outside"], [])

    def test_new_meta_of_in_scope_files_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "Assets" / "Scripts" / "Player").mkdir(parents=True)
            (root / "Assets" / "Old.cs.meta").write_text("guid: 1", encoding="utf-8")
            sh(root, "git", "add", "-A")
            sh(root, "git", "commit", "-q", "-m", "meta")
            for rel in ("Assets/Scripts/Player/Move.cs", "Assets/Scripts/Player/Move.cs.meta", "Assets/Scripts/Player.meta",
                        "Assets/Other.cs.meta"):
                (root / rel).write_text("x", encoding="utf-8")
            (root / "Assets" / "Old.cs.meta").write_text("guid: 2", encoding="utf-8")
            r = rw.scope_check(root, ["Assets/Scripts/Player/Move.cs", "Assets/Old.cs"], ["**/*.meta"], [])
            self.assertEqual(sorted(r["protected"]), ["Assets/Old.cs.meta", "Assets/Other.cs.meta"])
            self.assertEqual(r["outside"], [])

    def test_glob_matching(self):
        self.assertTrue(rw.path_matches("data/raw/a/b.txt", "data/raw/**"))
        self.assertTrue(rw.path_matches("src/x.js", "src/*.js"))
        self.assertFalse(rw.path_matches("src/sub/x.js", "src/*.js"))
        self.assertTrue(rw.path_matches("tests/t.js", "tests/"))


class ProxyTests(unittest.TestCase):
    def test_normalize_moves_system_and_strips(self):
        payload = {"system": [{"type": "text", "text": "S"}],
                   "messages": [{"role": "user", "content": "hi"}, {"role": "system", "content": "extra"}],
                   "thinking": {"type": "adaptive"}, "output_config": {}, "context_management": {}, "max_tokens": 5}
        out = rw.normalize(json.loads(json.dumps(payload)), strip_thinking=True)
        self.assertEqual([m["role"] for m in out["messages"]], ["user"])
        self.assertEqual(out["system"][-1]["text"], "extra")
        self.assertNotIn("thinking", out)
        kept = rw.normalize(json.loads(json.dumps(payload)), strip_thinking=False)
        self.assertIn("thinking", kept)

    def test_proxy_forwards_normalised_body(self):
        seen = {}

        class Upstream(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                seen["body"] = json.loads(self.rfile.read(int(self.headers["content-length"])))
                out = b'{"ok": true}'
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        up = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        threading.Thread(target=up.serve_forever, daemon=True).start()
        proxy = rw.Proxy(f"http://127.0.0.1:{up.server_address[1]}")
        port = proxy.start()
        try:
            body = json.dumps({"messages": [{"role": "user", "content": "x"}, {"role": "system", "content": "late"}]}).encode()
            req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/messages", data=body, method="POST",
                                         headers={"content-type": "application/json"})
            resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
            self.assertTrue(resp["ok"])
            self.assertEqual([m["role"] for m in seen["body"]["messages"]], ["user"])
            self.assertEqual(seen["body"]["system"], "late")
        finally:
            proxy.stop()
            up.shutdown()
            up.server_close()


class ModelTests(unittest.TestCase):
    MODELS = [{"id": "a-model", "state": "not-loaded", "type": "llm", "quantization": "Q4"},
              {"id": "b-model", "state": "loaded", "type": "llm", "quantization": "Q8"},
              {"id": "b-model-2", "state": "not-loaded", "type": "llm", "quantization": "Q8"}]

    def test_resolve_model(self):
        self.assertEqual(rw.resolve_model(self.MODELS, "a-model")["id"], "a-model")
        self.assertEqual(rw.resolve_model(self.MODELS, "A-MOD")["id"], "a-model")
        self.assertEqual(rw.resolve_model(self.MODELS)["id"], "b-model", "the single loaded model is used")
        self.assertEqual(rw.resolve_model(self.MODELS, "b-model-")["id"], "b-model-2", "unique substring")
        with self.assertRaises(rw.NeedsModel):
            rw.resolve_model(self.MODELS, "model")  # ambiguous

    def test_needs_model_without_loaded_or_keyboard(self):
        none_loaded = [dict(m, state="not-loaded") for m in self.MODELS]
        with self.assertRaises(rw.NeedsModel) as ctx:
            rw.resolve_model(none_loaded, None, interactive=False)
        self.assertEqual(len(ctx.exception.models), 3)
        picked = rw.resolve_model(none_loaded, None, interactive=True, ask=lambda _p: "2")
        self.assertEqual(picked["id"], "b-model")
        with self.assertRaises(ValueError):
            rw.resolve_model(self.MODELS, "nope")

    def test_list_models_reads_api_v0(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                data = {"data": [{"id": "m1", "type": "llm", "state": "not-loaded", "quantization": "Q4"},
                                 {"id": "embed-x", "type": "embeddings"}, {"id": "v1", "type": "vlm", "state": "loaded"}]}
                out = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("content-length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            models = rw.list_models(f"http://127.0.0.1:{srv.server_address[1]}")
            self.assertEqual([m["id"] for m in models], ["m1", "v1"])
            self.assertEqual(models[0]["state"], "not-loaded")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_unreachable_server(self):
        with self.assertRaises(ConnectionError):
            rw.list_models("http://127.0.0.1:1")


class GateTests(unittest.TestCase):
    def test_gates_stop_at_first_failure(self):
        with tempfile.TemporaryDirectory() as d:
            res = rw.run_gates(['python -c "print(1)"', 'python -c "import sys; sys.exit(3)"', 'python -c "print(2)"'], d, 30)
            self.assertEqual([r["ok"] for r in res], [True, False])
            self.assertFalse(rw.gates_ok(res))

    def test_gate_timeout(self):
        with tempfile.TemporaryDirectory() as d:
            res = rw.run_command('python -c "import time; time.sleep(5)"', d, 1)
            self.assertTrue(res["timed_out"])
            self.assertFalse(res["ok"])


class TimingTests(unittest.TestCase):
    def test_p90_and_adaptive_timeout(self):
        self.assertEqual(rw.p90([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 9)
        with tempfile.TemporaryDirectory() as d:
            t = rw.Timings(Path(d) / "s" / "timings.json")
            self.assertEqual(t.timeout_s("gate", 300, 60, 1200, 3.0), 300)  # no samples: default
            for s in (10, 12, 11):
                t.record("gate", s)
            high = t.timeout_s("gate", 300, 60, 1200, 3.0)
            self.assertLessEqual(high, 300)
            self.assertGreaterEqual(high, 60)
            self.assertLess(high, 300, "falls slowly towards the sample-based value")
            for s in (200, 220, 210):
                t.record("gate", s)
            self.assertGreater(t.timeout_s("gate", 300, 60, 1200, 3.0), high, "rises quickly")
            before = t.data["limits"]["gate"]
            self.assertEqual(t.bump("gate", 300, 1200), min(1200, round(before * 1.5, 1)))
            t.save()
            self.assertTrue((Path(d) / "s" / "timings.json").exists())


class LadderTests(unittest.TestCase):
    def run_with(self, script, local_attempts=3):
        calls = []

        def attempt(tier, n, kind, details):
            calls.append((tier, n, kind))
            return {"output": "", "timed_out": False, "seconds": 1.0,
                    "flags": {"overflow": False, "max_turns": False, "api_error": False}}

        results = iter(script)

        def check(res):
            return next(results)

        tiers = {"local": {"attempts": local_attempts}, "claude-haiku": {"attempts": 2}, "claude-sonnet": {"attempts": 1}}
        out = rw.run_ladder(["local", "claude-haiku", "claude-sonnet", "main-claude"], tiers, attempt, check)
        return out, calls

    ok = {"ok": True, "kind": "ok", "details": ""}

    def fail(self, kind="gates"):
        return {"ok": False, "kind": kind, "details": "details"}

    def test_succeeds_on_first_local_attempt(self):
        out, calls = self.run_with([self.ok])
        self.assertEqual(out["status"], "ok")
        self.assertEqual(calls, [("local", 1, "first")])

    def test_local_gets_three_attempts_with_matching_retry_kinds(self):
        out, calls = self.run_with([self.fail("overflow"), self.fail("gates"), self.ok])
        self.assertEqual(out["tier"], "local")
        self.assertEqual(calls, [("local", 1, "first"), ("local", 2, "overflow"), ("local", 3, "gates")])

    def test_escalates_after_local_attempts(self):
        out, calls = self.run_with([self.fail()] * 3 + [self.ok])
        self.assertEqual(out["tier"], "claude-haiku")
        self.assertEqual([c[0] for c in calls], ["local", "local", "local", "claude-haiku"])

    def test_exhausted_stops_at_main_claude(self):
        out, calls = self.run_with([self.fail()] * 6)
        self.assertEqual(out["status"], "exhausted")
        self.assertEqual(len(calls), 3 + 2 + 1)
        self.assertIsNotNone(out["last"])


class PromptTests(unittest.TestCase):
    def test_retry_prompts(self):
        self.assertEqual(rw.retry_prompt("T", "first", ""), "T")
        self.assertIn("ONE file per tool call", rw.retry_prompt("T", "overflow", ""))
        self.assertIn("continue from them", rw.retry_prompt("T", "timeout", ""))
        self.assertIn("npm test", rw.retry_prompt("T", "gates", "The check `npm test` failed"))

    def test_classify_output(self):
        f = rw.classify_output("API Error: Claude's response exceeded the 16000 output token maximum.")
        self.assertTrue(f["overflow"])
        self.assertTrue(f["api_error"])
        self.assertTrue(rw.classify_output("Error: Reached max turns (40)")["max_turns"])

    def test_worker_command_and_allowed_bash(self):
        cfg = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": ["npm test"], "full": ["npm test", "npm run build", "cargo test"]}})
        self.assertEqual(rw.allowed_bash_from_gates(cfg), ["npm", "cargo"])
        cmd = rw.build_worker_cmd("claude", "m", "ROLE", ["npm"], 40)
        self.assertIn("Read,Edit,Write,Glob,Grep,Bash(npm *)", cmd)
        self.assertEqual(cmd[cmd.index("--system-prompt") + 1], "ROLE")
        self.assertIn("Bash(git *)", cmd[cmd.index("--disallowedTools") + 1])


class CheckerTests(unittest.TestCase):
    def test_checker_failure_kinds_and_success(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            cfg = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": ['python -c "print(1)"']}})
            check = rw.make_checker(root, cfg, ["src/a.js"], 30)
            res = {"flags": {"overflow": False}, "timed_out": False}
            self.assertEqual(check(dict(res))["kind"], "no_output")
            self.assertEqual(check({"flags": {"overflow": True}, "timed_out": False})["kind"], "overflow")
            (root / "src" / "a.js").write_text("changed", encoding="utf-8")
            self.assertTrue(check(dict(res))["ok"])
            (root / "stray.txt").write_text("x", encoding="utf-8")
            r = check(dict(res))
            self.assertFalse(r["ok"])
            self.assertIn("stray.txt", r["details"])
            (root / "stray.txt").unlink()
            bad = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": ['python -c "import sys; sys.exit(1)"']}})
            r2 = rw.make_checker(root, bad, ["src/a.js"], 30)(dict(res))
            self.assertFalse(r2["ok"])
            self.assertIn("failed", r2["details"])

    def test_full_gates_run_after_fast_ones_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "src" / "a.js").write_text("changed", encoding="utf-8")
            res = {"flags": {"overflow": False}, "timed_out": False}
            ok = 'python -c "print(1)"'
            cfg = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": [ok], "full": [ok, 'python -c "print(2)"']}})
            r = dict(res)
            self.assertTrue(rw.make_checker(root, cfg, ["src/a.js"], 30)(r)["ok"])
            self.assertEqual([g["cmd"] for g in r["gates"]], [ok, 'python -c "print(2)"'], "a fast command is not run twice")
            bad = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": [ok], "full": ['python -c "import sys; sys.exit(3)"']}})
            chk = rw.make_checker(root, bad, ["src/a.js"], 30)(dict(res))
            self.assertFalse(chk["ok"])
            self.assertEqual(chk["kind"], "gates")
            failing_fast = rw.deep_merge(rw.DEFAULTS, {"gates": {"fast": ['python -c "import sys; sys.exit(1)"'],
                                                                 "full": ['python -c "print(2)"']}})
            r3 = dict(res)
            rw.make_checker(root, failing_fast, ["src/a.js"], 30)(r3)
            self.assertEqual(len(r3["gates"]), 1, "the full gate does not run when the fast one fails")


class BaseBranchTests(unittest.TestCase):
    def test_main_or_master_or_configured(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            self.assertEqual(rw.resolve_base_branch(root), "main")
            sh(root, "git", "branch", "-m", "main", "master")
            self.assertEqual(rw.resolve_base_branch(root), "master")
            self.assertIsNone(rw.resolve_base_branch(root, "develop"))
            sh(root, "git", "branch", "develop")
            self.assertEqual(rw.resolve_base_branch(root, "develop"), "develop")

    def test_ensure_branch_from_master(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            sh(root, "git", "branch", "-m", "main", "master")
            rw.ensure_branch(root, "task/001-x", rw.resolve_base_branch(root))
            self.assertEqual(rw.current_branch(root), "task/001-x")


class ConfigTests(unittest.TestCase):
    def test_deep_merge_and_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = rw.load_config(d)
            self.assertEqual(cfg["workers"]["local"]["attempts"], 3)
            (Path(d) / ".harness").mkdir()
            (Path(d) / ".harness" / "harness.toml").write_text('[workers.local]\nattempts = 5\n[gates]\nfast = ["x"]\n', encoding="utf-8")
            cfg = rw.load_config(d)
            self.assertEqual(cfg["workers"]["local"]["attempts"], 5)
            self.assertEqual(cfg["workers"]["local"]["url"], "http://127.0.0.1:1234")
            self.assertEqual(cfg["gates"]["fast"], ["x"])


class StripPolicyTests(unittest.TestCase):
    def test_first_attempts_strip_thinking(self):
        cfg = {"strip_thinking_attempts": 2}
        self.assertEqual([rw.use_strip(cfg, n) for n in (1, 2, 3)], [True, True, False])

    def test_flag_forces_every_attempt(self):
        cfg = {"strip_thinking": True, "strip_thinking_attempts": 0}
        self.assertEqual([rw.use_strip(cfg, n) for n in (1, 2, 3)], [True, True, True])

    def test_zero_attempts_means_never(self):
        self.assertFalse(rw.use_strip({"strip_thinking_attempts": 0}, 1))
        self.assertFalse(rw.use_strip({}, 1))

    def test_default_config_strips_two_of_three(self):
        local = rw.DEFAULTS["workers"]["local"]
        self.assertEqual([rw.use_strip(local, n) for n in (1, 2, 3)], [True, True, False])

    def test_proxy_follows_the_flag_per_request(self):
        seen = []

        class Upstream(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                seen.append(json.loads(self.rfile.read(int(self.headers["content-length"]))))
                out = b"{}"
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        up = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        threading.Thread(target=up.serve_forever, daemon=True).start()
        proxy = rw.Proxy(f"http://127.0.0.1:{up.server_address[1]}")
        port = proxy.start()
        try:
            for flag in (True, False):
                proxy.strip = flag
                body = json.dumps({"messages": [], "thinking": {"type": "adaptive"}, "output_config": {}}).encode()
                req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/messages", data=body, method="POST",
                                             headers={"content-type": "application/json"})
                urllib.request.urlopen(req, timeout=10).read()
            self.assertNotIn("thinking", seen[0])
            self.assertIn("thinking", seen[1])
        finally:
            proxy.stop()
            up.shutdown()
            up.server_close()


class FakeModelServer:
    """Model server with /api/v1/models (instances), /api/v0/models (state) and /api/v1/models/load."""

    def __init__(self, instances=0, v1=True, load_status=200, loads_anyway=False, delay=0.0, load_404=False):
        self.instances, self.v1, self.load_status = instances, v1, load_status
        self.loads_anyway, self.delay, self.load_404 = loads_anyway, delay, load_404
        self.load_calls = 0
        self.lock = threading.Lock()
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def _send(self, code, obj):
                out = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def do_GET(self):
                if self.path == "/api/v1/models":
                    if not outer.v1:
                        return self._send(404, {})
                    inst = [{"id": "m1" if i == 0 else f"m1:{i + 1}"} for i in range(outer.instances)]
                    return self._send(200, {"models": [{"key": "m1", "loaded_instances": inst}]})
                if self.path == "/api/v0/models":
                    state = "loaded" if outer.instances else "not-loaded"
                    return self._send(200, {"data": [{"id": "m1", "type": "llm", "state": state, "quantization": "Q4"}]})
                self._send(404, {})

            def do_POST(self):
                self.rfile.read(int(self.headers.get("content-length", 0)))
                if outer.load_404:
                    return self._send(404, {})
                with outer.lock:
                    outer.load_calls += 1
                time.sleep(outer.delay)
                if outer.load_status != 200:
                    if outer.loads_anyway:
                        with outer.lock:
                            outer.instances += 1
                    return self._send(outer.load_status, {"error": "boom"})
                with outer.lock:
                    outer.instances += 1
                self._send(200, {"status": "loaded"})

            def log_message(self, *a):
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


MODEL = {"id": "m1", "state": "not-loaded", "quantization": "Q4"}


class LoaderTests(unittest.TestCase):
    def test_already_loaded_sends_no_order(self):
        srv = FakeModelServer(instances=1)
        try:
            self.assertEqual(rw.ensure_loaded(srv.base, MODEL), "already loaded")
            self.assertEqual(srv.load_calls, 0)
        finally:
            srv.close()

    def test_not_loaded_sends_exactly_one_order(self):
        srv = FakeModelServer()
        try:
            self.assertEqual(rw.ensure_loaded(srv.base, MODEL), "loaded by the API")
            self.assertEqual((srv.load_calls, srv.instances), (1, 1))
            rw.ensure_loaded(srv.base, MODEL)  # asking again must not load a second instance
            self.assertEqual((srv.load_calls, srv.instances), (1, 1))
        finally:
            srv.close()

    def test_error_reply_but_model_loads_anyway(self):
        srv = FakeModelServer(load_status=500, loads_anyway=True)
        try:
            msg = rw.ensure_loaded(srv.base, MODEL, sleep=lambda s: None)
            self.assertIn("loaded", msg)
            self.assertEqual(srv.load_calls, 1, "the order is never repeated after an error")
        finally:
            srv.close()

    def test_error_reply_and_nothing_loads(self):
        srv = FakeModelServer(load_status=500)
        try:
            with self.assertRaises(urllib.error.HTTPError):
                rw.ensure_loaded(srv.base, MODEL, settle_s=4, sleep=lambda s: None)
            self.assertEqual(srv.load_calls, 1)
        finally:
            srv.close()

    def test_two_processes_at_once_load_one_instance(self):
        srv = FakeModelServer(delay=0.4)
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "load.lock"
            results = []
            threads = [threading.Thread(target=lambda: results.append(rw.ensure_loaded(srv.base, MODEL, lock_path=lock)))
                       for _ in range(3)]
            try:
                for t in threads:
                    t.start()
                for t in threads:
                    t.join(timeout=30)
                self.assertEqual((srv.load_calls, srv.instances), (1, 1))
                self.assertEqual(sorted(results), ["already loaded", "already loaded", "loaded by the API"])
                self.assertFalse(lock.exists(), "the lock is released")
            finally:
                srv.close()

    def test_falls_back_to_v0_state_without_instances_endpoint(self):
        srv = FakeModelServer(instances=1, v1=False)
        try:
            self.assertEqual(rw.ensure_loaded(srv.base, MODEL), "already loaded")
            self.assertEqual(srv.load_calls, 0)
        finally:
            srv.close()

    def test_server_without_load_endpoint(self):
        srv = FakeModelServer(load_404=True)
        try:
            self.assertIn("no load endpoint", rw.ensure_loaded(srv.base, MODEL))
        finally:
            srv.close()

    def test_extra_instances_are_reported(self):
        srv = FakeModelServer(instances=2)
        try:
            self.assertIn("WARNING: 2 instances", rw.ensure_loaded(srv.base, MODEL))
            self.assertEqual(srv.load_calls, 0)
        finally:
            srv.close()


def _m(name, state="not-loaded"):
    return {"id": name, "state": state, "type": "llm", "quantization": "Q4"}


class PlanModelsTests(unittest.TestCase):
    def test_nothing_loaded_tries_preferred_then_fallback(self):
        models = [_m("a-big"), _m("b-small"), _m("c-other")]
        got, note = rw.plan_models(models, preferred="a-big", fallback="b-small")
        self.assertEqual([m["id"] for m in got], ["a-big", "b-small"])
        self.assertEqual(note, "")

    def test_loaded_preferred_is_used_as_is(self):
        models = [_m("a-big", "loaded"), _m("b-small")]
        self.assertEqual([m["id"] for m in rw.plan_models(models, preferred="a-big", fallback="b-small")[0]], ["a-big"])

    def test_loaded_fallback_is_used_without_loading_the_preferred(self):
        models = [_m("a-big"), _m("b-small", "loaded")]
        self.assertEqual([m["id"] for m in rw.plan_models(models, preferred="a-big", fallback="b-small")[0]], ["b-small"])

    def test_other_loaded_model_is_used_with_a_note(self):
        models = [_m("a-big"), _m("b-small"), _m("c-other", "loaded")]
        got, note = rw.plan_models(models, preferred="a-big", fallback="b-small")
        self.assertEqual([m["id"] for m in got], ["c-other"])
        self.assertIn("already loaded c-other", note)

    def test_explicit_model_wins(self):
        models = [_m("a-big", "loaded"), _m("b-small")]
        self.assertEqual(rw.plan_models(models, wanted="b-small", preferred="a-big")[0][0]["id"], "b-small")

    def test_missing_fallback_is_skipped_missing_preferred_is_an_error(self):
        models = [_m("a-big")]
        self.assertEqual([m["id"] for m in rw.plan_models(models, preferred="a-big", fallback="gone")[0]], ["a-big"])
        with self.assertRaises(ValueError):
            rw.plan_models(models, preferred="gone")

    def test_nothing_configured_keeps_the_old_behaviour(self):
        self.assertEqual(rw.plan_models([_m("a", "loaded"), _m("b")])[0][0]["id"], "a")
        with self.assertRaises(rw.NeedsModel):
            rw.plan_models([_m("a"), _m("b")])


class LockTests(unittest.TestCase):
    def test_run_lock_blocks_a_live_run_and_replaces_a_dead_one(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "worker.lock"
            other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            try:
                path.write_text(str(other.pid), encoding="utf-8")
                self.assertEqual(rw.RunLock(path).acquire(), other.pid)
            finally:
                other.kill()
                other.wait()
            self.assertIsNone(rw.RunLock(path).acquire(), "the process is gone: the lock is taken over")
            self.assertEqual(path.read_text(encoding="utf-8"), str(os.getpid()))
            rw.RunLock(path).release()
            self.assertFalse(path.exists())

    def test_main_refuses_a_second_run_in_the_same_project(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "docs" / "tasks" / "001-x.md").write_text(TASK, encoding="utf-8")
            state = root / ".harness" / "state"
            state.mkdir(parents=True)
            other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            try:
                (state / "worker.lock").write_text(str(other.pid), encoding="utf-8")
                self.assertEqual(rw.main(["docs/tasks/001-x.md", "--root", str(root)]), rw.EXIT_BUSY)
            finally:
                other.kill()
                other.wait()

    def test_file_lock_takes_over_a_stale_lock(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.lock"
            path.write_text("1", encoding="utf-8")
            old = time.time() - 3600
            os.utime(path, (old, old))
            with rw.FileLock(path, timeout=2, stale=60):
                self.assertTrue(path.exists())
            self.assertFalse(path.exists())


class GuardrailTests(unittest.TestCase):
    def write(self, root, text):
        (Path(root) / "docs").mkdir(exist_ok=True)
        (Path(root) / "docs" / "guardrails.md").write_text(text, encoding="utf-8")

    def test_missing_file_or_section_gives_no_signs(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(rw.read_signs(d), [])
            self.write(d, "# G\n\n## Enforced\n- gates\n")
            self.assertEqual(rw.read_signs(d), [])

    def test_template_without_signs_is_empty(self):
        text = (ROOT / "core" / "docs" / "guardrails.md.tmpl").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            self.write(d, text.replace("{{project_name}}", "p"))
            self.assertEqual(rw.read_signs(d), [])

    def test_reads_only_bullets_of_the_signs_section(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "## Enforced\n- not a sign\n\n## Signs\n<!-- - hidden -->\n"
                          "- When A: do B. Evidence: t1\nplain text\n* When C: do D. Evidence: t2\n\n## Later\n- other\n")
            self.assertEqual(rw.read_signs(d), ["- When A: do B. Evidence: t1", "* When C: do D. Evidence: t2"])

    def test_role_with_signs(self):
        self.assertEqual(rw.role_with_signs("ROLE", []), "ROLE")
        out = rw.role_with_signs("ROLE", ["- When A: B."])
        self.assertTrue(out.startswith("ROLE\n\n## Project guardrails"))
        self.assertTrue(out.endswith("- When A: B."))


class MainTests(unittest.TestCase):
    def test_dry_run_and_missing_task(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "docs" / "tasks" / "001-x.md").write_text(TASK, encoding="utf-8")
            self.assertEqual(rw.main(["docs/tasks/001-x.md", "--root", str(root), "--dry-run"]), rw.EXIT_OK)
            self.assertEqual(rw.main(["docs/tasks/nope.md", "--root", str(root)]), rw.EXIT_CONFIG)
            self.assertEqual(rw.main(["docs/tasks/001-x.md", "--root", str(root), "--start", "bogus", "--dry-run"]), rw.EXIT_CONFIG)

    def test_ensure_branch_requires_clean_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            rw.ensure_branch(root, "task/001-x", "main")
            self.assertEqual(rw.current_branch(root), "task/001-x")
            sh(root, "git", "switch", "-q", "main")
            (root / "dirty.txt").write_text("d", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                rw.ensure_branch(root, "task/002-y", "main")


if __name__ == "__main__":
    unittest.main()
