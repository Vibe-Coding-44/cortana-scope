"""cortana-scope HTML ダッシュボード生成"""
import json
from pathlib import Path

SNAPSHOT = Path(__file__).parent.parent / "data" / "snapshot.json"
OUT = Path(__file__).parent.parent / "docs" / "index.html"

STAGE_COLOR = {
    "💡 アイデア": "#facc15",
    "🔨 作成中": "#60a5fa",
    "✅ 完了": "#4ade80",
}

STAGE_BG = {
    "💡 アイデア": "rgba(250,204,21,0.15)",
    "🔨 作成中": "rgba(96,165,250,0.15)",
    "✅ 完了": "rgba(74,222,128,0.15)",
}


def build():
    with open(SNAPSHOT) as f:
        snap = json.load(f)

    tl = snap["token_timeline"]
    projects = snap["projects"]
    totals = snap["totals"]
    generated = snap["generated_at"][:16].replace("T", " ")

    # ---- サマリカード ----
    stage_counts = {}
    for p in projects:
        s = p["stage"]
        stage_counts[s] = stage_counts.get(s, 0) + 1

    # ---- トークンタイムライン ----
    dates = [d["date"] for d in tl]
    saved = [d["saved_tokens"] for d in tl]
    input_tok = [d["input_tokens"] for d in tl]
    savings_pct = [d["savings_pct"] for d in tl]
    commands = [d["commands"] for d in tl]

    # ---- プロジェクトガント ----
    sorted_pj = sorted(projects, key=lambda p: p.get("last_active", ""), reverse=True)
    pj_labels = json.dumps([p["name"] for p in sorted_pj], ensure_ascii=False)
    pj_dates = json.dumps([p.get("last_active", "") for p in sorted_pj])
    pj_colors = json.dumps([STAGE_COLOR.get(p["stage"], "#9ca3af") for p in sorted_pj])
    pj_bgs = json.dumps([STAGE_BG.get(p["stage"], "rgba(156,163,175,0.15)") for p in sorted_pj])
    pj_stages = json.dumps([p["stage"] for p in sorted_pj], ensure_ascii=False)

    total_saved_m = round(totals["total_saved"] / 1_000_000, 1)
    avg_pct = totals["avg_savings_pct"]
    total_cmd = f"{totals['total_commands']:,}"
    pj_count = len(projects)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>cortana-scope</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8;
    --accent: #a78bfa; --green: #4ade80; --blue: #60a5fa; --yellow: #facc15;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; color: var(--accent); margin-bottom: .25rem; }}
  .updated {{ color: var(--muted); font-size: .85rem; margin-bottom: 2rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 2.5rem; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }}
  .card .label {{ font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}
  .card .value {{ font-size: 2rem; font-weight: 700; margin-top: .25rem; }}
  .card .sub {{ font-size: .8rem; color: var(--muted); margin-top: .2rem; }}
  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  .chart-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }}
  .chart-box h2 {{ font-size: 1rem; color: var(--accent); margin-bottom: 1rem; }}
  .chart-box.full {{ grid-column: 1 / -1; }}
  canvas {{ max-height: 280px; }}
  @media (max-width: 700px) {{ .charts {{ grid-template-columns: 1fr; }} .chart-box.full {{ grid-column: 1; }} }}
</style>
</head>
<body>
<h1>cortana-scope</h1>
<p class="updated">最終更新: {generated} JST</p>

<div class="cards">
  <div class="card">
    <div class="label">トークン節約</div>
    <div class="value" style="color:var(--green)">{total_saved_m}M</div>
    <div class="sub">累計節約トークン数</div>
  </div>
  <div class="card">
    <div class="label">平均節約率</div>
    <div class="value" style="color:var(--accent)">{avg_pct}%</div>
    <div class="sub">RTK フィルタリング</div>
  </div>
  <div class="card">
    <div class="label">総コマンド数</div>
    <div class="value" style="color:var(--blue)">{total_cmd}</div>
    <div class="sub">累計実行回数</div>
  </div>
  <div class="card">
    <div class="label">プロジェクト数</div>
    <div class="value" style="color:var(--yellow)">{pj_count}</div>
    <div class="sub">💡{stage_counts.get('💡 アイデア',0)} 🔨{stage_counts.get('🔨 作成中',0)} ✅{stage_counts.get('✅ 完了',0)}</div>
  </div>
</div>

<div class="charts">
  <div class="chart-box full">
    <h2>トークン節約タイムライン</h2>
    <canvas id="tokenChart"></canvas>
  </div>
  <div class="chart-box">
    <h2>日次コマンド数</h2>
    <canvas id="cmdChart"></canvas>
  </div>
  <div class="chart-box">
    <h2>プロジェクトライフサイクル</h2>
    <canvas id="gantChart"></canvas>
  </div>
</div>

<script>
const dates = {json.dumps(dates)};
const saved = {json.dumps(saved)};
const inputTok = {json.dumps(input_tok)};
const savingsPct = {json.dumps(savings_pct)};
const commands = {json.dumps(commands)};
const pjLabels = {pj_labels};
const pjDates = {pj_dates};
const pjColors = {pj_colors};
const pjBgs = {pj_bgs};
const pjStages = {pj_stages};

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';

// Token timeline
new Chart(document.getElementById('tokenChart'), {{
  type: 'bar',
  data: {{
    labels: dates,
    datasets: [
      {{
        label: '節約トークン',
        data: saved,
        backgroundColor: 'rgba(74,222,128,0.5)',
        borderColor: '#4ade80',
        borderWidth: 1,
        yAxisID: 'y',
        order: 2,
      }},
      {{
        label: '節約率 %',
        data: savingsPct,
        type: 'line',
        borderColor: '#a78bfa',
        backgroundColor: 'transparent',
        pointRadius: 2,
        tension: 0.3,
        yAxisID: 'y1',
        order: 1,
      }}
    ]
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    scales: {{
      y: {{ position: 'left', title: {{ display: true, text: '節約トークン数' }} }},
      y1: {{ position: 'right', min: 0, max: 100, title: {{ display: true, text: '節約率 %' }}, grid: {{ drawOnChartArea: false }} }},
      x: {{ ticks: {{ maxTicksLimit: 10 }} }}
    }}
  }}
}});

// Command chart
new Chart(document.getElementById('cmdChart'), {{
  type: 'bar',
  data: {{
    labels: dates,
    datasets: [{{ label: 'コマンド数', data: commands, backgroundColor: 'rgba(96,165,250,0.5)', borderColor: '#60a5fa', borderWidth: 1 }}]
  }},
  options: {{ responsive: true, scales: {{ x: {{ ticks: {{ maxTicksLimit: 8 }} }} }} }}
}});

// Project gantt (horizontal bar as doughnut alternative)
new Chart(document.getElementById('gantChart'), {{
  type: 'bar',
  data: {{
    labels: pjLabels,
    datasets: [{{
      label: 'プロジェクト',
      data: pjLabels.map(() => 1),
      backgroundColor: pjBgs,
      borderColor: pjColors,
      borderWidth: 2,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: (ctx) => pjStages[ctx.dataIndex] + '  ' + (pjDates[ctx.dataIndex] || ''),
        }}
      }}
    }},
    scales: {{
      x: {{ display: false }},
      y: {{ ticks: {{ font: {{ size: 11 }} }} }}
    }}
  }}
}});
</script>
</body>
</html>"""

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✅ {OUT} 生成完了 ({len(html):,} chars)")


if __name__ == "__main__":
    build()
