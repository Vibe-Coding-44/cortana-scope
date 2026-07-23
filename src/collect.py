"""cortana-scope データ収集 → data/snapshot.json 生成"""
import json
import subprocess
import datetime
from pathlib import Path

CORTANA_STATE = Path(__file__).parent.parent.parent / "cortana-db-v2" / "data" / "cortana_state.json"
VIBE_ROOT = Path(__file__).parent.parent.parent
OUT = Path(__file__).parent.parent / "data" / "snapshot.json"

PROJECTS_DIR = [
    "3Dviewer", "cortana-intro", "iptv-library", "voice-studio",
    "ai-explorer", "music-assistant", "design-md-spec",
    "cortana-design-system", "mjml-studio", "mjml-studio-v2",
    "last30days-studio", "voice-deck", "agent-lens",
    "html-video-studio", "memory-canvas", "cortana-scope",
]


def load_state():
    with open(CORTANA_STATE) as f:
        return json.load(f)


def collect_token_timeline(state):
    daily = state.get("token_history", {}).get("daily", [])
    return [
        {
            "date": d["date"],
            "commands": d.get("commands", 0),
            "input_tokens": d.get("input_tokens", 0),
            "saved_tokens": d.get("saved_tokens", 0),
            "savings_pct": round(d.get("savings_pct", 0), 1),
            "total_time_ms": d.get("total_time_ms", 0),
        }
        for d in daily
    ]


def collect_projects(state):
    projects = state.get("projects", {}).get("main", [])
    return [
        {
            "name": p.get("name", ""),
            "stage": p.get("stage", ""),
            "last_active": p.get("last_active", ""),
            "description": p.get("description", ""),
        }
        for p in projects
    ]


def collect_commit_activity():
    result = []
    since = "2026-06-01"
    for pj in PROJECTS_DIR:
        pj_path = VIBE_ROOT / pj
        if not (pj_path / ".git").exists():
            continue
        try:
            out = subprocess.check_output(
                ["git", "log", "--oneline", f"--since={since}", "--format=%ad", "--date=short"],
                cwd=pj_path, stderr=subprocess.DEVNULL, text=True
            )
            dates = [l.strip() for l in out.strip().splitlines() if l.strip()]
            by_date = {}
            for d in dates:
                by_date[d] = by_date.get(d, 0) + 1
            result.append({"project": pj, "commits_by_date": by_date, "total": len(dates)})
        except Exception:
            pass
    return result


def main():
    print("📦 cortana_state.json 読み込み中...")
    state = load_state()

    print("📈 トークンタイムライン収集...")
    token_timeline = collect_token_timeline(state)

    print("📋 プロジェクト一覧収集...")
    projects = collect_projects(state)

    print("🔨 コミット履歴収集...")
    commit_activity = collect_commit_activity()

    totals = state.get("tokens", {})

    snapshot = {
        "generated_at": datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        ).isoformat(),
        "totals": {
            "total_commands": totals.get("total_commands", 0),
            "total_saved": totals.get("total_saved", 0),
            "avg_savings_pct": round(totals.get("avg_savings_pct", 0), 1),
            "total_time_ms": totals.get("total_time_ms", 0),
        },
        "token_timeline": token_timeline,
        "projects": projects,
        "commit_activity": commit_activity,
    }

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"✅ {OUT} 生成完了")
    print(f"   トークン履歴: {len(token_timeline)}日分")
    print(f"   プロジェクト: {len(projects)}件")
    print(f"   コミット追跡PJ: {len(commit_activity)}件")


if __name__ == "__main__":
    main()
