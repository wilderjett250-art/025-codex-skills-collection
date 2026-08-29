#!/usr/bin/env python3
"""Cull and prepare retouching tasks for a folder of photos.

The default workflow scores images with explicit quality criteria, selects the
best candidates, and creates CosKit-inspired Codex imagegen tasks. Local
retouching engines remain available as fallbacks, but the high-quality portrait
beauty pass is expected to be produced by Codex imagegen in the conversation.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
SKILL_DIR = Path(__file__).resolve().parents[1]
CODEX_GENERATED_IMAGES_ROOT = Path.home() / ".codex" / "generated_images"


@dataclass
class PhotoScore:
    path: str
    filename: str
    width: int
    height: int
    sharpness: float
    exposure: float
    contrast: float
    color: float
    composition: float
    portrait: float
    retouch_potential: float
    total: float
    selected: bool = False
    output_file: str = ""
    engine: str = "baseline"
    decision: str = ""
    reasons: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select the best photos in a folder and prepare retouching outputs or Codex imagegen tasks.")
    parser.add_argument("input_folder", type=Path, help="Folder containing source images.")
    parser.add_argument("--keep-count", type=int, default=None, help="Exact number of images to keep.")
    parser.add_argument("--keep-ratio", type=float, default=0.2, help="Ratio of images to keep when keep-count is omitted.")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum total score required for selection.")
    parser.add_argument("--max-keep", type=int, default=30, help="Maximum images to keep when keep-count is omitted.")
    parser.add_argument("--filter", choices=["natural", "clean", "beauty", "warm", "cool", "film"], default="beauty")
    parser.add_argument("--beauty-strength", type=float, default=0.78, help="Visible portrait beautification strength from 0 to 1.")
    parser.add_argument("--output-name", default="output", help="Output folder name created in the input folder parent.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the output folder instead of making a timestamped run.")
    parser.add_argument("--quality", type=int, default=94, help="JPEG quality for edited outputs.")
    parser.add_argument(
        "--cull-engine",
        choices=["auto", "baseline", "shuttersift"],
        default="baseline",
        help="Default baseline works without optional engines; use shuttersift after installing optional engines.",
    )
    parser.add_argument(
        "--retouch-engine",
        choices=["auto", "baseline", "onnx-skin", "codex-imagegen"],
        default="codex-imagegen",
        help="Default creates Codex imagegen tasks; use baseline/onnx-skin only for fully local weak retouching.",
    )
    parser.add_argument(
        "--shuttersift-dir",
        type=Path,
        default=SKILL_DIR / "external" / "ShutterSift",
        help="Local ShutterSift repository path.",
    )
    parser.add_argument("--shuttersift-keep-threshold", type=int, default=70)
    parser.add_argument("--shuttersift-reject-threshold", type=int, default=40)
    parser.add_argument("--shuttersift-mode", choices=["lite", "cli"], default="lite")
    parser.add_argument("--shuttersift-timeout", type=int, default=180, help="Seconds before ShutterSift is treated as unavailable.")
    parser.add_argument("--jobs", type=int, default=4, help="Parallel jobs for external culling engines.")
    parser.add_argument(
        "--skin-model-dir",
        type=Path,
        default=SKILL_DIR / "external" / "skin-retouching-onnxruntime",
        help="Directory containing skin-retouching ONNX runtime and model files.",
    )
    parser.add_argument("--retouch-degree", type=float, default=0.7)
    parser.add_argument("--whitening-degree", type=float, default=0.8)
    parser.add_argument("--enable-local-blemish", action="store_true")
    parser.add_argument(
        "--imagegen-style",
        choices=["natural", "clean", "beauty", "film"],
        default="beauty",
        help="CosKit-inspired style target for Codex imagegen tasks.",
    )
    return parser.parse_args()


def iter_images(folder: Path) -> Iterable[Path]:
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def load_rgb(path: Path, max_side: int | None = None) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image).convert("RGB")
    if max_side:
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return image


def exif_orientation(path: Path) -> int | None:
    try:
        with Image.open(path) as image:
            return image.getexif().get(274)
    except Exception:
        return None


def match_source_orientation(image: Image.Image, source_path: Path) -> Image.Image:
    source = load_rgb(source_path)
    if image.size == source.size:
        return image
    if image.size != (source.height, source.width):
        return image

    orientation = exif_orientation(source_path)
    if orientation == 3:
        return image.rotate(180, expand=True)
    if orientation == 6:
        return image.rotate(270, expand=True)
    if orientation == 8:
        return image.rotate(90, expand=True)
    return image


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score_peak(value: float, target: float, tolerance: float) -> float:
    return clamp(100.0 - abs(value - target) / tolerance * 100.0)


def compute_sharpness(gray: np.ndarray) -> float:
    if cv2 is not None:
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(lap.var())
    else:
        shifted_x = np.diff(gray.astype(np.float32), axis=1)
        shifted_y = np.diff(gray.astype(np.float32), axis=0)
        variance = float((shifted_x.var() + shifted_y.var()) / 2.0)
    return clamp(math.log1p(max(variance, 0.0)) / math.log1p(1200.0) * 100.0)


def compute_exposure(gray: np.ndarray) -> float:
    mean = float(gray.mean()) / 255.0
    clipped_dark = float((gray < 8).mean())
    clipped_light = float((gray > 247).mean())
    base = score_peak(mean, 0.52, 0.42)
    return clamp(base - (clipped_dark + clipped_light) * 140.0)


def compute_contrast(gray: np.ndarray) -> float:
    p5, p95 = np.percentile(gray, [5, 95])
    spread = (float(p95) - float(p5)) / 255.0
    return clamp(score_peak(spread, 0.55, 0.45))


def compute_color(rgb: np.ndarray) -> float:
    rgb_float = rgb.astype(np.float32) / 255.0
    maxc = rgb_float.max(axis=2)
    minc = rgb_float.min(axis=2)
    saturation = float((maxc - minc).mean())
    sat_score = score_peak(saturation, 0.22, 0.24)
    channel_means = rgb_float.reshape(-1, 3).mean(axis=0)
    balance_penalty = float(np.std(channel_means)) * 180.0
    return clamp(sat_score - balance_penalty)


def compute_composition(gray: np.ndarray) -> float:
    h, w = gray.shape
    if h < 16 or w < 16:
        return 20.0
    edges = np.abs(np.gradient(gray.astype(np.float32))[0]) + np.abs(np.gradient(gray.astype(np.float32))[1])
    total = float(edges.sum()) + 1e-6
    yy, xx = np.indices(gray.shape)
    cx = float((xx * edges).sum() / total) / max(w - 1, 1)
    cy = float((yy * edges).sum() / total) / max(h - 1, 1)
    center_score = 100.0 - (abs(cx - 0.5) + abs(cy - 0.48)) * 135.0
    border = max(4, int(min(h, w) * 0.04))
    border_energy = (
        edges[:border, :].sum() + edges[-border:, :].sum() + edges[:, :border].sum() + edges[:, -border:].sum()
    ) / total
    border_score = 100.0 - float(border_energy) * 280.0
    return clamp(center_score * 0.65 + border_score * 0.35)


def detect_faces(rgb: np.ndarray) -> int:
    if cv2 is None:
        return 0
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        return 0
    detector = cv2.CascadeClassifier(str(cascade_path))
    faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(32, 32))
    return len(faces)


def skin_signal(rgb: np.ndarray) -> float:
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    mask = (r > 70) & (g > 40) & (b > 25) & (r > g) & (g > b) & ((r - g) > 8) & ((r - b) > 18)
    ratio = float(mask.mean())
    return clamp(score_peak(ratio, 0.16, 0.20))


def compute_portrait(rgb: np.ndarray) -> float:
    faces = detect_faces(rgb)
    face_score = 88.0 if faces == 1 else 70.0 if faces > 1 else 46.0
    return clamp(face_score * 0.55 + skin_signal(rgb) * 0.45)


def score_image(path: Path) -> PhotoScore:
    image = load_rgb(path, max_side=1280)
    rgb = np.asarray(image)
    gray = np.asarray(image.convert("L"))
    sharpness = compute_sharpness(gray)
    exposure = compute_exposure(gray)
    contrast = compute_contrast(gray)
    color = compute_color(rgb)
    composition = compute_composition(gray)
    portrait = compute_portrait(rgb)
    severe_failure = min(sharpness, exposure)
    retouch_potential = clamp(50.0 + severe_failure * 0.5)
    total = (
        sharpness * 0.22
        + exposure * 0.18
        + contrast * 0.12
        + color * 0.15
        + composition * 0.18
        + portrait * 0.10
        + retouch_potential * 0.05
    )
    return PhotoScore(
        path=str(path),
        filename=path.name,
        width=image.width,
        height=image.height,
        sharpness=round(sharpness, 2),
        exposure=round(exposure, 2),
        contrast=round(contrast, 2),
        color=round(color, 2),
        composition=round(composition, 2),
        portrait=round(portrait, 2),
        retouch_potential=round(retouch_potential, 2),
        total=round(clamp(total), 2),
        engine="baseline",
    )


def baseline_score_images(image_paths: list[Path]) -> tuple[list[PhotoScore], list[dict[str, str]]]:
    scores: list[PhotoScore] = []
    failed: list[dict[str, str]] = []
    for path in image_paths:
        try:
            scores.append(score_image(path))
        except Exception as exc:
            failed.append({"path": str(path), "error": str(exc)})
    return scores, failed


def load_module_from_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def detect_face_bboxes_normalized(rgb: np.ndarray) -> list[tuple[float, float, float, float]]:
    if cv2 is None:
        return []
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        return []
    detector = cv2.CascadeClassifier(str(cascade_path))
    faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(32, 32))
    h, w = gray.shape
    return [(float(x) / w, float(y) / h, float(x + fw) / w, float(y + fh) / h) for x, y, fw, fh in faces]


def score_with_shuttersift_lite(image_paths: list[Path], shuttersift_dir: Path) -> list[PhotoScore]:
    if cv2 is None:
        raise RuntimeError("OpenCV is required for ShutterSift lite scoring.")
    analyzer_dir = shuttersift_dir / "src" / "shuttersift" / "engine" / "analyzers"
    sharpness_mod = load_module_from_file("shuttersift_lite_sharpness", analyzer_dir / "sharpness.py")
    exposure_mod = load_module_from_file("shuttersift_lite_exposure", analyzer_dir / "exposure.py")
    composition_mod = load_module_from_file("shuttersift_lite_composition", analyzer_dir / "composition.py")

    scores: list[PhotoScore] = []
    for path in image_paths:
        image_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image_bgr is None:
            continue
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        sharpness = float(sharpness_mod.sharpness_score(image_bgr))
        exposure = float(exposure_mod.exposure_score(image_bgr))
        face_bboxes = detect_face_bboxes_normalized(image_rgb)
        composition = float(composition_mod.composition_score(image_bgr, face_bboxes))
        face_quality = 82.0 if len(face_bboxes) == 1 else 72.0 if len(face_bboxes) > 1 else 55.0
        aesthetic = compute_color(image_rgb) * 0.45 + compute_contrast(cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)) * 0.35 + composition * 0.20
        total = sharpness * 0.30 + exposure * 0.15 + aesthetic * 0.25 + face_quality * 0.20 + composition * 0.10
        decision = "keep" if total >= 70 else "reject" if total < 40 else "review"
        h, w = image_bgr.shape[:2]
        scores.append(
            PhotoScore(
                path=str(path),
                filename=path.name,
                width=w,
                height=h,
                sharpness=round(sharpness, 2),
                exposure=round(exposure, 2),
                contrast=round(aesthetic, 2),
                color=round(aesthetic, 2),
                composition=round(composition, 2),
                portrait=round(face_quality, 2),
                retouch_potential=round(clamp((total + face_quality) / 2.0), 2),
                total=round(clamp(total), 2),
                engine="shuttersift-lite",
                decision=decision,
                reasons="ShutterSift lite: sharpness/exposure/composition formulas with local portrait heuristic",
            )
        )
    if not scores:
        raise RuntimeError("ShutterSift lite returned no scored photos.")
    return scores


def score_with_shuttersift_cli(
    input_folder: Path,
    output_dir: Path,
    shuttersift_dir: Path,
    keep_threshold: int,
    reject_threshold: int,
    jobs: int,
    timeout: int,
) -> list[PhotoScore]:
    source_dir = shuttersift_dir / "src"
    cli_file = source_dir / "shuttersift" / "cli" / "main.py"
    if not cli_file.exists():
        raise FileNotFoundError(f"ShutterSift CLI not found: {cli_file}")

    engine_output = output_dir / "_engine_shuttersift"
    env = dict(**os_environ_with_pythonpath(source_dir))
    cmd = [
        sys.executable,
        "-c",
        "from shuttersift.cli.main import app; app()",
        "scan",
        str(input_folder),
        "-o",
        str(engine_output),
        "--keep",
        str(keep_threshold),
        "--reject",
        str(reject_threshold),
        "-j",
        str(jobs),
        "-f",
    ]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(shuttersift_dir),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"ShutterSift exceeded {timeout}s without completing") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"ShutterSift failed: {detail[:1200]}")

    results_path = engine_output / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"ShutterSift did not write results.json: {results_path}")

    data = json.loads(results_path.read_text(encoding="utf-8"))
    scores: list[PhotoScore] = []
    for item in data.get("photos", []):
        path = Path(item["path"])
        try:
            image = load_rgb(path, max_side=64)
            width, height = image.width, image.height
        except Exception:
            width, height = 0, 0
        sub = item.get("sub_scores", {})
        score = float(item.get("score", 0.0))
        aesthetic = float(sub.get("aesthetic", 0.0))
        face_quality = float(sub.get("face_quality", 0.0))
        scores.append(
            PhotoScore(
                path=str(path),
                filename=path.name,
                width=width,
                height=height,
                sharpness=round(float(sub.get("sharpness", 0.0)), 2),
                exposure=round(float(sub.get("exposure", 0.0)), 2),
                contrast=round(aesthetic, 2),
                color=round(aesthetic, 2),
                composition=round(float(sub.get("composition", 0.0)), 2),
                portrait=round(face_quality, 2),
                retouch_potential=round(clamp((score + face_quality) / 2.0), 2),
                total=round(clamp(score), 2),
                engine="shuttersift",
                decision=str(item.get("decision", "")),
                reasons="; ".join(str(reason) for reason in item.get("reasons", [])),
            )
        )
    if not scores:
        raise RuntimeError("ShutterSift returned no scored photos.")
    return scores


def os_environ_with_pythonpath(extra: Path) -> dict[str, str]:
    import os

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(extra) if not existing else f"{extra}:{existing}"
    return env


def score_images(
    input_folder: Path,
    image_paths: list[Path],
    output_dir: Path,
    args: argparse.Namespace,
) -> tuple[list[PhotoScore], list[dict[str, str]], str, str]:
    if args.cull_engine in ("auto", "shuttersift"):
        try:
            shuttersift_dir = args.shuttersift_dir.expanduser().resolve()
            if args.shuttersift_mode == "cli":
                scores = score_with_shuttersift_cli(
                    input_folder=input_folder,
                    output_dir=output_dir,
                    shuttersift_dir=shuttersift_dir,
                    keep_threshold=args.shuttersift_keep_threshold,
                    reject_threshold=args.shuttersift_reject_threshold,
                    jobs=args.jobs,
                    timeout=args.shuttersift_timeout,
                )
                return scores, [], "shuttersift-cli", ""
            scores = score_with_shuttersift_lite(image_paths, shuttersift_dir)
            return scores, [], "shuttersift-lite", ""
        except Exception as exc:
            if args.cull_engine == "shuttersift":
                raise
            warning = str(exc)
            scores, failed = baseline_score_images(image_paths)
            return scores, failed, "baseline", f"ShutterSift unavailable, used baseline: {warning}"

    scores, failed = baseline_score_images(image_paths)
    return scores, failed, "baseline", ""


def choose_scores(scores: list[PhotoScore], keep_count: int | None, keep_ratio: float, max_keep: int, min_score: float) -> list[PhotoScore]:
    ranked = sorted(scores, key=lambda item: item.total, reverse=True)
    if keep_count is None:
        keep_count = max(1, min(max_keep, math.ceil(len(scores) * keep_ratio)))
    keep_count = max(1, min(len(scores), keep_count))
    selected = [score for score in ranked if score.total >= min_score][:keep_count]
    if not selected:
        selected = ranked[:1]
    selected_paths = {score.path for score in selected}
    for score in scores:
        score.selected = score.path in selected_paths
    return selected


def gray_world_white_balance(image: Image.Image) -> Image.Image:
    arr = np.asarray(image).astype(np.float32)
    means = arr.reshape(-1, 3).mean(axis=0)
    gray = float(means.mean())
    scale = gray / np.maximum(means, 1.0)
    balanced = np.clip(arr * scale, 0, 255).astype(np.uint8)
    return Image.fromarray(balanced, "RGB")


def smooth_skin(image: Image.Image) -> Image.Image:
    if cv2 is None:
        return image.filter(ImageFilter.SMOOTH_MORE)
    rgb = np.asarray(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    mask = cv2.inRange(ycrcb, np.array([40, 135, 85]), np.array([235, 180, 135]))
    mask = cv2.GaussianBlur(mask, (0, 0), 5)
    softened = cv2.bilateralFilter(bgr, d=9, sigmaColor=55, sigmaSpace=55)
    alpha = (mask.astype(np.float32) / 255.0)[:, :, None] * 0.42
    mixed = (softened.astype(np.float32) * alpha + bgr.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(mixed, cv2.COLOR_BGR2RGB), "RGB")


def apply_filter(image: Image.Image, preset: str, strength: float = 0.78) -> Image.Image:
    strength = max(0.0, min(1.0, float(strength)))
    if preset == "clean":
        image = ImageEnhance.Brightness(image).enhance(1.04)
        image = ImageEnhance.Color(image).enhance(0.96)
        return ImageEnhance.Contrast(image).enhance(1.07)
    if preset == "beauty":
        image = ImageEnhance.Brightness(image).enhance(1.0 + 0.08 * strength)
        image = ImageEnhance.Contrast(image).enhance(1.0 + 0.08 * strength)
        image = ImageEnhance.Color(image).enhance(1.0 + 0.12 * strength)
        arr = np.asarray(image).astype(np.float32) / 255.0
        gamma = 1.0 - 0.10 * strength
        arr = np.power(np.clip(arr, 0.0, 1.0), gamma)
        arr = arr * 255.0 + np.array([5.0, 2.0, -1.0], dtype=np.float32) * strength
        polished = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        soft = polished.filter(ImageFilter.GaussianBlur(radius=0.65 + 0.55 * strength))
        polished = Image.blend(polished, soft, 0.10 * strength)
        return ImageEnhance.Sharpness(polished).enhance(1.0 + 0.10 * strength)
    if preset == "warm":
        arr = np.asarray(image).astype(np.float32)
        arr[:, :, 0] *= 1.04
        arr[:, :, 1] *= 1.01
        arr[:, :, 2] *= 0.96
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    if preset == "cool":
        arr = np.asarray(image).astype(np.float32)
        arr[:, :, 0] *= 0.97
        arr[:, :, 1] *= 1.00
        arr[:, :, 2] *= 1.05
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    if preset == "film":
        image = ImageEnhance.Contrast(image).enhance(0.96)
        image = ImageEnhance.Color(image).enhance(0.88)
        arr = np.asarray(image).astype(np.float32)
        arr = arr * 0.97 + np.array([8.0, 6.0, 2.0], dtype=np.float32)
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    return image


def retouch_image(path: Path, preset: str, beauty_strength: float = 0.78) -> Image.Image:
    image = load_rgb(path)
    image = gray_world_white_balance(image)
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Brightness(image).enhance(1.03)
    image = ImageEnhance.Contrast(image).enhance(1.06)
    image = ImageEnhance.Color(image).enhance(1.05)
    image = smooth_skin(image)
    image = apply_filter(image, preset, beauty_strength)
    image = ImageEnhance.Sharpness(image).enhance(1.16)
    return image


def skin_onnx_ready(model_dir: Path, enable_local: bool) -> tuple[bool, list[str]]:
    required = ["model.onnx", "retouch_generator.onnx", "face_detector.onnx"]
    if enable_local:
        required += ["local_detection.onnx", "local_inpainting.onnx"]
    missing = [name for name in required if not (model_dir / name).exists()]
    runtime = model_dir / "retouch_onnx.py"
    if not runtime.exists():
        missing.append("retouch_onnx.py")
    return not missing, missing


def retouch_with_onnx_skin(path: Path, temp_output: Path, args: argparse.Namespace) -> None:
    model_dir = args.skin_model_dir.expanduser().resolve()
    ready, missing = skin_onnx_ready(model_dir, args.enable_local_blemish)
    if not ready:
        raise FileNotFoundError(f"skin-retouching ONNX files missing: {', '.join(missing)}")

    cmd = [
        sys.executable,
        str(model_dir / "retouch_onnx.py"),
        "--input",
        str(path),
        "--output",
        str(temp_output),
        "--model-dir",
        str(model_dir),
        "--retouch-degree",
        str(args.retouch_degree),
        "--whitening-degree",
        str(args.whitening_degree),
    ]
    if args.enable_local_blemish:
        cmd.append("--enable-local")
    env = os_environ_with_pythonpath(model_dir)
    completed = subprocess.run(cmd, cwd=str(model_dir), env=env, text=True, capture_output=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"skin-retouching ONNX failed: {detail[:1200]}")
    if not temp_output.exists():
        raise RuntimeError("skin-retouching ONNX did not write output image.")


def coskit_codex_imagegen_prompt(style: str = "beauty") -> str:
    style_hint = {
        "natural": "自然真实、轻微优化，像专业摄影师交付的干净原片后期。",
        "clean": "清透干净、肤色明亮、背景通透，适合生活写真和社交平台发布。",
        "beauty": "高级女生写真美化，肤质干净通透，色彩温柔鲜明，整体明显比原图更精致。",
        "film": "自然胶片写真风格，柔和高光、轻微颗粒、温暖但不偏色。",
    }.get(style, "高级女生写真美化，肤质干净通透。")

    return f"""你是一位专业的人像摄影后期修图师。请基于原图进行自然高级的人像美化，保持人物身份、五官、发型、服装、姿态、背景和构图不变，不要重绘成另一个人。

修图风格：{style_hint}

按 CosKit 的专业修图流程处理：
1. 影调调整：压住过曝高光，提亮面部阴影，保留立体光影和衣服细节。
2. 色彩风格化：白平衡更干净，天空和背景更通透，花草色彩更鲜明但不过饱和，肤色保持自然。
3. 细节增强：眼神更清晰，头发和服装边缘自然，整体锐度适中，不要产生硬锐化光晕。
4. 磨皮美肤：淡化痘印、斑点、毛孔和暗沉，但保留真实皮肤纹理，避免塑料感。
5. 美白提亮：均匀提亮面部和可见皮肤，让肤色更通透，但不能死白。
6. 人脸调整：只允许极轻微优化气色和精神感，必须保留本人辨识度，不要改脸型到不像本人。

禁止：
- 不要改变人物身份、脸型特征、衣服、背景、姿势、画面比例。
- 不要添加文字、水印、边框或多余装饰。
- 不要过度磨皮、不要夸张网红滤镜。
- 不要把照片变成插画、CG、AI写真或另一个场景。

输出：只返回修好后的图片。"""


def write_codex_imagegen_tasks(output_dir: Path, tasks: list[dict[str, object]]) -> None:
    (output_dir / "imagegen_tasks.json").write_text(
        json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Codex Imagegen Tasks",
        "",
        "CosKit is used for workflow and prompt structure only.",
        "Do not call CosKit's Gemini/OpenAI image APIs for these tasks.",
        "For every task below, Codex must inspect the source image and invoke its own imagegen image-editing capability.",
        f"Generated images are normally saved under `{CODEX_GENERATED_IMAGES_ROOT}/`; use `scripts/finalize_imagegen_outputs.py` to copy them into `edited/`.",
        "",
    ]
    for index, task in enumerate(tasks, start=1):
        lines.extend(
            [
                f"## Task {index}",
                "",
                f"- source: {task['source_image']}",
                f"- expected output: {task['expected_output']}",
                f"- score: {task['score']}",
                "",
                "Prompt:",
                "",
                "```text",
                str(task["prompt"]),
                "```",
                "",
            ]
        )
    (output_dir / "imagegen_instructions.md").write_text("\n".join(lines), encoding="utf-8")


def retouch_selected_image(path: Path, preset: str, edited_target: Path, args: argparse.Namespace) -> tuple[str, str]:
    if args.retouch_engine == "codex-imagegen":
        return "codex-imagegen", "Imagegen task generated; final image must be produced by Codex imagegen."

    if args.retouch_engine in ("auto", "onnx-skin"):
        temp_output = edited_target.with_suffix(".onnx.png")
        try:
            retouch_with_onnx_skin(path, temp_output, args)
            image = load_rgb(temp_output)
            image = match_source_orientation(image, path)
            temp_output.unlink(missing_ok=True)
            image = apply_filter(image, preset, args.beauty_strength)
            image = ImageEnhance.Sharpness(image).enhance(1.10)
            image.save(edited_target, quality=args.quality, optimize=True)
            return "onnx-skin", ""
        except Exception as exc:
            temp_output.unlink(missing_ok=True)
            if args.retouch_engine == "onnx-skin":
                raise
            image = retouch_image(path, preset, args.beauty_strength)
            image.save(edited_target, quality=args.quality, optimize=True)
            return "baseline", f"ONNX skin retouch unavailable, used baseline: {exc}"

    image = retouch_image(path, preset, args.beauty_strength)
    image.save(edited_target, quality=args.quality, optimize=True)
    return "baseline", ""


def make_output_dir(input_folder: Path, output_name: str, overwrite: bool) -> Path:
    base = input_folder.parent / output_name
    if overwrite:
        if base.exists():
            shutil.rmtree(base)
        base.mkdir(parents=True)
        return base
    if not base.exists():
        base.mkdir(parents=True)
        return base
    run_dir = base / datetime.now().strftime("run-%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True)
    return run_dir


def safe_stem(path: Path) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "_" for char in path.stem)


def write_score_report(path: Path, scores: list[PhotoScore]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(scores[0]).keys()))
        writer.writeheader()
        for score in sorted(scores, key=lambda item: item.total, reverse=True):
            writer.writerow(asdict(score))


def make_contact_sheet(images: list[Path], output_path: Path) -> None:
    if not images:
        return
    thumbs: list[Image.Image] = []
    for path in images[:30]:
        img = load_rgb(path)
        img.thumbnail((360, 360), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (360, 360), "white")
        canvas.paste(img, ((360 - img.width) // 2, (360 - img.height) // 2))
        thumbs.append(canvas)
    cols = min(5, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 360, rows * 360), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 360, (index // cols) * 360))
    sheet.save(output_path, quality=90)


def main() -> int:
    args = parse_args()
    input_folder = args.input_folder.expanduser().resolve()
    if not input_folder.exists() or not input_folder.is_dir():
        print(f"Input folder does not exist: {input_folder}", file=sys.stderr)
        return 2

    image_paths = list(iter_images(input_folder))
    if not image_paths:
        print(f"No supported images found in: {input_folder}", file=sys.stderr)
        return 2

    output_dir = make_output_dir(input_folder, args.output_name, args.overwrite)
    edited_dir = output_dir / "edited"
    originals_dir = output_dir / "selected_originals"
    edited_dir.mkdir(parents=True, exist_ok=True)
    originals_dir.mkdir(parents=True, exist_ok=True)

    scores, failed, cull_engine_used, cull_warning = score_images(input_folder, image_paths, output_dir, args)

    if not scores:
        print("All images failed to load.", file=sys.stderr)
        return 1

    selected = choose_scores(scores, args.keep_count, args.keep_ratio, args.max_keep, args.min_score)
    edited_paths: list[Path] = []
    retouch_engines_used: set[str] = set()
    retouch_warnings: list[str] = []
    imagegen_tasks: list[dict[str, object]] = []
    for rank, score in enumerate(selected, start=1):
        src = Path(score.path)
        name = f"{rank:03d}_{int(round(score.total)):02d}_{safe_stem(src)}.jpg"
        original_target = originals_dir / src.name
        edited_target = edited_dir / name
        shutil.copy2(src, original_target)
        if args.retouch_engine == "codex-imagegen":
            task = {
                "rank": rank,
                "source_image": str(original_target),
                "original_source_image": str(src),
                "expected_output": str(edited_target),
                "score": score.total,
                "filter": args.imagegen_style,
                "coskit_basis": ["tone_adjust", "color_style", "detail_enhance", "skin_smooth", "skin_whiten", "face_adjust"],
                "prompt": coskit_codex_imagegen_prompt(args.imagegen_style),
            }
            imagegen_tasks.append(task)
            retouch_engine_used = "codex-imagegen"
            retouch_warning = "Task generated only; Codex imagegen must create the final image."
        else:
            retouch_engine_used, retouch_warning = retouch_selected_image(src, args.filter, edited_target, args)
            edited_paths.append(edited_target)
        retouch_engines_used.add(retouch_engine_used)
        if retouch_warning and retouch_warning not in retouch_warnings:
            retouch_warnings.append(retouch_warning)
        score.output_file = str(edited_target)

    write_score_report(output_dir / "score_report.csv", scores)
    if imagegen_tasks:
        write_codex_imagegen_tasks(output_dir, imagegen_tasks)
    make_contact_sheet(edited_paths if edited_paths else [Path(task["source_image"]) for task in imagegen_tasks], output_dir / "contact_sheet.jpg")

    manifest = {
        "input_folder": str(input_folder),
        "output_folder": str(output_dir),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "filter": args.filter,
        "imagegen_style": args.imagegen_style,
        "codex_generated_images_root": str(CODEX_GENERATED_IMAGES_ROOT),
        "cull_engine_requested": args.cull_engine,
        "cull_engine_used": cull_engine_used,
        "cull_warning": cull_warning,
        "retouch_engine_requested": args.retouch_engine,
        "retouch_engines_used": sorted(retouch_engines_used),
        "retouch_warnings": retouch_warnings,
        "imagegen_tasks_file": str(output_dir / "imagegen_tasks.json") if imagegen_tasks else "",
        "imagegen_instructions_file": str(output_dir / "imagegen_instructions.md") if imagegen_tasks else "",
        "imagegen_tasks": imagegen_tasks,
        "shuttersift_dir": str(args.shuttersift_dir.expanduser().resolve()),
        "skin_model_dir": str(args.skin_model_dir.expanduser().resolve()),
        "scanned": len(image_paths),
        "scored": len(scores),
        "selected": len(selected),
        "failed": failed,
        "selected_files": [asdict(score) for score in sorted(selected, key=lambda item: item.total, reverse=True)],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"output_folder": str(output_dir), "scanned": len(image_paths), "selected": len(selected)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
