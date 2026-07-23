# cortana-scope — プロジェクト・ロール定義

Cortana組織の活動データを可視化するダッシュボード生成ツール。
上位の `/Users/620306/Vibe-Coding/CLAUDE.md`（PgM 自動起動）に従属する。

## コンセプト（絶対に外さない一本の糸）

**「Cortana組織が自分自身を俯瞰する鏡」**

ログを眺めるのではなく、**パターンを見る**。  
意思決定の速度、プロジェクトの停滞、コストの波——  
これらを可視化することで、次の判断が速くなる。

静的HTML出力。サーバーなし。Git管理。Vercel完結。

## ロール定義

| ロール | 責務 |
|---|---|
| **データエンジニア** | cortana_state.json / Slack API / git log の収集・整形 |
| **ビジュアライザー** | Chart.js による4本柱の実装 |
| **インテグレーター** | 夜間ルーティンへの組み込み・Vercelデプロイ自動化 |

## データソース定義

| ソース | パス / API | 用途 |
|---|---|---|
| token history | `../cortana-db-v2/data/cortana_state.json` | トークンタイムライン |
| project registry | 同上 `.projects.main[]` | ガントチャート |
| Slack #all-cortana | C0BCW3H6K5E | 意思決定速度 |
| Slack #cortana-ideas | C0BJCCK67E2 | アイデア→PJ転換率 |
| git log | 全 Vibe-Coding/* PJ | コミット速度 |

## 技術方針

- Python 3.12+、依存最小限（requests + jinja2 + Chart.js CDN）
- `data/snapshot.json` が唯一の中間ファイル（再生成可能）
- `docs/index.html` が成果物（GitHub Pages / Vercel で公開）
- Slack APIトークンは `SLACK_BOT_TOKEN` 環境変数から取得
- 課金・外部発信が絡む変更は PgM 経由でボスに確認

## スコープ境界

- V0（現在）: スキャフォールド + データ設計
- V1: トークンタイムライン + プロジェクトガント（データ既存で即実装可能）
- V2: Slack連携（意思決定速度・ヒートマップ）
- V3: 夜間ルーティン自動更新・PMOヘルススコア算出
- 対象外: リアルタイム更新・認証UI・汎用化

## 起案メタ

- 起案: アイデアマン（クローンリーダー）/ 2026-07-23
- 背景: Record-RING（万博大屋根リングの3DGSアーカイブ）から着想。
  「記録すること自体がプロジェクト」という潮流 × Cortana自身のビッグデータ。
- 夜間レポート未解決課題「PMOヘルススコア」の自然な解としても機能する。
