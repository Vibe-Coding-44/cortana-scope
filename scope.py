"""cortana-scope — データ収集・HTML生成エントリーポイント (V0 スタブ)"""
import sys


def build():
    print("📊 cortana-scope build — V1実装待ち")
    print("  予定: cortana_state.json + Slack API → data/snapshot.json → docs/index.html")


def preview():
    import http.server, webbrowser, os
    from functools import partial
    from pathlib import Path

    docs = Path(__file__).parent / "docs"
    if not (docs / "index.html").exists():
        print("❌ docs/index.html が存在しません。先に build を実行してください。")
        sys.exit(1)

    os.chdir(docs)
    Handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(docs))
    with http.server.HTTPServer(("", 8766), Handler) as httpd:
        url = "http://localhost:8766/"
        print(f"🌐 {url}")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n停止しました。")


def push():
    import subprocess
    result = subprocess.run(
        ["git", "add", "docs/", "data/"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ git add 失敗: {result.stderr}")
        sys.exit(1)
    subprocess.run(["git", "commit", "-m", "chore: scope snapshot 更新"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ push 完了 — Vercel デプロイ開始")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    {"build": build, "preview": preview, "push": push}.get(cmd, build)()
