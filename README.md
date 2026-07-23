# cortana-scope

Cortana組織が自分自身を俯瞰する可視化ダッシュボード。

## コンセプト

Record-RINGが「消えゆく建築空間を空気感ごと記録する」ように、  
cortana-scopeは「Cortanaシステムの活動を時系列で記録・可視化する」。

毎日の意思決定・トークン消費・プロジェクト進捗・Slack活動が  
インタラクティブなHTMLダッシュボードとして結晶化する。

## 可視化4本柱

| # | ビジュアル | データソース |
|---|---|---|
| 1 | **トークンタイムライン** | cortana_state.json (日次コスト・削減率) |
| 2 | **プロジェクトガント** | project_registry (💡→🔨→✅ライフサイクル) |
| 3 | **意思決定速度** | #all-cortana (HOLD→GO日数・夜間GO率) |
| 4 | **アクティビティヒートマップ** | Slack全チャンネル (時間帯×チャンネル密度) |

## アーキテクチャ

```
データ収集 (Python)
  ├── cortana_state.json
  ├── Slack API (#all-cortana / #cortana-ideas)
  └── git log (全PJのコミット履歴)
        ↓
  集計・整形 → data/snapshot.json
        ↓
  Chart.js テンプレート → docs/index.html
        ↓
  Vercel (cortana-db-v2 経由) で自動デプロイ
```

## コマンド

```bash
python scope.py build     # snapshot.json 生成 + HTML ビルド
python scope.py preview   # ローカルプレビュー (port 8766)
python scope.py push      # git commit + push (Vercel自動デプロイ)
```

## 夜間ルーティン連携

夜間ルーティン完了後に `scope.py build && scope.py push` を実行することで  
毎朝最新状態のダッシュボードが公開される。

## スコープ境界

- **対象外**: リアルタイム更新・WebSocket・認証UI
- **対象外**: Cortana以外の組織への転用（汎用化は V2 以降）
- **出力**: 静的HTML (Git管理・Vercel完結)
