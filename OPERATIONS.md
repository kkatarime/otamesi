# 疑似スクラムチーム 運用マニュアル

## 1. 仕組みの概要

### なぜこれが「疑似スクラムチーム」なのか

Claude Code は単一のAIエージェントです。しかし **CLAUDE.md に書かれたロール定義** と **カスタムスラッシュコマンド** を組み合わせることで、1つのエージェントが「Product Owner」「Scrum Master」「Developer」「QA」を順番に演じてスクラムプロセスを回します。

```
[あなた（ユーザー）]
        ↓ コマンドを入力
[Claude Code エージェント]
        ↓ CLAUDE.md を読んでロールを切り替え
  ┌─────────────────────────────┐
  │  PO → SM → Dev → QA → SM  │  ← 1つのエージェントが順番に担当
  └─────────────────────────────┘
        ↓ 結果を書き込む
[memory/ ディレクトリ（共有メモリ）]
```

---

## 2. アーキテクチャ詳細

### 2-1. 情報の流れ

```
ユーザーの要望
    │
    ▼
memory/backlog.md ──────────────────────────────────────────────
（バックログ）         │                                         │
                       │ /sprint-planning                        │
                       ▼                                         │
             memory/sprint-current.md                           │
             （スプリント状態）                                   │
                  │          │                                   │
                  │ 実装依頼  │ /standup                         │ /retro
                  ▼          ▼                                   │
               src/    memory/standup-log.md                     │
              （コード）  （スタンドアップ記録）                    │
                  │                                              │
                  │ /review                                      │
                  ▼                                              │
        memory/sprint-current.md                                 │
        （レビュー結果追記）                                       │
                  │                                              │
                  └─────────────────────────────────────────────▶
                                                    memory/retrospectives/
                                                    memory/sprint-history/
```

### 2-2. ファイルの役割

| ファイル | 書く人 | 読む人 | 内容 |
|---------|--------|--------|------|
| `CLAUDE.md` | セットアップ時のみ | 全エージェント | ロール定義・ルール・コマンド一覧 |
| `memory/backlog.md` | PO | PO・SM | ユーザーストーリーの一覧と優先度 |
| `memory/sprint-current.md` | SM・Dev・QA | 全員 | 現スプリントのタスク状態 |
| `memory/standup-log.md` | SM | SM | スタンドアップ記録 |
| `memory/impediments.md` | SM | SM・Dev | 障害リスト |
| `memory/audit-log.txt` | Hook（自動） | 管理者 | ツール操作ログ |
| `memory/sprint-history/` | SM（/retro時） | SM | 過去スプリントのアーカイブ |
| `memory/retrospectives/` | SM（/retro時） | SM | レトロスペクティブ記録 |

### 2-3. カスタムコマンドの仕組み

`.claude/commands/` 配下の `.md` ファイルがそのままスラッシュコマンドになります。

```
.claude/commands/sprint-planning.md  →  /sprint-planning
.claude/commands/standup.md          →  /standup
.claude/commands/review.md           →  /review
.claude/commands/retro.md            →  /retro
```

コマンドを実行すると、MDファイルの内容がClaudeへのシステムプロンプトとして渡され、エージェントがその手順に従って動作します。

---

## 3. スプリントサイクルの全手順

### 週間スケジュール

```
月曜日 08:00  スプリント計画 (/sprint-planning)
月〜金 09:00  デイリースタンドアップ (/standup) ← Cronで自動化可能
火〜木         実装・レビュー依頼
金曜日 17:00  レビュー (/review) → レトロ (/retro)
```

---

### Step 1: バックログにストーリーを追加する（Product Owner）

**いつ**: スプリント開始前、または思いついたとき

**方法**:
```
"Product Ownerとして、以下のユーザーストーリーをバックログに追加してください：
ユーザーがパスワードをリセットできる機能（P1、5ポイント）"
```

Claude が `memory/backlog.md` に追記します。

**バックログのステータス**:
- `READY` — スプリントに入れる準備ができている
- `IN_SPRINT` — 現スプリント中
- `DONE` — 完了済み

---

### Step 2: スプリント計画 (/sprint-planning)

**いつ**: 毎週月曜日（スプリント開始時）

**実行**:
```
/sprint-planning
```

**何が起きるか**:
1. POとして `memory/backlog.md` を読み、優先度上位を提案
2. ユーザーが確認・承認
3. SMとしてタスクに分解（1タスク = 2〜4時間）
4. `memory/sprint-current.md` を更新
5. `memory/backlog.md` のステータスを `IN_SPRINT` に変更

**出力例**:
```
## Sprint 1 計画完了

スプリントゴール: Hello World Webサーバーの基盤を構築する
期間: 2026-04-21 〜 2026-04-27
総ポイント: 5pt

| タスクID | 説明 | 担当 | ポイント | ステータス |
|---------|------|------|----------|------------|
| T-001 | package.json初期化 | Dev-1 | 1 | TODO |
| T-002 | Expressサーバー実装 | Dev-1 | 2 | TODO |
| T-003 | テストコード作成 | Dev-2 | 1 | TODO |
| T-004 | /healthエンドポイント | Dev-2 | 1 | TODO |
```

---

### Step 3: 実装（Developer Agent）

**いつ**: スプリント期間中（火〜木）

**方法A — タスクを指定して実装**:
```
"Dev-1としてT-001（package.json初期化）を実装してください"
```

**方法B — 次のTODOを自動選択**:
```
"Dev-1として次のTODOタスクを実装してください"
```

**何が起きるか**:
1. `memory/sprint-current.md` でタスク詳細を確認
2. タスクステータスを `IN_PROGRESS` に更新
3. `src/` 配下に実装コード・テストコードを生成
4. タスクステータスを `REVIEW_PENDING` に更新

**実装後のステータス遷移**:
```
TODO → IN_PROGRESS → REVIEW_PENDING
```

---

### Step 4: デイリースタンドアップ (/standup)

**いつ**: 毎朝（Cronで自動化推奨）

**実行**:
```
/standup
```

**何が起きるか**:
1. `memory/sprint-current.md` の全タスクを確認
2. Dev-1・Dev-2それぞれの「昨日/今日/障害」をサマリー
3. バーンダウン計算（進捗率 vs 理想進捗率）
4. `memory/standup-log.md` に追記
5. 障害があれば `memory/impediments.md` に追記

**バーンダウン警告**:
```
⚠️ 警告: 進捗率15% / 理想43%（-28%の遅れ）
→ 残タスクの見直しを推奨します
```

---

### Step 5: コードレビュー (/review)

**いつ**: 実装完了後（REVIEW_PENDINGが出たとき）

**実行**:
```
/review
```

**何が起きるか**:
1. `REVIEW_PENDING` のタスクを特定
2. git diff で変更内容を確認
3. 以下の基準でレビュー：
   - コード品質（関数50行以内・可読性）
   - テストの存在
   - セキュリティ（入力バリデーション・機密情報）
4. 判定を `memory/sprint-current.md` に記録

**判定結果**:
- `APPROVED` → タスクステータスを `DONE` に変更
- `NEEDS_REVISION` → 具体的な修正指示を記録、Devに差し戻し

**修正対応**:
```
"Dev-1としてT-002のレビュー指摘（エラーハンドリング不足）を修正してください"
```

---

### Step 6: スプリントレトロスペクティブ (/retro)

**いつ**: スプリント最終日（金曜日）

**実行**:
```
/retro
```

**何が起きるか**:
1. 全タスクの完了率を集計
2. Keep/Problem/Try を自動生成
3. `memory/retrospectives/retro-{N}.md` に保存
4. 改善アクションアイテムをバックログに追加
5. `memory/sprint-history/sprint-{N}.md` にアーカイブ
6. `memory/sprint-current.md` を次スプリント用にリセット

**出力例**:
```
## Sprint 1 レトロスペクティブ

集計: 4/5タスク完了（80%）、4pt/5pt

### Keep ✅
- タスク分解が適切で進捗がスムーズだった
- コードレビューを全タスクに実施できた

### Problem ❌
- T-003のテストカバレッジが不足しNEEDS_REVISIONが発生

### Try 🔄
- テスト作成を実装と同時に行う（TDD）
- 1タスクのサイズを最大2時間に縮小する
```

---

## 4. Cronによる自動化

### デイリースタンドアップの自動化

**初回設定（一度だけ実行）**:
```
"毎朝9時（月〜金）に/standupを自動実行するCronをdurable:trueで設定してください"
```

**注意**: Cronは**7日で自動失効**します。毎週月曜日に再登録が必要です。

### Cronの確認・管理

```
"現在設定されているCronを一覧表示してください"
"スタンドアップのCronを削除してください"
```

---

## 5. よくある操作パターン

### バックログの優先度を変更したい
```
"Product Ownerとして、US-004の優先度をP2からP1に変更してください"
```

### タスクが完了できなかった場合（スプリント持ち越し）
```
"Scrum Masterとして、T-005を次のスプリントに持ち越してください"
```
→ `memory/sprint-current.md` のステータスを `CARRY_OVER` に変更、次の `/sprint-planning` で自動的に引き継がれます。

### 障害が発生した場合
```
"Scrum Masterとして、外部APIが停止しておりT-003がブロックされています。障害として記録してください"
```

### 複数タスクを並行して進めたい
```
"Dev-1としてT-001を、Dev-2としてT-002を並行して実装してください"
```
→ Claude が順番に実装（Dev-1 → Dev-2の順）しますが、ファイルは別々の場所に生成されます。

---

## 6. memory/ ファイルの読み方

### `sprint-current.md` のタスクステータス早見表

| ステータス | 意味 | 次のアクション |
|-----------|------|--------------|
| `TODO` | 未着手 | Devに実装依頼 |
| `IN_PROGRESS` | 実装中 | 待機 |
| `REVIEW_PENDING` | レビュー待ち | `/review` 実行 |
| `NEEDS_REVISION` | 修正必要 | Devに修正依頼 |
| `DONE` | 完了 | なし |
| `BLOCKED` | 障害で停止中 | SMに障害対応依頼 |
| `CARRY_OVER` | 次スプリントへ持ち越し | 次の `/sprint-planning` で引き継ぎ |

---

## 7. トラブルシューティング

### コマンドが意図通りに動かない場合
```
"CLAUDE.mdを読み込み、Scrum Masterとして /standup の手順に従ってください"
```
→ ロールと手順を明示的に指定することで意図通りに動きます。

### memory/ ファイルが古い情報のままの場合
```
"memory/sprint-current.md を確認して、現在の状況を整理してください"
```

### git の状態がおかしい場合
```bash
git status
git log --oneline -5
```

---

## 8. 拡張・カスタマイズ

### スプリント期間を変更したい
`CLAUDE.md` の以下の行を変更：
```
- スプリント期間: 1週間（7日）  ← ここを変更
```
`standup.md` の以下の行も変更：
```
理想進捗率 = 経過日数 / 7 × 100  ← 7を変更
```

### ストーリーポイント上限を変更したい
`CLAUDE.md` の以下の行を変更：
```
- ストーリーポイント上限: 20pt/スプリント  ← ここを変更
```
`sprint-planning.md` も同様に変更。

### 新しいロールを追加したい（例: Tech Lead）
1. `CLAUDE.md` にロール定義を追加
2. `.claude/commands/tech-lead-review.md` を作成
3. `/tech-lead-review` として使用可能になる

---

## 9. 全体のファイル構成

```
C:\Users\kiyom\kk\otamesi\
├── CLAUDE.md                   ← ロール定義・チームルール（最重要）
├── OPERATIONS.md               ← このファイル（運用マニュアル）
├── .claude/
│   ├── settings.json           ← 権限・Hooks設定
│   └── commands/
│       ├── sprint-planning.md  ← /sprint-planning の定義
│       ├── standup.md          ← /standup の定義
│       ← review.md             ← /review の定義
│       └── retro.md            ← /retro の定義
├── memory/
│   ├── backlog.md              ← プロダクトバックログ（PO管理）
│   ├── sprint-current.md       ← 現スプリントの状態（全員参照）
│   ├── standup-log.md          ← デイリースタンドアップ記録
│   ├── impediments.md          ← 障害リスト（SM管理）
│   ├── audit-log.txt           ← ツール操作ログ（自動生成）
│   ├── sprint-history/         ← 完了スプリントのアーカイブ
│   │   └── sprint-001.md
│   └── retrospectives/         ← レトロスペクティブ記録
│       └── retro-001.md
└── src/                        ← 実装コード（スプリントで生成）
```
