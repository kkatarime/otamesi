"""
生成塗りつぶし（Inpainting）モジュール。
diffusers が利用可能かつモデルがキャッシュ済みなら SD Inpaint、
なければ OpenCV Telea にフォールバック。
"""
from pathlib import Path
import time
import numpy as np
from PIL import Image

_MODEL_DIR = Path.home() / ".sd_inpaint"


def is_diffusers_available() -> bool:
    try:
        import diffusers  # noqa: F401
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


def is_model_cached() -> bool:
    return (_MODEL_DIR / "model_index.json").exists()


def _inpaint_sd(
    image: Image.Image,
    mask: Image.Image,
    prompt: str,
    negative_prompt: str,
    progress_cb,
) -> Image.Image:
    import torch
    from diffusers import StableDiffusionInpaintPipeline

    progress_cb("SDモデルを読み込んでいます…")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        str(_MODEL_DIR),
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    ).to(device)
    pipe.safety_checker = None

    orig_w, orig_h = image.size
    # SDは512×512を期待するためリサイズして推論後に戻す
    proc_image = image.convert("RGB").resize((512, 512), Image.LANCZOS)
    proc_mask = mask.resize((512, 512), Image.NEAREST)

    progress_cb(f"生成中… プロンプト: {prompt[:40]}")
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt or "blurry, bad quality",
        image=proc_image,
        mask_image=proc_mask,
        num_inference_steps=20,
    ).images[0]

    # 元サイズに戻し、マスク外は元画像を使用
    result = result.resize((orig_w, orig_h), Image.LANCZOS)
    mask_resized = proc_mask.resize((orig_w, orig_h), Image.NEAREST).convert("L")
    base = image.convert("RGBA")
    gen = result.convert("RGBA")
    mask_np = np.array(mask_resized)
    base_np = np.array(base)
    gen_np = np.array(gen)
    alpha = (mask_np > 127).astype(np.float32)[..., np.newaxis]
    blended = (gen_np * alpha + base_np * (1 - alpha)).astype(np.uint8)
    return Image.fromarray(blended, "RGBA")


def _inpaint_opencv(image: Image.Image, mask: Image.Image, progress_cb) -> Image.Image:
    import cv2

    progress_cb("OpenCV Telea で塗りつぶし中…")
    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    mask_np = np.array(mask.convert("L"))
    mask_bin = (mask_np > 127).astype(np.uint8) * 255
    result_bgr = cv2.inpaint(bgr, mask_bin, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    out = Image.fromarray(result_rgb, "RGB")
    if image.mode == "RGBA":
        out = out.convert("RGBA")
        orig_a = image.split()[3]
        out.putalpha(orig_a)
    return out


def inpaint(
    image: Image.Image,
    mask: Image.Image,
    prompt: str = "",
    negative_prompt: str = "",
    progress_cb=None,
) -> tuple[Image.Image, float]:
    """
    マスク領域を塗りつぶす。
    mask: L mode PIL Image (白=塗りつぶし対象)
    returns: 結果画像, 処理時間(秒)
    """
    def _progress(msg: str):
        if progress_cb:
            progress_cb(msg)

    t0 = time.perf_counter()

    if is_diffusers_available() and is_model_cached() and prompt:
        result = _inpaint_sd(image, mask, prompt, negative_prompt, _progress)
    else:
        if not is_diffusers_available():
            _progress("diffusers 未インストール → OpenCV フォールバック")
        elif not is_model_cached():
            _progress("SDモデル未キャッシュ → OpenCV フォールバック")
        elif not prompt:
            _progress("プロンプト未入力 → OpenCV フォールバック")
        result = _inpaint_opencv(image, mask, _progress)

    return result, time.perf_counter() - t0
