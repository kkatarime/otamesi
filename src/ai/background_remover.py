import time
from pathlib import Path
from PIL import Image

_MODEL_CACHE = Path.home() / ".u2net" / "u2net.onnx"


def is_model_cached() -> bool:
    return _MODEL_CACHE.exists()


def remove_background(image: Image.Image) -> tuple[Image.Image, float]:
    """背景を除去してRGBA画像と処理時間を返す。初回はモデルをDL（約176MB）。"""
    from rembg import remove
    t0 = time.perf_counter()
    result = remove(image)
    elapsed = time.perf_counter() - t0
    return result, elapsed
