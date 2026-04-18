import time
from PIL import Image


def remove_background(image: Image.Image) -> tuple[Image.Image, float]:
    """背景を除去してRGBA画像と処理時間を返す。初回はモデルをDL（約170MB）。"""
    from rembg import remove  # 遅延インポートで起動を速くする
    t0 = time.perf_counter()
    result = remove(image)
    elapsed = time.perf_counter() - t0
    return result, elapsed
