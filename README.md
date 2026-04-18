# ローカルAI画像エディタ

Adobe Firefly の代替を目指した、**完全ローカル動作**の AI 画像編集デスクトップアプリです。
課金不要・インターネット不要・プライバシー保護。Python + PyQt5 で動作します。

---

## 機能一覧

| 機能 | 説明 | 使用AI |
|------|------|--------|
| 🔲 背景除去 | ワンクリックで背景を透過 PNG に変換 | U²-Net (ONNX) |
| ✂️ 選択除去 | 矩形で囲んだ範囲だけ残して背景を除去 | GrabCut (OpenCV) |
| ✏️ 生成塗りつぶし | ブラシでマスクを描き、プロンプトで AI 生成 | Stable Diffusion Inpaint / OpenCV Telea |
| 🔍 高解像度化 | 画像を 4 倍に高解像度化 | Real-ESRGAN / PIL LANCZOS |

全機能にフォールバックがあり、重量級 AI モデルが未インストールでも動作します。

---

## スクリーンショット

```
[ 📂 開く ]  [ 💾 保存 ]  |  [ 🔲 背景除去 ]  [ ✂️ 選択除去 ]  [ ✏️ 生成塗りつぶし ]  [ 🔍 高解像度化 ]  |  [ ▶ 実行 ]
┌─────────────────────────────────────────────────────┐
│                                                     │
│                   画像キャンバス                      │
│           （ズーム・パン対応）                         │
│                                                     │
└─────────────────────────────────────────────────────┘
ステータスバー: 処理状況・ファイル名
```

---

## 必要環境

- Python 3.10 以上
- Windows 10/11（Mac/Linux でも動作予定）

---

## インストール

### 1. 依存パッケージ（必須）

```bash
pip install PyQt5 Pillow numpy opencv-python
```

### 2. 背景除去 AI（推奨・約 170 MB）

```bash
pip install onnxruntime
```

> モデルは初回実行時に自動ダウンロードされます。

### 3. 高解像度化 AI（オプション・約 64 MB）

```bash
pip install realesrgan basicsr
```

> 未インストール時は PIL の高品質リサイズで代替します。

### 4. 生成塗りつぶし AI（オプション・約 4 GB）

```bash
pip install diffusers transformers accelerate torch
```

> 未インストール時は OpenCV Telea で塗りつぶします。GPU 推奨。

---

## 起動方法

```bash
cd src
python main.py
```

初回起動時にモデルのインストール案内ウィザードが表示されます。

---

## 使い方

### 背景除去
1. 「📂 開く」で画像を読み込む
2. 「🔲 背景除去」を選択
3. 「▶ 実行」を押す → 透過 PNG が生成される
4. 「💾 保存」で書き出す

### 選択除去
1. 「✂️ 選択除去」を選択
2. キャンバス上でドラッグして残したい範囲を矩形選択
3. 「▶ 実行」を押す

### 生成塗りつぶし
1. 「✏️ 生成塗りつぶし」を選択 → ダイアログでプロンプトを入力
2. ブラシで塗りつぶしたい領域を塗る（右クリックで消去）
3. 「▶ 実行」を再度押す → AI が生成

### 高解像度化
1. 「🔍 高解像度化」を選択
2. 「▶ 実行」を押す → 4 倍に拡大
3. 「💾 保存」で書き出す

---

## プロジェクト構成

```
src/
├── main.py                  # エントリポイント
├── ai/
│   ├── background_remover.py  # U²-Net ONNX 背景除去
│   ├── grabcut_remover.py     # GrabCut 選択除去
│   ├── inpainter.py           # SD Inpaint / OpenCV 塗りつぶし
│   └── upscaler.py            # Real-ESRGAN / PIL 高解像度化
├── ui/
│   ├── main_window.py         # メインウィンドウ・処理フロー
│   ├── canvas_widget.py       # 画像キャンバス（ズーム・ブラシ）
│   ├── toolbar_widget.py      # ツールバー
│   ├── inpaint_dialog.py      # 生成塗りつぶし設定ダイアログ
│   ├── first_run_wizard.py    # 初回起動ウィザード
│   └── progress_dialog.py    # 進捗ダイアログ
└── tests/
    ├── test_canvas_widget.py
    ├── test_background_remover.py
    └── test_grabcut_remover.py
```

---

## テスト実行

```bash
cd src
python -m pytest tests/ -v
```

---

## ライセンス

MIT License

---

## 開発メモ

このプロジェクトは Claude Code による疑似スクラムチーム（PO / SM / Dev / QA）で開発されています。
スプリント管理は `memory/` ディレクトリの Markdown ファイルで行っています。
