あなたはScrum Masterとして、スプリントレトロスペクティブを実施します。CLAUDE.mdのSMロール定義に従って行動してください。

## 手順

1. `memory/sprint-current.md` を読み込み、全タスクのステータスを集計する
   ```
   完了(DONE): N件 / Npt
   未完了(TODO/IN_PROGRESS): N件 / Npt
   要修正(NEEDS_REVISION): N件 / Npt
   ```

2. `memory/standup-log.md` から今スプリントのエントリを確認する

3. `memory/impediments.md` から今スプリントの障害を確認する

4. 以下の観点でKeep/Problem/Tryを生成する：

   **Keep（良かったこと）**
   - 高い完了率（>80%）であれば評価
   - 障害が少なかった点
   - レビューが迅速だった点

   **Problem（問題点）**
   - NEEDS_REVISIONが多かった場合
   - BLOCKED が発生した場合
   - バーンダウンが計画より大幅に遅れた場合

   **Try（改善提案）**
   - 具体的なアクションアイテムとして記述
   - 次スプリントですぐ実行できる内容にする

5. `memory/retrospectives/retro-{スプリント番号}.md` に保存する
   ```markdown
   # Sprint {N} レトロスペクティブ — {日付}

   ## 集計
   ...

   ## Keep
   ...

   ## Problem
   ...

   ## Try（アクションアイテム）
   ...
   ```

6. Tryのアクションアイテムを `memory/backlog.md` に追加する（P2として）

7. `memory/sprint-current.md` を `memory/sprint-history/sprint-{N}.md` にコピーする

8. `memory/sprint-current.md` を次スプリント用にリセットする（テンプレートに戻す）

9. `memory/backlog.md` の完了ストーリーのステータスを `DONE` に更新する

## 出力フォーマット
レトロスペクティブの全内容をチャットに表示してからファイルを保存すること。
