"""
高解像度化（Upscaling）モジュール。
realesrgan が利用可能なら Real-ESRGAN、なければ PIL LANCZOS にフォールバック。
"""
from pathlib import Path
import time
import numpy as np
from PIL import Image

_MODEL_DIR = Path.home() / ".realesrgan"


def is_realesrgan_available() -> bool:
    try:
        from realesrgan import RealESRGANer  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # noqa: F401
        return True
    except ImportError:
        return False


def is_model_cached() -> bool:
    return (_MODEL_DIR / "RealESRGAN_x4plus.pth").exists()


def _upscale_realesrgan(image: Image.Image, scale: int, progress_cb) -> Image.Image:
    import cv2
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    progress_cb("Real-ESRGANモデルを読み込んでいます…")
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_block=23, num_grow_ch=32, scale=4)
    upsampler = RealESRGANer(
        scale=4,
        model_path=str(_MODEL_DIR / "RealESRGAN_x4plus.pth"),
        model=model,
        tile=512,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )
    progress_cb(f"高解像度化中… （{image.width}×{image.height} → {image.width*scale}×{image.height*scale}px）")
    img_bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    output_bgr, _ = upsampler.enhance(img_bgr, outscale=scale)
    output_rgb = cv2.cvtColor(output_bgr, cv2.COLOR_BGR2RGB)
    result = Image.fromarray(output_rgb, "RGB")
    if image.mode == "RGBA":
        orig_a = image.split()[3].resize(result.size, Image.LANCZOS)
        result = result.convert("RGBA")
        result.putalpha(orig_a)
    return result


def upscale(
    image: Image.Image,
    scale: int = 4,
    progress_cb=None,
) -> tuple[Image.Image, float]:
    """
    画像を scale 倍に高解像度化する。
    Real-ESRGAN 利用可能な場合はAI拡大、なければ高品質リサイズ。
    returns: 拡大画像, 処理時間(秒)
    """
    def _progress(msg: str):
        if progress_cb:
            progress_cb(msg)

    t0 = time.perf_counter()

    if is_realesrgan_available() and is_model_cached():
        result = _upscale_realesrgan(image, scale, _progress)
    else:
        mode_label = "Real-ESRGAN" if is_realesrgan_available() else "高品質リサイズ（AI拡大にはrealesrganをインストール）"
        _progress(f"{mode_label}で拡大中… {image.width}×{image.height} → {image.width*scale}×{image.height*scale}px")
        w, h = image.size
        result = image.resize((w * scale, h * scale), Image.LANCZOS)

    return result, time.perf_counter() - t0
