#!/usr/bin/env python
"""Draw which servo id goes where on the robot, for the assembly docs.

The ids come from `code/13_quadruped/include/quad_calib.h` (QUAD_SERVO_ID
and the joint order in the comment above it), not from this file, so the
figure cannot drift from what the firmware addresses. The robot is the MJCF
at its `home` keyframe, seen from above and from the left, and each id is
pinned on the servo body it belongs to by projecting that body's position
through the render camera.

This lives in scripts/ rather than next to the MJCF because code/ is synced
from the manuscript and files that exist only here are deleted by the sync.

Run:  uv run --no-project --with mujoco --with pillow --with numpy \\
          python scripts/render_servo_ids.py

Writes docs/{ja,en}/source/hardware/assembly_img/servo_ids.png.
"""

import argparse
import os
import re
import sys

import mujoco
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER = os.path.join(REPO, "code", "13_quadruped")
MJCF = os.path.join(CHAPTER, "arduino_os_quad_robot", "mjcf", "arduino_os_quad_robot.xml")
CALIB = os.path.join(CHAPTER, "include", "quad_calib.h")
DEFAULT_FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

VIEW_W, VIEW_H = 760, 640
BG = (255, 255, 255)
INK = (33, 37, 41)
SUB = (108, 117, 125)
# One colour per leg, so a badge in the top view and the row in the table
# read as the same leg at a glance.
LEG_COLOR = {
    "FR": (214, 69, 65),
    "FL": (38, 110, 196),
    "RR": (230, 145, 30),
    "RL": (46, 139, 87),
}
LEG_ORDER = ("FR", "FL", "RR", "RL")

TEXT = {
    "ja": {
        "title": "サーボ ID の割り当て",
        "top": "上から見た図",
        "side": "左から見た図",
        "front": "前",
        "hip": "股",
        "knee": "膝",
        "leg": {"FR": "右前 FR", "FL": "左前 FL", "RR": "右後 RR", "RL": "左後 RL"},
        "note": "ID は include/quad_calib.h の QUAD_SERVO_ID と同じ。前 = 歩く向き。",
    },
    "en": {
        "title": "Servo id assignment",
        "top": "Top view",
        "side": "Left side view",
        "front": "Front",
        "hip": "hip",
        "knee": "knee",
        "leg": {
            "FR": "Front right FR",
            "FL": "Front left FL",
            "RR": "Rear right RR",
            "RL": "Rear left RL",
        },
        "note": "Ids match QUAD_SERVO_ID in include/quad_calib.h. Front = walking direction.",
    },
}


def read_servo_ids(path):
    """Read the joint to servo id map from quad_calib.h.

    Parameters
    ----------
    path : str
        Path to quad_calib.h.

    Returns
    -------
    dict of str to int
        Servo id keyed by joint name, e.g. ``{"FL_hip": 3, ...}``.
    """
    with open(path, encoding="utf-8") as f:
        src = f.read()
    order = re.search(r"//\s*バス上の ID。\s*(.+)\n", src)
    ids = re.search(r"QUAD_SERVO_ID\[[^\]]*\]\s*=\s*\{([^}]*)\}", src)
    if order is None or ids is None:
        raise SystemExit(f"could not find QUAD_SERVO_ID and its joint order in {path}")
    names = [n.strip() for n in order.group(1).split(",")]
    values = [int(v) for v in ids.group(1).split(",")]
    if len(names) != len(values):
        raise SystemExit(f"{path}: {len(names)} joint names but {len(values)} ids")
    return dict(zip(names, values, strict=True))


def project(scene, point, width, height):
    """Project a world point to pixel coordinates of the last render.

    Parameters
    ----------
    scene : mujoco.MjvScene
        Scene the image was rendered from.
    point : numpy.ndarray
        World position, shape (3,).
    width, height : int
        Image size in pixels.

    Returns
    -------
    tuple of float
        ``(u, v)`` pixel position, origin top left.
    """
    cams = scene.camera
    pos = (np.array(cams[0].pos) + np.array(cams[1].pos)) / 2
    fwd = np.array(cams[0].forward)
    up = np.array(cams[0].up)
    right = np.cross(fwd, up)
    rel = np.asarray(point) - pos
    depth = rel @ fwd
    near = cams[0].frustum_near
    xn = (rel @ right) * near / depth
    yn = (rel @ up) * near / depth
    # mjv leaves frustum_width at 0; the renderer widens the frustum to the
    # image aspect ratio, so the half width follows from the height.
    half = (cams[0].frustum_top - cams[0].frustum_bottom) / 2 * width / height
    center = cams[0].frustum_center
    u = (xn - (center - half)) / (2 * half) * width
    v = (cams[0].frustum_top - yn) / (cams[0].frustum_top - cams[0].frustum_bottom) * height
    return u, v


def render_view(model, data, renderer, azimuth, elevation, distance, lookat):
    """Render the robot on a white background.

    Returns
    -------
    PIL.Image.Image
        The view, background replaced by white.
    """
    opt = mujoco.MjvOption()
    opt.geomgroup[:] = 0
    opt.geomgroup[2] = 1  # visual meshes only
    cam = mujoco.MjvCamera()
    cam.lookat[:] = lookat
    cam.distance = distance
    cam.azimuth = azimuth
    cam.elevation = elevation
    renderer.update_scene(data, cam, opt)
    rgb = renderer.render().copy()
    renderer.enable_segmentation_rendering()
    renderer.update_scene(data, cam, opt)
    seg = renderer.render()
    renderer.disable_segmentation_rendering()
    rgb[seg[:, :, 0] < 0] = BG
    return Image.fromarray(rgb)


def badge(draw, center, text, color, font, radius):
    """Draw a filled circle with a number in it."""
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=BG, width=3)
    draw.text((x, y), text, font=font, fill=BG, anchor="mm")


def arrow(draw, start, end, color, width=6, head=18):
    """Draw a straight arrow from start to end."""
    start = np.asarray(start, float)
    end = np.asarray(end, float)
    draw.line([tuple(start), tuple(end)], fill=color, width=width)
    d = (end - start) / np.linalg.norm(end - start)
    n = np.array([-d[1], d[0]])
    tip = end + d * head * 0.4
    draw.polygon(
        [
            tuple(tip),
            tuple(end - d * head + n * head * 0.6),
            tuple(end - d * head - n * head * 0.6),
        ],
        fill=color,
    )


def front_arrow(draw, scene, base, font, label, color):
    """Draw a 'front' arrow along the robot's +X in the given view."""
    a = project(scene, base + np.array([0.02, 0, 0]), VIEW_W, VIEW_H)
    b = project(scene, base + np.array([0.06, 0, 0]), VIEW_W, VIEW_H)
    d = np.subtract(b, a)
    d = d / np.linalg.norm(d)
    # Park the arrow in the top left corner, pointing where +X points, with
    # the label just past the tip. Leave room for the label when the arrow
    # points left or up, so it does not run off the edge.
    length = 90
    gap = 16
    label_w = draw.textlength(label, font=font)
    label_h = font.size
    room = np.array([label_w + gap, label_h + gap])
    # A label centred on a vertical arrow needs half its width to the left.
    corner = np.array([max(40.0, label_w / 2 + gap), 40.0])
    origin = corner + np.maximum(-d, 0) * (length + room)
    tip = origin + d * length
    arrow(draw, origin, tip, color)
    if abs(d[0]) >= abs(d[1]):
        anchor = "lm" if d[0] > 0 else "rm"
    else:
        anchor = "mt" if d[1] > 0 else "mb"
    draw.text(tuple(tip + d * gap), label, font=font, fill=color, anchor=anchor)


def compose(lang, model, data, renderer, ids, font_path):
    """Lay out both views and the id table for one language.

    Returns
    -------
    PIL.Image.Image
        The finished figure.
    """
    t = TEXT[lang]
    big = ImageFont.truetype(font_path, 40, index=0)
    mid = ImageFont.truetype(font_path, 28, index=0)
    num = ImageFont.truetype(font_path, 26, index=0)
    small = ImageFont.truetype(font_path, 22, index=0)

    base = data.body("base_link").xpos.copy()
    lookat = base - np.array([0, 0, 0.05])
    views = []
    for key, azimuth, elevation, distance, joints in (
        # Azimuth is the direction the camera looks in: 0 from above puts +X
        # (front) at the top of the image, 270 looks along -Y from the +Y
        # (left) side of the robot.
        ("top", 0.0, -89.9, 0.55, ("hip", "knee")),
        ("side", 270.0, 0.0, 0.5, ("hip", "knee")),
    ):
        img = render_view(model, data, renderer, azimuth, elevation, distance, lookat)
        draw = ImageDraw.Draw(img)
        front_arrow(draw, renderer.scene, base, mid, t["front"], INK)
        for leg in LEG_ORDER:
            if key == "side" and leg in ("FR", "RR"):
                continue  # hidden behind the left legs
            for joint in joints:
                name = f"{leg}_{joint}"
                uv = project(renderer.scene, data.body(f"{name}_servo").xpos, VIEW_W, VIEW_H)
                badge(draw, uv, str(ids[name]), LEG_COLOR[leg], num, 22)
        views.append((t[key], img))

    pad = 40
    table_h = 250
    width = pad * 3 + VIEW_W * 2
    height = 90 + 50 + VIEW_H + table_h
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 30), t["title"], font=big, fill=INK)
    for i, (caption, img) in enumerate(views):
        x = pad + i * (VIEW_W + pad)
        draw.text((x, 100), caption, font=mid, fill=SUB)
        canvas.paste(img, (x, 140))
        draw.rectangle((x, 140, x + VIEW_W - 1, 140 + VIEW_H - 1), outline=(222, 226, 230), width=2)

    y0 = 140 + VIEW_H + 30
    col_w = (width - 2 * pad) // 4
    for i, leg in enumerate(LEG_ORDER):
        x = pad + i * col_w
        draw.rectangle((x, y0, x + 14, y0 + 30), fill=LEG_COLOR[leg])
        draw.text((x + 26, y0 + 15), t["leg"][leg], font=mid, fill=INK, anchor="lm")
        for j, joint in enumerate(("hip", "knee")):
            yy = y0 + 70 + j * 56
            badge(draw, (x + 26, yy), str(ids[f"{leg}_{joint}"]), LEG_COLOR[leg], num, 22)
            draw.text((x + 62, yy), t[joint], font=mid, fill=INK, anchor="lm")
    draw.text((pad, height - 36), t["note"], font=small, fill=SUB, anchor="lm")
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--font", default=DEFAULT_FONT, help="a font with Japanese glyphs (default: %(default)s)"
    )
    args = parser.parse_args()
    if not os.path.exists(args.font):
        raise SystemExit(f"font not found: {args.font}. Pass one with --font.")

    ids = read_servo_ids(CALIB)
    model = mujoco.MjModel.from_xml_path(MJCF)
    model.vis.global_.offwidth = max(model.vis.global_.offwidth, VIEW_W)
    model.vis.global_.offheight = max(model.vis.global_.offheight, VIEW_H)
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    mujoco.mj_forward(model, data)
    renderer = mujoco.Renderer(model, VIEW_H, VIEW_W)

    for lang in ("ja", "en"):
        out = os.path.join(
            REPO, "docs", lang, "source", "hardware", "assembly_img", "servo_ids.png"
        )
        compose(lang, model, data, renderer, ids, args.font).save(out, optimize=True)
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
