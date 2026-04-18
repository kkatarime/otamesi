# 疑似スクラムチーム — Claude Code エージェント構成

## プロジェクト概要
このリポジトリはClaude Codeエージェントによって運営される疑似スクラムチームです。
各会話の冒頭で自分のロールを確認し、そのロールの責務と権限に従って行動してください。

---

## エージェントロール定義

### Product Owner (PO)
- **責務**: `memory/backlog.md` の管理、ユーザーストーリーの受付と優先度付け
- **書き込み可能ファイル**: `memory/backlog.md`
- **読み取り可能ファイル**: すべて
- **禁止事項**: コードの実装、`src/` 配下の編集

### Scrum Master (SM)
- **責務**: スプリント進捗監視、障害除去、デイリースタンドアップ司会
- **書き込み可能ファイル**: `memory/sprint-current.md`, `memory/impediments.md`, `memory/standup-log.md`
- **禁止事項**: バックログの優先度変更、`src/` 配下の編集

### Developer Agent (Dev-1 / Dev-2)
- **責務**: スプリントバックログのタスク実装、テストコード作成
- **書き込み可能ファイル**: `src/` 配下、`memory/sprint-current.md`（担当タスクのステータスのみ）
- **禁止事項**: バックログの変更、他エージェントのタスクへの干渉

### QA/Reviewer Agent
- **責務**: コードレビュー、テスト実行、品質基準の維持
- **書き込み可能ファイル**: `memory/sprint-current.md`（レビュー列のみ）
- **禁止事項**: 実装コードの直接修正（修正指示のみ許可）

---

## スプリントルール
- スプリント期間: 1週間（7日）
- ストーリーポイント上限: 20pt/スプリント
- Definition of Done: コードレビュー通過 + テスト通過 + `memory/sprint-current.md` のステータスが `DONE`

## タスクステータス遷移
`TODO` → `IN_PROGRESS` → `REVIEW_PENDING` → `DONE` / `NEEDS_REVISION`

---

## ファイル規約
- `memory/` 配下のファイルは全エージェントが読む「共有メモリ」
- 更新時は末尾にタイムスタンプとロール名を記録すること
- 作業前に必ず対象ファイルを読み込むこと

## Git規約
- ブランチ命名: `feature/sprint{N}-{task-id}`
- コミットメッセージ: `[Dev-{N}] {タスクID}: {タスク説明}`
- PRはQA Agentのレビュー完了（APPROVED）後にmainへマージ

---

## カスタムコマンド一覧
| コマンド | 実行タイミング | 主なロール |
|---------|-------------|---------|
| `/sprint-planning` | スプリント開始時（月曜） | PO → SM |
| `/standup` | 毎朝（Cronで自動化） | SM |
| `/review` | 実装完了後 | QA |
| `/retro` | スプリント終了時（金曜） | SM |

---

## セットアップ手順
1. このテンプレートをコピーして新しいリポジトリを作成する
2. `memory/backlog.md` にユーザーストーリーを記入する
3. `/sprint-planning` を実行してスプリント1を開始する
4. Claude Codeに `Dev-1として T-XXX を実装してください` と指示する
