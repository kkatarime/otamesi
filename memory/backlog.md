# Product Backlog
最終更新: 2026-04-18 by Product Owner

## 優先度凡例
- P1: Must Have（スプリント必須）
- P2: Should Have
- P3: Nice to Have

## バックログ

| ID | タイトル | 優先度 | ポイント | ステータス | 受入条件 |
|----|----------|--------|----------|------------|----------|
| US-001 | Hello World Webサーバー | P1 | 3 | READY | `GET /` で `{"message":"Hello World"}` が返る |
| US-002 | ヘルスチェックエンドポイント | P1 | 2 | READY | `GET /health` で `{"status":"ok"}` が返る |
| US-003 | ユーザー一覧API | P2 | 5 | READY | `GET /users` でJSONの配列が返る |
| US-004 | ユーザー作成API | P2 | 5 | READY | `POST /users` でユーザーを作成できる |
| US-005 | エラーハンドリング | P2 | 3 | READY | 404/500のエラーレスポンスが統一された形式で返る |
| US-006 | ロギング機能 | P3 | 3 | READY | リクエスト・レスポンスがログファイルに記録される |

## IN_SPRINT（現スプリント中）
（スプリント開始時にここへ移動）

## DONE（完了済み）
（完了したストーリーはここへ移動）
