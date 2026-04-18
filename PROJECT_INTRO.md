# ローカルAI画像エディタ — プロジェクト紹介文

---

## コピペ用（日本語）

**ローカルAI画像エディタ** は、Adobe Firefly の代替を目指した完全ローカル動作の AI 画像編集デスクトップアプリです。課金不要・インターネット不要・プライバシー保護を実現しました。

### できること
- 🔲 **背景除去** — ワンクリックで背景を透過 PNG に変換（U²-Net / ONNX）
- ✂️ **選択除去** — ドラッグで範囲を選んで背景を除去（GrabCut）
- ✏️ **生成塗りつぶし** — ブラシでマスクを描いてプロンプトで AI 生成（Stable Diffusion Inpaint）
- 🔍 **高解像度化** — 画像を 4 倍に拡大（Real-ESRGAN）

全機能にフォールバックがあり、重量級 AI モデルが未インストールでも動作します。

### 技術スタック
Python / PyQt5 / ONNX Runtime / Stable Diffusion / Real-ESRGAN / OpenCV

### 開発プロセス
Claude Code エージェントが PO・Scrum Master・Developer・QA の 4 ロールを担当する疑似スクラムチームで開発。スプリント 3 回・全 18 ストーリーポイントを消化し完成。

🔗 GitHub: https://github.com/kkatarime/otamesi

---

## コピペ用（English）

**Local AI Image Editor** is a fully offline desktop app for AI-powered image editing — a free, privacy-friendly alternative to Adobe Firefly.

### Features
- 🔲 **Background Removal** — One-click background removal to transparent PNG (U²-Net / ONNX)
- ✂️ **Selection Removal** — Drag to select the region you want to keep
- ✏️ **Generative Fill** — Paint a mask, enter a prompt, and let AI fill it in (Stable Diffusion Inpaint)
- 🔍 **Upscaling ×4** — Upscale images 4× with Real-ESRGAN

All features include fallbacks and work even without heavy AI models installed.

### Tech Stack
Python / PyQt5 / ONNX Runtime / Stable Diffusion / Real-ESRGAN / OpenCV

### Development
Built by a simulated Scrum team powered by Claude Code agents (PO / Scrum Master / Developer / QA). Completed in 3 sprints, 18 story points total.

🔗 GitHub: https://github.com/kkatarime/otamesi
