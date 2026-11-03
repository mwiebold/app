"""Check source syntax and the running local API (Python 3, Node, Docker)."""

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent


def run(*command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def request(path, payload=None):
    command = [
        "docker", "compose", "exec", "-T", "web", "curl",
        "--silent", "--show-error", "--max-time", "10",
        "--write-out", "\n%{http_code}",
    ]
    if payload is not None:
        command.extend(["--header", "Content-Type: application/json", "--data", json.dumps(payload)])
    body, status = run(*command, "http://localhost" + path).rsplit("\n", 1)
    return body, int(status)


def main():
    files = run("git", "ls-files", "-z").split("\0")
    javascript = [p for p in files if p.endswith(".js") and not p.startswith("js/lib/")]
    for path in javascript:
        run("node", "--check", path)
    print(f"JavaScript syntax: {len(javascript)} files passed (vendor libraries excluded)")

    php = [p for p in files if p.endswith(".php")] + ["api/cora/setting.php"]
    run("docker", "compose", "exec", "-T", "web", "php", "-l", *php)
    print(f"PHP syntax: {len(php)} files passed")

    payload = {
        "resource": "announcement", "method": "read_id",
        "api_key": "0000000000000000000000000000000000000001",
    }
    body, status = request("/api/", payload)
    assert status == 200 and json.loads(body)["success"] is True, body
    payload["resource"] = "user"
    body, status = request("/api/", payload)
    response = json.loads(body)
    assert response["success"] is False and response["data"]["error_code"] == 1505, body
    print("API: database-backed read passed; private read requires a session")

    for path in ["/.git/config", "/api/beestat.sql", "/compose.yaml", "/dev/setup.py"]:
        _, status = request(path)
        assert status == 403, f"{path}: expected 403, got {status}"
    body, status = request("/js/beestat.js")
    assert status == 200 and "var beestat" in body
    print("HTTP: development files blocked; application JavaScript served")


if __name__ == "__main__":
    main()
