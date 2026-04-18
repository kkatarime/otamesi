"""
生成塗りつぶし（Inpainting）モジュール。
diffusers が利用可能かつモデルがキャッシュ済みなら SD Inpaint、
なければ OpenCV Telea にフォールバック。
"""
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageFilter

_MODEL_DIR = Path.home() / ".sd_inpaint"

_DEFAULT_NEGATIVE = (
    "blurry, bad quality, distorted, ugly, low resolution, "
    "artifacts, noise, deformed, out of frame, duplicate"
)
_QUALITY_SUFFIX = ", highly detailed, photorealistic, sharp focus, 4k"


def is_diffusers_available() -> bool:
    try:
        import diffusers  # noqa: F401
        import torch      # noqa: F401
        return True
    except (ImportError, OSError):
        return False


def is_model_cached() -> bool:
    return (_MODEL_DIR / "model_index.json").exists()


def _feather_mask(mask: Image.Image, radius: int = 8) -> Image.Image:
    """マスク境界をGaussianぼかしで滑らかにする"""
    arr = np.array(mask.convert("L")).astype(np.float32) / 255.0
    blurred = np.array(
        Image.fromarray((arr * 255).astype(np.uint8), "L").filter(
            ImageFilter.GaussianBlur(radius=radius)
        )
    ).astype(np.float32) / 255.0
    # ぼかした値と元の値を合成（硬い中心 + 柔らかい境界）
    feathered = np.clip(arr * 0.6 + blurred * 0.4, 0, 1)
    return Image.fromarray((feathered * 255).astype(np.uint8), "L")


def _inpaint_sd(
    image: Image.Image,
    mask: Image.Image,
    prompt: str,
    negative_prompt: str,
    steps: int,
    guidance_scale: float,
    seed: int,
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

    # 品質トークンを自動付加
    full_prompt = prompt + _QUALITY_SUFFIX
    full_neg = negative_prompt if negative_prompt else _DEFAULT_NEGATIVE

    orig_w, orig_h = image.size
    proc_image = image.convert("RGB").resize((512, 512), Image.LANCZOS)

    # マスクをフェザリングして512×512にリサイズ
    feathered = _feather_mask(mask)
    proc_mask = feathered.resize((512, 512), Image.LANCZOS)

    generator = torch.Generator(device=device)
    if seed >= 0:
        generator.manual_seed(seed)

    progress_cb(
        f"生成中… {steps}steps / CFG:{guidance_scale} / "
        f"{'seed:'+str(seed) if seed >= 0 else 'random'}"
    )
    result = pipe(
        prompt=full_prompt,
        negative_prompt=full_neg,
        image=proc_image,
        mask_image=proc_mask,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        generator=generator,
    ).images[0]

    # 元サイズに戻し、フェザリングマスクで滑らかにブレンド
    result = result.resize((orig_w, orig_h), Image.LANCZOS)
    soft_mask = feathered.resize((orig_w, orig_h), Image.LANCZOS).convert("L")
    base = image.convert("RGBA")
    gen_rgba = result.convert("RGBA")
    alpha = np.array(soft_mask).astype(np.float32)[..., np.newaxis] / 255.0
    blended = (np.array(gen_rgba) * alpha + np.array(base) * (1 - alpha)).astype(np.uint8)
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
        out.putalpha(image.split()[3])
    return out


def inpaint(
    image: Image.Image,
    mask: Image.Image,
    prompt: str = "",
    negative_prompt: str = "",
    steps: int = 30,
    guidance_scale: float = 9.0,
    seed: int = -1,
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
        result = _inpaint_sd(
            image, mask, prompt, negative_prompt,
            steps, guidance_scale, seed, _progress,
        )
    else:
        if not is_diffusers_available():
            _progress("diffusers 未インストール → OpenCV フォールバック")
        elif not is_model_cached():
            _progress("SDモデル未キャッシュ → OpenCV フォールバック")
        elif not prompt:
            _progress("プロンプト未入力 → OpenCV フォールバック")
        result = _inpaint_opencv(image, mask, _progress)

    return result, time.perf_counter() - t0
