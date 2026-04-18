import time
import numpy as np
import cv2
from PIL import Image


def remove_background_by_rect(
    image: Image.Image,
    rect: tuple[int, int, int, int],  # (x, y, w, h) 画像座標
    iterations: int = 5,
) -> tuple[Image.Image, float]:
    """
    指定矩形内を前景として GrabCut で背景除去する。
    rect は画像ピクセル座標 (x, y, width, height)。
    """
    t0 = time.perf_counter()

    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    mask = np.zeros(bgr.shape[:2], np.uint8)
    fg_model = np.zeros((1, 65), np.float64)
    bg_model = np.zeros((1, 65), np.float64)

    x, y, w, h = rect
    x = max(0, x)
    y = max(0, y)
    w = min(w, bgr.shape[1] - x)
    h = min(h, bgr.shape[0] - y)

    cv2.grabCut(bgr, mask, (x, y, w, h), bg_model, fg_model, iterations, cv2.GC_INIT_WITH_RECT)

    # GC_FGD(1) or GC_PR_FGD(3) を前景とみなす
    fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
    rgba[:, :, 3] = fg_mask

    result = Image.fromarray(rgba, "RGBA")
    return result, time.perf_counter() - t0
