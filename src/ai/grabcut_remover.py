import time
import numpy as np
from PIL import Image


def remove_background_by_rect(
    image: Image.Image,
    rect: tuple[int, int, int, int],  # (x, y, w, h) 画像座標
) -> tuple[Image.Image, float]:
    """
    矩形の外側を透明にする（矩形内のピクセルは100%保持）。
    GrabCutより確実：選択範囲内は絶対に消えない。
    """
    t0 = time.perf_counter()

    rgba = np.array(image.convert("RGBA"))
    x, y, w, h = rect

    # 矩形外のアルファを0にする
    mask = np.zeros(rgba.shape[:2], dtype=np.uint8)
    x2 = min(x + w, rgba.shape[1])
    y2 = min(y + h, rgba.shape[0])
    mask[max(0, y):y2, max(0, x):x2] = 255

    rgba[:, :, 3] = mask
    return Image.fromarray(rgba, "RGBA"), time.perf_counter() - t0
