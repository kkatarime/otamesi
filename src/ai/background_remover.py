"""
U2Net ONNX を直接使った背景除去。
rembg に依存しない完全自己完結実装。
"""
from pathlib import Path
import time
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_PATH = Path.home() / ".u2net" / "u2net.onnx"
_INPUT_SIZE = 320          # U2Net 固定入力サイズ
_MAX_SIDE = 1500           # これ以上の画像は推論前にリサイズ
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# セッションをモジュールレベルでキャッシュ（2回目以降の呼び出しを高速化）
_session: ort.InferenceSession | None = None


def is_model_cached() -> bool:
    return MODEL_PATH.exists()


def _get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        _session = ort.InferenceSession(
            str(MODEL_PATH),
            providers=["CPUExecutionProvider"],
        )
    return _session


def _preprocess(image: Image.Image) -> np.ndarray:
    """RGB画像 → U2Net 入力テンソル (1, 3, 320, 320)"""
    rgb = image.convert("RGB").resize((_INPUT_SIZE, _INPUT_SIZE), Image.LANCZOS)
    arr = np.array(rgb, dtype=np.float32) / 255.0
    arr = (arr - _MEAN) / _STD
    return arr.transpose(2, 0, 1)[np.newaxis]   # HWC → 1CHW


def _postprocess(raw: np.ndarray, orig_size: tuple[int, int]) -> Image.Image:
    """推論出力 (1,1,320,320) → オリジナルサイズのグレースケールマスク"""
    mask = raw[0, 0]
    lo, hi = mask.min(), mask.max()
    mask = (mask - lo) / (hi - lo + 1e-8)
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))
    return mask_img.resize(orig_size, Image.LANCZOS)


def remove_background(
    image: Image.Image,
    progress_cb=None,          # Optional[Callable[[str], None]]
) -> tuple[Image.Image, float]:
    """
    背景を除去して RGBA 画像と処理時間(秒)を返す。
    progress_cb(message) でステージ進捗を呼び出し元に通知できる。
    """
    def _progress(msg: str):
        if progress_cb:
            progress_cb(msg)

    t0 = time.perf_counter()

    # 1. 大きな画像は推論前にリサイズ（メモリ対策）
    _progress("画像を前処理しています…")
    orig_size = image.size
    work = image
    if max(orig_size) > _MAX_SIDE:
        ratio = _MAX_SIDE / max(orig_size)
        work = image.resize(
            (int(orig_size[0] * ratio), int(orig_size[1] * ratio)),
            Image.LANCZOS,
        )

    # 2. モデル読み込み（初回のみ）
    _progress("AIモデルを読み込んでいます…")
    session = _get_session()

    # 3. 推論
    _progress("背景を検出しています…（CPUの場合 1〜3分かかります）")
    inp = _preprocess(work)
    input_name = session.get_inputs()[0].name
    raw = session.run(None, {input_name: inp})[0]

    # 4. マスク生成・合成
    _progress("マスクを適用しています…")
    mask = _postprocess(raw, orig_size)
    rgba = image.convert("RGBA")
    rgba.putalpha(mask)

    return rgba, time.perf_counter() - t0
