#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_nav_previews.py — генератор PNG-прев'ю варіантів навігації Power BI.

Малює один з 7 канонічних варіантів навігаційного меню (V1..V7) як wireframe
сторінки реального розміру канви (масштабований до максимум 1280px по
ширині), з меню промальованим у кольорах палітри звіту та реальними іменами
сторінок (підтримка кирилиці через TTF-шрифт з гліфами кирилиці, за
замовчуванням Segoe UI з C:\\Windows\\Fonts).

Використання:
    python render_nav_previews.py --config config.json
    python render_nav_previews.py --config config.json --variant V3 --out-dir out

config.json:
    {
      "pages": [
        {"name": "Головна сторінка", "width": 1280, "height": 720, "icon": "icons/home.png"},
        ...
      ],
      "palette": {"primary": "#0F3D5C", "accent": "#ECDAB2", "bg": "#FFFFFF",
                   "text": "#202A44", "selected": "#27893E"},
      "font": "Segoe UI",
      "variant": "V1",
      "hero_page": "Головна сторінка",
      "out_dir": "previews",
      "selected_style": "S1",
      "icons": "labeled",
      "groups": [{"name": "Огляд", "pages": ["Головна сторінка", "..."]}, ...]
    }

Кожен запуск малює РІВНО один PNG: out_dir/<variant>.png. variant береться з
config.json (поле "variant") або з --variant, якщо переданий (--variant має
пріоритет). Щоб отримати всі 7 прев'ю, скрипт викликається 7 разів (по одному
на варіант) — так і задумано специфікацією.

Нові опційні поля (зворотно сумісні — старий config.json без них далі працює
без змін):
  selected_style  "S1".."S5" — як позначено активний пункт меню:
                  S1 заливка (дефолт для V1/V4/V5/V7), S2 індикаторна смужка
                  3-4px (дефолт для V2/V3/V6: під вкладкою у V1/V6/V7-стилю
                  чи знизу картки у V4, зліва рядка у V2/V3/V5), S3 лише
                  жирність шрифту, S4 лише колір тексту/іконки, S5 заливка+
                  жирність. Дефолт залежить від варіанта, якщо поле не задане.
  icons           "none"|"labeled"|"only" (дефолт "labeled"). V3 не приймає
                  "none" (це піктограмна рейка за задумом) — примусово
                  "labeled"; V6 (нативний pageNavigator) кастомних іконок не
                  рендерить — значення ігнорується з попередженням у stderr.
  pages[].icon    шлях до PNG цієї сторінки; якщо файл існує — вставляється
                  (resize 20-24px, з прозорістю) замість квадрата-плейсхолдера,
                  інакше плейсхолдер + попередження у stderr.
  groups          [{"name":.., "pages":[назви,...]}] — реальна інформаційна
                  архітектура для V7 (групи + рядок підвкладок) і заголовки
                  секцій у V2/V4. Без цього поля V7 будує синтетичні групи
                  "Розділ N" (як і раніше), а V2/V4 лишаються пласким списком.

Футер кожного PNG містить дрібний підпис із застосованим selected_style та
режимом іконок — для швидкої QA-звірки без відкриття config.json.

Немає зовнішніх мережевих запитів; лише stdlib + Pillow. Exit code: 0 — успіх,
1 — помилка (повідомлення в stderr).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - середовище без Pillow
    sys.stderr.write(
        "[ERROR] Pillow не встановлено. Встановіть: pip install Pillow\n"
        f"[ERROR] {exc}\n"
    )
    sys.exit(1)


# --------------------------------------------------------------------------
# Константи та довідник варіантів
# --------------------------------------------------------------------------

MAX_CANVAS_WIDTH = 1280
HEADER_HEIGHT = 108
FOOTER_HEIGHT = 26
INDICATOR_BAR_THICKNESS = 4

PLACEHOLDER_FILL = (228, 228, 228)
PLACEHOLDER_BORDER = (196, 196, 196)
WHITE = (255, 255, 255)

VALID_SELECTED_STYLES = ("S1", "S2", "S3", "S4", "S5")

# Рекомендований дефолт стилю активного пункту меню за варіантом (якщо
# "selected_style" не заданий у config.json). V1/V4/V5/V7 — заливка (їхня
# історична поведінка); V2/V3/V6 — індикаторна смужка.
DEFAULT_SELECTED_STYLE: dict[str, str] = {
    "V1": "S1",
    "V2": "S2",
    "V3": "S2",
    "V4": "S1",
    "V5": "S1",
    "V6": "S2",
    "V7": "S1",
}

VALID_ICON_MODES = ("none", "labeled", "only")
# "labeled" зберігає історичний вигляд V2 (іконка+підпис) і V3 (іконка+тултіп)
# без змін і додає іконки-плейсхолдери іншим варіантам.
DEFAULT_ICONS_MODE = "labeled"

VARIANTS: dict[str, dict[str, str]] = {
    "V1": {
        "layout": "top-tab-bar",
        "title": "V1 — Верхня панель вкладок (top tab bar)",
        "summary": (
            "Горизонтальна панель pill-вкладок зверху з усіма сторінками; "
            "активна вкладка (hero_page) залита кольором selected, білий текст."
        ),
    },
    "V2": {
        "layout": "left-rail-expanded",
        "title": "V2 — Розгорнута ліва панель (left rail, ~240px)",
        "summary": (
            "Ліва вертикальна панель з іконкою-плейсхолдером і назвою кожної "
            "сторінки; активний пункт підсвічено кольором selected."
        ),
    },
    "V3": {
        "layout": "left-rail-icons",
        "title": "V3 — Вузька ліва панель іконок (~56px)",
        "summary": (
            "Компактна ліва панель лише з іконками-плейсхолдерами; активна "
            "іконка підсвічена, поруч — тултіп-виноска з назвою сторінки."
        ),
    },
    "V4": {
        "layout": "hub-home",
        "title": "V4 — Хаб-сторінка з картками розділів",
        "summary": (
            "Головна сторінка показує сітку карток розділів (2 колонки); "
            "на контентній сторінці — компактна кнопка «Головна» в кутку."
        ),
    },
    "V5": {
        "layout": "hamburger-overlay",
        "title": "V5 — Кнопка-гамбургер з оверлей-панеллю",
        "summary": (
            "Кнопка-гамбургер у кутку відкриває напівпрозорий оверлей зліва "
            "зі списком сторінок поверх контенту (симуляція відкритого стану)."
        ),
    },
    "V6": {
        "layout": "page-navigator",
        "title": "V6 — Нативна стрічка pageNavigator",
        "summary": (
            "Нижня стрічка кнопок-сторінок у стилі нативного візуала "
            "pageNavigator; активна сторінка підсвічена кольором selected."
        ),
    },
    "V7": {
        "layout": "grouped-topbar",
        "title": "V7 — Групована верхня панель",
        "summary": (
            "Верхня панель груп сторінок (3-5 груп); під активною групою — "
            "рядок підвкладок із реальними назвами сторінок цієї групи."
        ),
    },
}


# --------------------------------------------------------------------------
# Дрібні утиліти
# --------------------------------------------------------------------------


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = str(value).strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) != 6:
        raise ValueError(f"Некоректний HEX-колір у палітрі: {value!r}")
    try:
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except ValueError as exc:
        raise ValueError(f"Некоректний HEX-колір у палітрі: {value!r}") from exc


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Лінійна інтерполяція між двома RGB-кольорами (t=0 -> c1, t=1 -> c2)."""
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))  # type: ignore[return-value]


@dataclass(frozen=True)
class Palette:
    primary: tuple[int, int, int]
    accent: tuple[int, int, int]
    bg: tuple[int, int, int]
    text: tuple[int, int, int]
    selected: tuple[int, int, int]

    @classmethod
    def from_config(cls, data: dict) -> "Palette":
        required = ["primary", "accent", "bg", "text", "selected"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"У 'palette' відсутні поля: {', '.join(missing)}")
        return cls(**{k: hex_to_rgb(data[k]) for k in required})


# --------------------------------------------------------------------------
# Шрифти (обов'язкова підтримка кирилиці)
# --------------------------------------------------------------------------

_WIN_FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"

# Найменування -> (regular, bold) файли в C:\Windows\Fonts.
_FONT_NAME_MAP: dict[str, tuple[str, str]] = {
    "segoe ui": ("segoeui.ttf", "segoeuib.ttf"),
    "segoeui": ("segoeui.ttf", "segoeuib.ttf"),
    "arial": ("arial.ttf", "arialbd.ttf"),
    "calibri": ("calibri.ttf", "calibrib.ttf"),
    "tahoma": ("tahoma.ttf", "tahomabd.ttf"),
    "verdana": ("verdana.ttf", "verdanab.ttf"),
}

# Ланцюжок фолбеків, якщо запитаний шрифт не знайдено (усі мають кирилицю на Windows).
_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("segoeui.ttf", "segoeuib.ttf"),
    ("arial.ttf", "arialbd.ttf"),
    ("tahoma.ttf", "tahomabd.ttf"),
    ("calibri.ttf", "calibrib.ttf"),
    ("verdana.ttf", "verdanab.ttf"),
    ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),  # може бути відсутнім — це нормально
]


class FontBundle:
    """Кешує TTF-шрифти за (розмір, bold) і гарантує graceful fallback."""

    def __init__(self, font_name: Optional[str]):
        self.reg_path, self.bold_path, self.used_family, self.warning = self._resolve(font_name)
        self._cache: dict[tuple[int, bool], "ImageFont.FreeTypeFont | ImageFont.ImageFont"] = {}

    @staticmethod
    def _resolve(font_name: Optional[str]):
        candidates: list[tuple[Path, Path]] = []

        # 1) Явний шлях до .ttf/.otf у config["font"].
        if font_name:
            p = Path(font_name)
            if p.suffix.lower() in {".ttf", ".otf"} and p.is_file():
                candidates.append((p, p))

        # 2) Відоме ім'я шрифту -> файли в C:\Windows\Fonts.
        key = (font_name or "").strip().lower()
        if key in _FONT_NAME_MAP:
            reg, bold = _FONT_NAME_MAP[key]
            candidates.append((_WIN_FONTS_DIR / reg, _WIN_FONTS_DIR / bold))

        # 3) Ланцюжок фолбеків (Segoe UI першим, тоді інші системні, тоді DejaVu).
        for reg, bold in _FALLBACK_CHAIN:
            candidates.append((_WIN_FONTS_DIR / reg, _WIN_FONTS_DIR / bold))

        for reg_path, bold_path in candidates:
            if Path(reg_path).is_file():
                bold_final = Path(bold_path) if Path(bold_path).is_file() else Path(reg_path)
                return Path(reg_path), bold_final, Path(reg_path).name, None

        warning = (
            "Жодного TTF-шрифту з кирилицею не знайдено (перевірено запитаний шрифт, "
            "C:\\Windows\\Fonts\\segoeui.ttf та фолбеки). Використано вбудований "
            "бітмаповий шрифт Pillow — українські назви можуть відображатись як "
            "порожні прямокутники."
        )
        return None, None, None, warning

    def get(self, size: int, bold: bool = False):
        size = max(6, int(round(size)))
        key = (size, bold)
        if key in self._cache:
            return self._cache[key]
        path = self.bold_path if (bold and self.bold_path) else self.reg_path
        if path is None:
            try:
                font = ImageFont.load_default(size=size)
            except TypeError:
                font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(str(path), size)
        self._cache[key] = font
        return font


# --------------------------------------------------------------------------
# Текстові утиліти
# --------------------------------------------------------------------------


def _text_bbox(draw: "ImageDraw.ImageDraw", text: str, font) -> tuple[int, int, int, int]:
    if not text:
        return (0, 0, 0, 0)
    return draw.textbbox((0, 0), text, font=font)


def text_size(draw: "ImageDraw.ImageDraw", text: str, font) -> tuple[int, int]:
    bbox = _text_bbox(draw, text, font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text(draw: "ImageDraw.ImageDraw", pos: tuple[float, float], text: str, font, fill) -> None:
    if not text:
        return
    x, y = pos
    bbox = _text_bbox(draw, text, font)
    draw.text((x - bbox[0], y - bbox[1]), text, font=font, fill=fill)


def fit_text(draw: "ImageDraw.ImageDraw", text: str, font, max_width: float) -> str:
    """Обрізає текст з «…», якщо він не влазить у max_width."""
    if max_width <= 0 or not text:
        return ""
    if draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    if draw.textlength(ellipsis, font=font) > max_width:
        return ""
    lo, hi = 0, len(text)
    best = ellipsis
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = text[:mid].rstrip() + ellipsis
        if draw.textlength(candidate, font=font) <= max_width:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_text_in_box(
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    text: str,
    font,
    fill,
    align: str = "left",
    valign: str = "middle",
    padding: float = 6,
) -> tuple[int, int]:
    x0, y0, x1, y1 = box
    avail_w = (x1 - x0) - 2 * padding
    text = fit_text(draw, text, font, avail_w)
    if not text:
        return (0, 0)
    w, h = text_size(draw, text, font)
    if align == "left":
        x = x0 + padding
    elif align == "center":
        x = x0 + ((x1 - x0) - w) / 2
    else:  # right
        x = x1 - padding - w
    if valign == "top":
        y = y0 + padding
    elif valign == "bottom":
        y = y1 - padding - h
    else:  # middle
        y = y0 + ((y1 - y0) - h) / 2
    draw_text(draw, (x, y), text, font, fill)
    return (w, h)


# --------------------------------------------------------------------------
# Плейсхолдери контенту (2-3 сірих прямокутники «візуалів»)
# --------------------------------------------------------------------------


def draw_placeholder_rect(draw: "ImageDraw.ImageDraw", box: tuple[float, float, float, float]) -> None:
    x0, y0, x1, y1 = box
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    draw.rectangle((x0, y0, x1, y1), fill=PLACEHOLDER_FILL, outline=PLACEHOLDER_BORDER, width=2)


def draw_placeholders(
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    palette: Palette,
    fonts: FontBundle,
    header_text: Optional[str] = None,
) -> None:
    x0, y0, x1, y1 = box
    pad = clamp((x1 - x0) * 0.025, 10, 22)
    cx0, cy0, cx1, cy1 = x0 + pad, y0 + pad, x1 - pad, y1 - pad
    if cx1 <= cx0 or cy1 <= cy0:
        return

    if header_text:
        title_font = fonts.get(clamp((cx1 - cx0) * 0.028, 15, 21), bold=True)
        draw_text(draw, (cx0, cy0), header_text, title_font, palette.text)
        _, th = text_size(draw, header_text, title_font)
        cy0 += th + pad

    total_h = cy1 - cy0
    if total_h <= 20:
        return

    gap = pad
    top_h = round(total_h * 0.56)
    rect1 = (cx0, cy0, cx1, cy0 + top_h)
    draw_placeholder_rect(draw, rect1)

    y2 = cy0 + top_h + gap
    bottom_h = cy1 - y2
    if bottom_h > 24 and (cx1 - cx0) > 60:
        half_w = (cx1 - cx0 - gap) / 2
        draw_placeholder_rect(draw, (cx0, y2, cx0 + half_w, cy1))
        draw_placeholder_rect(draw, (cx0 + half_w + gap, y2, cx1, cy1))


# --------------------------------------------------------------------------
# Дрібні піктограми (щоб не залежати від гліфів ⌂/☰, яких може не бути у TTF)
# --------------------------------------------------------------------------


def draw_home_icon(draw: "ImageDraw.ImageDraw", x0: float, y0: float, size: float, color) -> None:
    w = size
    roof = [(x0, y0 + w * 0.55), (x0 + w * 0.5, y0), (x0 + w, y0 + w * 0.55)]
    draw.polygon(roof, fill=color)
    base_box = (x0 + w * 0.22, y0 + w * 0.5, x0 + w * 0.78, y0 + w * 0.96)
    draw.rectangle(base_box, fill=color)


def draw_hamburger_icon(draw: "ImageDraw.ImageDraw", x0: float, y0: float, size: float, color) -> None:
    pad = size * 0.22
    thickness = max(2, round(size * 0.09))
    xs0, xs1 = x0 + pad, x0 + size - pad
    for frac in (0.28, 0.5, 0.72):
        y = y0 + size * frac
        draw.line([(xs0, y), (xs1, y)], fill=color, width=thickness)


# --------------------------------------------------------------------------
# PNG-іконки сторінок (pages[].icon) з graceful fallback на плейсхолдер
# --------------------------------------------------------------------------


class IconCache:
    """Відкриває/масштабує PNG-іконки сторінок і кешує результат.

    Відсутній чи нечитний файл не є фатальною помилкою: повертається None
    (виклик-сайт малює плейсхолдер-квадрат), а попередження в stderr
    друкується один раз на шлях, щоб не спамити при повторному використанні
    тієї самої іконки на кількох рядках/вкладках.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], "Optional[Image.Image]"] = {}
        self._warned: set[str] = set()

    def get(self, path_str: Optional[str], size: float) -> "Optional[Image.Image]":
        if not path_str:
            return None
        size_i = max(1, round(size))
        key = (path_str, size_i)
        if key in self._cache:
            return self._cache[key]

        p = Path(path_str)
        icon_img: Optional["Image.Image"]
        if not p.is_file():
            if path_str not in self._warned:
                sys.stderr.write(f"[WARN] Файл іконки не знайдено: {path_str} — використано плейсхолдер.\n")
                self._warned.add(path_str)
            icon_img = None
        else:
            try:
                src = Image.open(p).convert("RGBA")
                icon_img = src.resize((size_i, size_i), Image.LANCZOS)
            except Exception as exc:  # noqa: BLE001 - будь-яка помилка іконки не має валити рендер
                if path_str not in self._warned:
                    sys.stderr.write(f"[WARN] Не вдалося відкрити іконку {path_str}: {exc} — використано плейсхолдер.\n")
                    self._warned.add(path_str)
                icon_img = None
        self._cache[key] = icon_img
        return icon_img


def draw_item_content(
    img: "Image.Image",
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    page: dict,
    icons_mode: str,
    icons: IconCache,
    icon_size: float,
    icon_color,
    text_color,
    font,
    align: str = "left",
) -> None:
    """Малює вміст пункту меню (іконка та/або назва сторінки) за icons_mode.

    "none" — лише текст (як і до появи цієї опції); "labeled" — іконка+текст;
    "only" — лише іконка. Реальний PNG (page['icon']) вставляється зі
    збереженням прозорості; інакше — квадрат-плейсхолдер кольору icon_color.
    `img` — зображення, у яке фактично вставляється PNG-іконка (може бути
    окремим RGBA-шаром, напр. оверлеєм V5, а не лише головним полотном).
    """
    x0, y0, x1, y1 = box
    show_icon = icons_mode in ("labeled", "only")
    show_text = icons_mode in ("none", "labeled") or not show_icon
    name = page["name"]
    icon_img = icons.get(page.get("icon"), icon_size) if show_icon else None

    def place_icon(icon_x: float) -> None:
        icon_y = (y0 + y1 - icon_size) / 2
        if icon_img is not None:
            img.paste(icon_img, (round(icon_x), round(icon_y)), icon_img)
        else:
            draw.rectangle((icon_x, icon_y, icon_x + icon_size, icon_y + icon_size), outline=icon_color, width=2)

    if show_icon and show_text:
        gap = 8
        if align == "center":
            avail_w = max(0.0, (x1 - x0) - 2 * gap - icon_size - gap)
            fitted = fit_text(draw, name, font, avail_w)
            text_w, _ = text_size(draw, fitted, font)
            total_w = icon_size + gap + text_w
            start_x = x0 + max(gap, ((x1 - x0) - total_w) / 2)
            place_icon(start_x)
            text_box = (start_x + icon_size + gap, y0, x1 - gap, y1)
            draw_text_in_box(draw, text_box, name, font, text_color, align="left", valign="middle")
        elif align == "right":
            icon_x = x1 - gap - icon_size
            place_icon(icon_x)
            draw_text_in_box(draw, (x0 + gap, y0, icon_x - gap, y1), name, font, text_color, align="right", valign="middle")
        else:  # left
            icon_x = x0 + gap
            place_icon(icon_x)
            draw_text_in_box(draw, (icon_x + icon_size + gap, y0, x1 - gap, y1), name, font, text_color, align="left", valign="middle")
    elif show_icon:
        place_icon((x0 + x1 - icon_size) / 2)
    else:
        draw_text_in_box(draw, box, name, font, text_color, align=align, valign="middle")


# --------------------------------------------------------------------------
# Стилі виділення активного пункту меню (selected_style S1..S5)
# --------------------------------------------------------------------------


def resolve_active_style(style: str, selected: tuple[int, int, int], base_text: tuple[int, int, int], base_icon: Optional[tuple[int, int, int]] = None) -> dict:
    """Вигляд активного пункту для «табів/рядків» (pill, rail row, segment).

    fill  — колір заливки фону (None => фон лишається як у неактивного);
    text/icon — колір тексту/іконки активного пункту;
    bold  — чи використовувати жирний шрифт;
    bar   — чи малювати тонку (3-4px) індикаторну смужку кольору selected;
            саме позиціювання смужки (знизу таба, зліва рядка тощо) визначає
            виклик-сайт, бо воно залежить від форми елемента.
    """
    base_icon = base_text if base_icon is None else base_icon
    if style == "S1":
        return {"fill": selected, "text": WHITE, "icon": WHITE, "bold": False, "bar": False}
    if style == "S2":
        return {"fill": None, "text": base_text, "icon": base_icon, "bold": False, "bar": True}
    if style == "S3":
        return {"fill": None, "text": base_text, "icon": base_icon, "bold": True, "bar": False}
    if style == "S4":
        return {"fill": None, "text": selected, "icon": selected, "bold": False, "bar": False}
    if style == "S5":
        return {"fill": selected, "text": WHITE, "icon": WHITE, "bold": True, "bar": False}
    raise ValueError(f"Невідомий selected_style: {style!r}. Дозволені: {', '.join(VALID_SELECTED_STYLES)}.")


def card_active_style(style: str, palette: "Palette") -> dict:
    """Вигляд активної картки V4 — картка не має «заливки-як-у-таба», тому
    мапінг стилів виражено у власній візуальній мові карток (рамка/стрічка/
    легкий тон/жирність підпису), але з тим самим набором з 5 сигналів."""
    if style == "S1":
        return {"border": palette.selected, "border_w": 3, "top_bar": False, "tint": False, "bold": False, "label": palette.selected}
    if style == "S2":
        return {"border": palette.primary, "border_w": 2, "top_bar": True, "tint": False, "bold": False, "label": palette.text}
    if style == "S3":
        return {"border": palette.primary, "border_w": 2, "top_bar": False, "tint": False, "bold": True, "label": palette.text}
    if style == "S4":
        return {"border": palette.primary, "border_w": 2, "top_bar": False, "tint": False, "bold": False, "label": palette.selected}
    if style == "S5":
        return {"border": palette.selected, "border_w": 3, "top_bar": False, "tint": True, "bold": True, "label": palette.selected}
    raise ValueError(f"Невідомий selected_style: {style!r}. Дозволені: {', '.join(VALID_SELECTED_STYLES)}.")


@dataclass
class RenderContext:
    """Пакує все, що потрібно варіантам V1..V7 для малювання одного PNG."""

    pages: list[dict]
    pages_by_name: dict[str, dict]
    palette: "Palette"
    hero: str
    fonts: "FontBundle"
    style: str
    icons_mode: str
    icons: IconCache
    groups: Optional[list[dict]]  # [{"name":.., "pages":[назви,...]}] або None


# --------------------------------------------------------------------------
# Заголовна смужка PNG (назва варіанта + суть + легенда палітри)
# --------------------------------------------------------------------------


def draw_header(
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    variant_key: str,
    palette: Palette,
    fonts: FontBundle,
) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=palette.primary)
    meta = VARIANTS[variant_key]
    pad = 18

    title_font = fonts.get(23, bold=True)
    draw_text(draw, (x0 + pad, y0 + 14), meta["title"], title_font, WHITE)

    desc_font = fonts.get(14)
    desc_color = mix(palette.accent, WHITE, 0.25)
    draw_text_in_box(
        draw,
        (x0 + pad, y0 + 46, x1 - pad, y0 + 46 + 24),
        meta["summary"],
        desc_font,
        desc_color,
        align="left",
        valign="top",
        padding=0,
    )

    # Легенда палітри (QA-допомога): 5 квадратів праворуч знизу заголовка.
    swatches = [
        ("primary", palette.primary),
        ("accent", palette.accent),
        ("selected", palette.selected),
        ("text", palette.text),
        ("bg", palette.bg),
    ]
    sw = 13
    label_font = fonts.get(9)
    slot_w = 74
    block_w = len(swatches) * slot_w
    lx = x1 - pad - block_w
    ly = y1 - 26
    for name, color in swatches:
        draw.rectangle((lx, ly, lx + sw, ly + sw), fill=color, outline=WHITE, width=1)
        draw_text(draw, (lx + sw + 4, ly - 1), name, label_font, WHITE)
        lx += slot_w


def draw_footer(
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    ctx: RenderContext,
    palette: "Palette",
) -> None:
    """Дрібний QA-підпис знизу PNG: застосований selected_style, режим
    іконок і чи використано реальні groups (вимога — щоб не відкривати
    config.json, аби зрозуміти, з якими параметрами відрендерено прев'ю)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=mix(palette.primary, palette.bg, 0.88))
    draw.line([(x0, y0), (x1, y0)], fill=palette.primary, width=1)
    font = ctx.fonts.get(11)
    groups_note = "реальні groups" if ctx.groups else "синтетичні групи (лише V7)"
    caption = f"selected_style: {ctx.style}   ·   icons: {ctx.icons_mode}   ·   {groups_note}"
    draw_text_in_box(draw, (x0 + 12, y0, x1 - 12, y1), caption, font, palette.text, align="left", valign="middle", padding=0)


# --------------------------------------------------------------------------
# V1 — верхня панель pill-вкладок
# --------------------------------------------------------------------------


def draw_v1(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    bar_h = clamp((y1 - y0) * 0.11, 48, 74)
    draw.rectangle((x0, y0, x1, y0 + bar_h), fill=palette.primary)

    pad = 10
    pages = ctx.pages
    n = max(len(pages), 1)
    avail_w = (x1 - x0) - pad * (n + 1)
    pill_w = max(64, avail_w / n)
    pill_h = bar_h - 14
    icon_size = 18
    font_size = clamp(bar_h * 0.30, 12, 17)

    x = x0 + pad
    for page in pages:
        if x >= x1 - pad:
            break
        active = page["name"] == ctx.hero
        box = (x, y0 + 7, min(x + pill_w, x1 - pad), y0 + 7 + pill_h)
        if active:
            st = resolve_active_style(ctx.style, palette.selected, palette.primary)
            fill = st["fill"] if st["fill"] is not None else palette.accent
            textfill, iconfill, bold = st["text"], st["icon"], st["bold"]
        else:
            fill, textfill, iconfill, bold = palette.accent, palette.primary, palette.primary, False
        draw.rounded_rectangle(box, radius=pill_h / 2, fill=fill)
        font = ctx.fonts.get(font_size, bold=bold)
        draw_item_content(img, draw, box, page, ctx.icons_mode, ctx.icons, icon_size, iconfill, textfill, font, align="center")
        if active and st["bar"]:
            by = box[3] + 2
            draw.rectangle((box[0] + 6, by, box[2] - 6, min(by + INDICATOR_BAR_THICKNESS, y0 + bar_h - 1)), fill=palette.selected)
        x += pill_w + pad

    draw_placeholders(draw, (x0, y0 + bar_h, x1, y1), palette, ctx.fonts, header_text=ctx.hero)


# --------------------------------------------------------------------------
# V2 — розгорнута ліва панель
# --------------------------------------------------------------------------


def draw_v2(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    rail_w = clamp((x1 - x0) * 0.19, 170, 240)
    draw.rectangle((x0, y0, x0 + rail_w, y1), fill=palette.primary)

    icon_size = 18

    # Без "groups" — один блок без заголовка (плаский список, як і раніше).
    if ctx.groups:
        blocks = [(g["name"], [ctx.pages_by_name[n] for n in g["pages"] if n in ctx.pages_by_name]) for g in ctx.groups]
        blocks = [(gname, gp) for gname, gp in blocks if gp]
    else:
        blocks = [(None, ctx.pages)]

    total_pages = sum(len(gp) for _, gp in blocks) or 1
    n_headers = sum(1 for gname, _ in blocks if gname is not None)
    header_h = 24
    avail_h = (y1 - y0 - 16) - n_headers * header_h
    row_h = clamp(avail_h / total_pages, 32, 58)
    font_size = clamp(row_h * 0.32, 12, 16)
    header_font = ctx.fonts.get(12, bold=True)
    header_color = mix(palette.accent, WHITE, 0.15)

    y = y0 + 8
    for gname, gp in blocks:
        if y >= y1:
            break
        if gname is not None:
            draw_text(draw, (x0 + 14, y + 4), gname.upper(), header_font, header_color)
            y += header_h
        for page in gp:
            if y >= y1:
                break
            active = page["name"] == ctx.hero
            row_box = (x0, y, x0 + rail_w, min(y + row_h, y1))
            if active:
                st = resolve_active_style(ctx.style, palette.selected, palette.accent)
                if st["fill"] is not None:
                    draw.rectangle(row_box, fill=st["fill"])
                textfill, iconfill, bold = st["text"], st["icon"], st["bold"]
            else:
                textfill, iconfill, bold = palette.accent, palette.accent, False
            font = ctx.fonts.get(font_size, bold=bold)
            content_box = (x0 + 14, row_box[1], x0 + rail_w - 8, row_box[3])
            draw_item_content(img, draw, content_box, page, ctx.icons_mode, ctx.icons, icon_size, iconfill, textfill, font, align="left")
            if active and st["bar"]:
                draw.rectangle((x0, row_box[1], x0 + INDICATOR_BAR_THICKNESS, row_box[3]), fill=palette.selected)
            y += row_h

    draw_placeholders(draw, (x0 + rail_w, y0, x1, y1), palette, ctx.fonts, header_text=ctx.hero)


# --------------------------------------------------------------------------
# V3 — вузька ліва панель іконок + тултіп
# --------------------------------------------------------------------------


def draw_v3(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    rail_w = clamp((x1 - x0) * 0.045, 48, 64)
    draw.rectangle((x0, y0, x0 + rail_w, y1), fill=palette.primary)

    pages = ctx.pages
    n = max(len(pages), 1)
    row_h = clamp((y1 - y0 - 16) / n, 42, 62)
    icon_size = 22
    y = y0 + 8
    hero_row_box = None
    for page in pages:
        if y >= y1:
            break
        active = page["name"] == ctx.hero
        row_box = (x0, y, x0 + rail_w, min(y + row_h, y1))
        if active:
            st = resolve_active_style(ctx.style, palette.selected, palette.accent)
            if st["fill"] is not None:
                draw.rectangle(row_box, fill=st["fill"])
            iconfill = st["icon"]
            hero_row_box = row_box
            if st["bar"]:
                draw.rectangle((x0, row_box[1], x0 + INDICATOR_BAR_THICKNESS, row_box[3]), fill=palette.selected)
        else:
            iconfill = palette.accent
        cx = x0 + rail_w / 2
        cy = y + row_h / 2
        icon_img = ctx.icons.get(page.get("icon"), icon_size)
        if icon_img is not None:
            img.paste(icon_img, (round(cx - icon_size / 2), round(cy - icon_size / 2)), icon_img)
        else:
            icon_box = (cx - icon_size / 2, cy - icon_size / 2, cx + icon_size / 2, cy + icon_size / 2)
            draw.rounded_rectangle(icon_box, radius=4, outline=iconfill, width=2)
        y += row_h

    # Контент малюється першим — тултіп floating-виноска йде поверх нього,
    # інакше заголовок сторінки й текст тултіпа перекриваються (нечитабельно).
    draw_placeholders(draw, (x0 + rail_w, y0, x1, y1), palette, ctx.fonts, header_text=ctx.hero)

    # icons_mode="only" -> чиста піктограмна рейка без жодного тексту, навіть
    # без тултіпа активної сторінки (icons_mode вже примусово labeled/only
    # для V3 — див. resolve_icons_mode).
    if hero_row_box is not None and ctx.icons_mode != "only":
        ry0, ry1 = hero_row_box[1], hero_row_box[3]
        cy = (ry0 + ry1) / 2
        font = ctx.fonts.get(14)
        hero = ctx.hero
        tw = draw.textlength(hero, font=font)
        pad = 10
        box_w = min(tw + 2 * pad, (x1 - x0) * 0.5)
        tip_x0 = x0 + rail_w + 8
        box = (tip_x0, cy - 15, tip_x0 + box_w, cy + 15)
        # вказівник тултіпа
        draw.polygon(
            [(tip_x0, cy - 6), (tip_x0, cy + 6), (tip_x0 - 8, cy)],
            fill=palette.accent,
            outline=palette.primary,
        )
        draw.rounded_rectangle(box, radius=6, fill=palette.accent, outline=palette.primary)
        draw_text_in_box(draw, box, hero, font, palette.primary, align="center", valign="middle")


# --------------------------------------------------------------------------
# V4 — хаб-сторінка (2 кадри в одному PNG, поділ по вертикалі)
# --------------------------------------------------------------------------


def draw_hub_card(
    img: "Image.Image",
    draw: "ImageDraw.ImageDraw",
    box: tuple[float, float, float, float],
    page: dict,
    active: bool,
    ctx: RenderContext,
    label_font_size: float,
) -> None:
    cx0, cy0, cx1, cy1 = box
    palette = ctx.palette
    if active:
        cs = card_active_style(ctx.style, palette)
        border_color, border_w = cs["border"], cs["border_w"]
        label_color, bold, top_bar = cs["label"], cs["bold"], cs["top_bar"]
        fill = mix(palette.selected, palette.bg, 0.85) if cs["tint"] else palette.bg
    else:
        border_color, border_w, label_color, bold, fill, top_bar = palette.primary, 2, palette.text, False, palette.bg, False

    draw.rounded_rectangle((cx0, cy0, cx1, cy1), radius=8, fill=fill, outline=border_color, width=border_w)

    inner_pad = 8
    label_h = 22
    label_top = cy1 - label_h - 4
    vis_box = (cx0 + inner_pad, cy0 + inner_pad, cx1 - inner_pad, label_top - 4)
    if vis_box[3] > vis_box[1]:
        draw_placeholder_rect(draw, vis_box)

    if top_bar:
        draw.rectangle((cx0 + 6, cy0, cx1 - 6, cy0 + INDICATOR_BAR_THICKNESS), fill=palette.selected)

    label_box = (cx0 + inner_pad, label_top, cx1 - inner_pad, cy1 - 4)
    font = ctx.fonts.get(label_font_size, bold=bold)
    icon_size = 16
    draw_item_content(img, draw, label_box, page, ctx.icons_mode, ctx.icons, icon_size, label_color, label_color, font, align="left")


def draw_v4(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    mid = y0 + round((y1 - y0) * 0.54)
    pad = 16

    # --- Кадр 1: хаб з сіткою карток розділів (за групами, якщо задані) ---
    header_font = ctx.fonts.get(19, bold=True)
    draw_text(draw, (x0 + pad, y0 + 10), "Головна — розділи звіту", header_font, palette.text)
    _, th = text_size(draw, "Hg", header_font)
    grid_y0 = y0 + 10 + th + pad

    cols = 2
    gap = 14
    card_w = (x1 - x0 - 2 * pad - gap * (cols - 1)) / cols

    if ctx.groups:
        blocks = [(g["name"], [ctx.pages_by_name[n] for n in g["pages"] if n in ctx.pages_by_name]) for g in ctx.groups]
        blocks = [(gname, gp) for gname, gp in blocks if gp]
    else:
        blocks = [(None, ctx.pages)]

    group_header_h = 22
    group_header_font = ctx.fonts.get(14, bold=True)
    total_card_rows = sum(math.ceil(len(gp) / cols) for _, gp in blocks) or 1
    n_headers = sum(1 for gname, _ in blocks if gname is not None)
    available = mid - grid_y0 - pad - gap * max(total_card_rows - 1, 0) - group_header_h * n_headers
    card_h = max(46.0, available / total_card_rows)
    label_font_size = clamp(card_h * 0.15, 12, 16)

    y_cursor = grid_y0
    for gname, gp in blocks:
        # невеликий допуск проти похибки округлення float
        if y_cursor > mid - pad + 0.75:
            break
        if gname is not None:
            draw_text(draw, (x0 + pad, y_cursor + 2), gname, group_header_font, palette.primary)
            y_cursor += group_header_h
        for i, page in enumerate(gp):
            r, c = divmod(i, cols)
            cx0 = x0 + pad + c * (card_w + gap)
            cy0 = y_cursor + r * (card_h + gap)
            cx1 = cx0 + card_w
            cy1 = cy0 + card_h
            if cy1 > mid - pad + 0.75 or cy0 >= mid - pad:
                continue
            active = page["name"] == ctx.hero
            draw_hub_card(img, draw, (cx0, cy0, cx1, cy1), page, active, ctx, label_font_size)
        rows_here = math.ceil(len(gp) / cols)
        y_cursor += rows_here * (card_h + gap)

    # --- роздільник ---
    draw.line([(x0, mid), (x1, mid)], fill=palette.primary, width=2)
    caption_font = ctx.fonts.get(12)
    draw_text(draw, (x0 + 8, mid + 4), "Контентна сторінка (приклад):", caption_font, palette.text)

    # --- Кадр 2: контентна сторінка з кнопкою «Головна» в кутку ---
    content_top = mid + 22
    draw_placeholders(draw, (x0, content_top, x1, y1), palette, ctx.fonts, header_text=ctx.hero)

    btn_w, btn_h = 136, 34
    bx0 = x1 - btn_w - 16
    by0 = content_top + 10
    draw.rounded_rectangle((bx0, by0, bx0 + btn_w, by0 + btn_h), radius=17, fill=palette.accent, outline=palette.primary, width=1)
    icon_size = 16
    draw_home_icon(draw, bx0 + 12, by0 + (btn_h - icon_size) / 2, icon_size, palette.primary)
    btn_font = ctx.fonts.get(13)
    draw_text_in_box(
        draw,
        (bx0 + 12 + icon_size + 6, by0, bx0 + btn_w - 8, by0 + btn_h),
        "Головна",
        btn_font,
        palette.primary,
        align="left",
        valign="middle",
        padding=0,
    )


# --------------------------------------------------------------------------
# V5 — гамбургер + напівпрозорий оверлей
# --------------------------------------------------------------------------


def draw_v5(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    btn = 44
    bx0, by0 = x0 + 14, y0 + 14
    draw.rounded_rectangle((bx0, by0, bx0 + btn, by0 + btn), radius=8, fill=palette.primary)
    draw_hamburger_icon(draw, bx0, by0, btn, WHITE)

    header_font = ctx.fonts.get(18, bold=True)
    draw_text_in_box(
        draw,
        (bx0 + btn + 14, by0, x1 - 16, by0 + btn),
        ctx.hero,
        header_font,
        palette.text,
        align="left",
        valign="middle",
        padding=0,
    )

    content_top = by0 + btn + 18
    draw_placeholders(draw, (x0, content_top, x1, y1), palette, ctx.fonts, header_text=None)

    # напівпрозорий оверлей зліва (симуляція відкритого стану)
    overlay_w = max(160, round((x1 - x0) * 0.38))
    overlay_h = y1 - y0
    overlay = Image.new("RGBA", (overlay_w, overlay_h), palette.primary + (218,))
    odraw = ImageDraw.Draw(overlay)
    pad = 16
    # Заголовок оверлею йде нижче кнопки-гамбургера (та малюється поверх
    # оверлею в img-координатах) — інакше текст і кнопка накладаються.
    title_top = btn + 14 + 16
    title_font = ctx.fonts.get(16, bold=True)
    draw_text(odraw, (pad, title_top), "Сторінки звіту", title_font, WHITE)

    pages = ctx.pages
    n = max(len(pages), 1)
    list_top = title_top + 34
    row_h = clamp((overlay_h - list_top - pad) / n, 34, 52)
    font_size = 13
    icon_size = 18
    y = list_top
    for page in pages:
        if y >= overlay_h - pad:
            break
        active = page["name"] == ctx.hero
        row_box = (0, y, overlay_w, min(y + row_h, overlay_h))
        if active:
            st = resolve_active_style(ctx.style, palette.selected, WHITE)
            if st["fill"] is not None:
                odraw.rectangle(row_box, fill=st["fill"] + (255,))
            textfill, iconfill, bold = st["text"], st["icon"], st["bold"]
            if st["bar"]:
                odraw.rectangle((0, row_box[1], INDICATOR_BAR_THICKNESS, row_box[3]), fill=palette.selected + (255,))
        else:
            textfill, iconfill, bold = (255, 255, 255, 235), (255, 255, 255), False
        font = ctx.fonts.get(font_size, bold=bold)
        content_box = (pad, row_box[1], overlay_w - pad, row_box[3])
        draw_item_content(overlay, odraw, content_box, page, ctx.icons_mode, ctx.icons, icon_size, iconfill, textfill, font, align="left")
        y += row_h

    img.paste(overlay, (x0, y0), overlay)

    # гамбургер-кнопка залишається видимою поверх оверлею
    draw2 = ImageDraw.Draw(img)
    draw2.rounded_rectangle((bx0, by0, bx0 + btn, by0 + btn), radius=8, fill=palette.primary)
    draw_hamburger_icon(draw2, bx0, by0, btn, WHITE)


# --------------------------------------------------------------------------
# V6 — нативний pageNavigator (нижня стрічка)
# --------------------------------------------------------------------------


def draw_v6(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    bar_h = clamp((y1 - y0) * 0.09, 40, 56)
    draw_placeholders(draw, (x0, y0, x1, y1 - bar_h), palette, ctx.fonts, header_text=ctx.hero)

    bar_top = y1 - bar_h
    draw.line([(x0, bar_top), (x1, bar_top)], fill=palette.primary, width=2)

    pages = ctx.pages
    n = max(len(pages), 1)
    seg_w = (x1 - x0) / n
    font_size = clamp(bar_h * 0.30, 11, 15)
    # Резервуємо 8px знизу сегмента (замість 4px) — там же, за потреби,
    # малюється індикаторна смужка S2 "під вкладкою".
    for i, page in enumerate(pages):
        active = page["name"] == ctx.hero
        seg_box = (x0 + i * seg_w + 2, bar_top + 4, x0 + (i + 1) * seg_w - 2, y1 - 8)
        if active:
            st = resolve_active_style(ctx.style, palette.selected, palette.primary)
            fill = st["fill"] if st["fill"] is not None else palette.accent
            textfill, bold = st["text"], st["bold"]
        else:
            fill, textfill, bold = palette.accent, palette.primary, False
        draw.rectangle(seg_box, fill=fill, outline=palette.primary, width=1)
        font = ctx.fonts.get(font_size, bold=bold)
        draw_text_in_box(draw, seg_box, page["name"], font, textfill, align="center", valign="middle", padding=6)
        if active and st["bar"]:
            draw.rectangle((seg_box[0] + 4, y1 - 6, seg_box[2] - 4, y1 - 2), fill=palette.selected)
    # V6 не рендерить кастомні PNG-іконки — ctx.icons_mode тут завжди "none"
    # (примусово, див. resolve_icons_mode: нативний pageNavigator їх не підтримує).


# --------------------------------------------------------------------------
# V7 — групована верхня панель + рядок підвкладок
# --------------------------------------------------------------------------


def group_count(n: int) -> int:
    if n <= 0:
        return 0
    if n < 3:
        return n
    return int(clamp(math.ceil(n / 2), 3, 5))


def chunk_pages(pages: list[dict], g: int) -> list[list[dict]]:
    if g <= 0:
        return []
    n = len(pages)
    base, rem = divmod(n, g)
    groups: list[list[dict]] = []
    idx = 0
    for i in range(g):
        size = base + (1 if i < rem else 0)
        groups.append(pages[idx: idx + size])
        idx += size
    return [grp for grp in groups if grp]


def draw_v7(img: "Image.Image", region, ctx: RenderContext) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = region
    palette = ctx.palette
    draw.rectangle(region, fill=palette.bg)

    if ctx.groups:
        # Реальна ІА з config.json: групи + сторінки саме в заданому порядку.
        groups = [
            {"name": g["name"], "pages": [ctx.pages_by_name[n] for n in g["pages"] if n in ctx.pages_by_name]}
            for g in ctx.groups
        ]
        groups = [g for g in groups if g["pages"]]
    else:
        chunked = chunk_pages(ctx.pages, group_count(len(ctx.pages)))
        if not chunked:
            chunked = [ctx.pages]
        groups = [{"name": f"Розділ {i + 1}", "pages": grp} for i, grp in enumerate(chunked)]

    active_gi = next((i for i, g in enumerate(groups) if any(p["name"] == ctx.hero for p in g["pages"])), 0)

    bar1_h = clamp((y1 - y0) * 0.09, 42, 58)
    bar2_h = clamp((y1 - y0) * 0.075, 36, 50)

    draw.rectangle((x0, y0, x1, y0 + bar1_h), fill=palette.primary)
    ng = max(len(groups), 1)
    seg_w = (x1 - x0) / ng
    font1_size = clamp(bar1_h * 0.30, 13, 17)
    for i, g in enumerate(groups):
        active = i == active_gi
        box = (x0 + i * seg_w + 3, y0 + 6, x0 + (i + 1) * seg_w - 3, y0 + bar1_h - 6)
        if active:
            st = resolve_active_style(ctx.style, palette.selected, palette.primary)
            fill = st["fill"] if st["fill"] is not None else palette.accent
            textfill, bold = st["text"], st["bold"]
        else:
            fill, textfill, bold = palette.accent, palette.primary, False
        draw.rounded_rectangle(box, radius=6, fill=fill)
        font1 = ctx.fonts.get(font1_size, bold=bold)
        draw_text_in_box(draw, box, g["name"], font1, textfill, align="center", valign="middle")
        if active and st["bar"]:
            by = box[3] + 2
            draw.rectangle((box[0] + 4, by, box[2] - 4, min(by + INDICATOR_BAR_THICKNESS, y0 + bar1_h - 1)), fill=palette.selected)

    sub_y0 = y0 + bar1_h
    draw.rectangle((x0, sub_y0, x1, sub_y0 + bar2_h), fill=mix(palette.accent, WHITE, 0.45))
    sub_pages = groups[active_gi]["pages"] if groups else []
    m = max(len(sub_pages), 1)
    sub_w = (x1 - x0) / m
    font2_size = clamp(bar2_h * 0.32, 11, 15)
    icon_size = 16
    for i, page in enumerate(sub_pages):
        active = page["name"] == ctx.hero
        box = (x0 + i * sub_w + 3, sub_y0 + 5, x0 + (i + 1) * sub_w - 3, sub_y0 + bar2_h - 5)
        if active:
            st = resolve_active_style(ctx.style, palette.selected, palette.primary)
            if st["fill"] is not None:
                draw.rounded_rectangle(box, radius=5, fill=st["fill"])
            else:
                draw.rounded_rectangle(box, radius=5, outline=palette.primary, width=1)
            textfill, iconfill, bold = st["text"], st["icon"], st["bold"]
        else:
            draw.rounded_rectangle(box, radius=5, outline=palette.primary, width=1)
            textfill, iconfill, bold = palette.primary, palette.primary, False
        font2 = ctx.fonts.get(font2_size, bold=bold)
        draw_item_content(img, draw, box, page, ctx.icons_mode, ctx.icons, icon_size, iconfill, textfill, font2, align="center")
        if active and st["bar"]:
            by = box[3] + 2
            draw.rectangle((box[0] + 4, by, box[2] - 4, min(by + INDICATOR_BAR_THICKNESS, sub_y0 + bar2_h - 1)), fill=palette.selected)

    draw_placeholders(draw, (x0, sub_y0 + bar2_h, x1, y1), palette, ctx.fonts, header_text=None)


DISPATCH = {
    "V1": draw_v1,
    "V2": draw_v2,
    "V3": draw_v3,
    "V4": draw_v4,
    "V5": draw_v5,
    "V6": draw_v6,
    "V7": draw_v7,
}


# --------------------------------------------------------------------------
# Конфігурація та рендер
# --------------------------------------------------------------------------


def load_config(path_str: str) -> dict:
    path = Path(path_str)
    if not path.is_file():
        raise FileNotFoundError(f"Файл конфігурації не знайдено: {path}")
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Некоректний JSON у {path}: {exc}") from exc


def validate_config(config: dict) -> None:
    pages = config.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("Поле 'pages' має бути непорожнім списком сторінок.")
    for page in pages:
        if not isinstance(page, dict) or "name" not in page or "width" not in page or "height" not in page:
            raise ValueError(f"Кожна сторінка повинна мати name/width/height: {page!r}")
        w, h = page["width"], page["height"]
        if not (isinstance(w, (int, float)) and w > 0 and isinstance(h, (int, float)) and h > 0):
            raise ValueError(f"Некоректні розміри сторінки: {page!r}")
        icon = page.get("icon")
        if icon is not None and not isinstance(icon, str):
            raise ValueError(f"Поле 'icon' сторінки має бути рядком-шляхом до PNG: {page!r}")

    if not isinstance(config.get("palette"), dict):
        raise ValueError("Поле 'palette' відсутнє або має бути об'єктом.")

    hero = config.get("hero_page")
    if not hero:
        raise ValueError("Поле 'hero_page' є обов'язковим.")
    if not any(p["name"] == hero for p in pages):
        raise ValueError(f"hero_page {hero!r} не знайдено серед 'pages'.")


def resolve_selected_style(config: dict, variant_key: str) -> str:
    style = config.get("selected_style") or DEFAULT_SELECTED_STYLE[variant_key]
    if style not in VALID_SELECTED_STYLES:
        raise ValueError(f"Некоректне значення 'selected_style': {style!r}. Дозволені: {', '.join(VALID_SELECTED_STYLES)}.")
    return style


def resolve_icons_mode(config: dict, variant_key: str) -> str:
    mode = config.get("icons", DEFAULT_ICONS_MODE)
    if mode not in VALID_ICON_MODES:
        raise ValueError(f"Некоректне значення 'icons': {mode!r}. Дозволені: {', '.join(VALID_ICON_MODES)}.")
    if variant_key == "V6":
        if "icons" in config and mode != "none":
            sys.stderr.write(
                "[WARN] V6 (нативний pageNavigator) не рендерить кастомні іконки — "
                f"'icons'={mode!r} проігноровано.\n"
            )
        return "none"
    if variant_key == "V3" and mode == "none":
        sys.stderr.write(
            "[WARN] V3 — піктограмна рейка за задумом; 'icons=none' недоступне для V3, "
            "примусово використано 'labeled'.\n"
        )
        return "labeled"
    return mode


def resolve_groups(config: dict, pages: list[dict]) -> Optional[list[dict]]:
    """Валідує опційне поле 'groups'; повертає None, якщо поле не задане
    (тоді V7 будує синтетичні групи, а V2/V4 лишаються пласким списком)."""
    raw = config.get("groups")
    if not raw:
        return None
    if not isinstance(raw, list):
        raise ValueError("Поле 'groups' має бути списком об'єктів {name, pages}.")

    page_names = {p["name"] for p in pages}
    grouped: set[str] = set()
    groups: list[dict] = []
    for g in raw:
        if not isinstance(g, dict) or not g.get("name") or not g.get("pages"):
            raise ValueError(f"Кожна група повинна мати непорожні 'name' і 'pages': {g!r}")
        gpages = g["pages"]
        if not isinstance(gpages, list) or not all(isinstance(n, str) for n in gpages):
            raise ValueError(f"'pages' групи {g['name']!r} має бути списком назв сторінок (рядків).")
        missing = [n for n in gpages if n not in page_names]
        if missing:
            raise ValueError(f"Група {g['name']!r} посилається на сторінки, яких немає у 'pages': {missing}")
        groups.append({"name": g["name"], "pages": list(gpages)})
        grouped.update(gpages)

    ungrouped = [p["name"] for p in pages if p["name"] not in grouped]
    if ungrouped:
        sys.stderr.write(
            "[WARN] Сторінки поза 'groups' не показуються у групованих варіантах "
            f"(V2/V4/V7): {', '.join(ungrouped)}\n"
        )
    return groups


def render(config: dict, variant_key: str, out_path: Path) -> Optional[str]:
    pages = config["pages"]
    hero_name = config["hero_page"]
    hero_page = next(p for p in pages if p["name"] == hero_name)

    palette = Palette.from_config(config["palette"])
    fonts = FontBundle(config.get("font"))
    style = resolve_selected_style(config, variant_key)
    icons_mode = resolve_icons_mode(config, variant_key)
    groups = resolve_groups(config, pages)

    ctx = RenderContext(
        pages=pages,
        pages_by_name={p["name"]: p for p in pages},
        palette=palette,
        hero=hero_name,
        fonts=fonts,
        style=style,
        icons_mode=icons_mode,
        icons=IconCache(),
        groups=groups,
    )

    real_w, real_h = float(hero_page["width"]), float(hero_page["height"])
    scale = min(1.0, MAX_CANVAS_WIDTH / real_w)
    canvas_w = max(1, round(real_w * scale))
    canvas_h = max(1, round(real_h * scale))

    total_w = canvas_w
    total_h = HEADER_HEIGHT + canvas_h + FOOTER_HEIGHT

    img = Image.new("RGB", (total_w, total_h), palette.bg)
    draw = ImageDraw.Draw(img)
    draw_header(draw, (0, 0, total_w, HEADER_HEIGHT), variant_key, palette, fonts)

    region = (0, HEADER_HEIGHT, total_w, HEADER_HEIGHT + canvas_h)
    DISPATCH[variant_key](img, region, ctx)

    footer_draw = ImageDraw.Draw(img)
    draw_footer(footer_draw, (0, HEADER_HEIGHT + canvas_h, total_w, total_h), ctx, palette)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    return fonts.warning


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="render_nav_previews.py",
        description=(
            "Генератор PNG-прев'ю варіантів навігації Power BI (V1..V7). "
            "Один запуск малює один PNG для варіанта з config.json (або --variant)."
        ),
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="config.json",
        help=(
            "Шлях до JSON-конфігурації (pages, palette, font, variant, hero_page, out_dir; "
            "опційно: selected_style S1..S5, icons none|labeled|only, groups)."
        ),
    )
    parser.add_argument(
        "--variant",
        choices=sorted(VARIANTS),
        default=None,
        help="Перевизначити 'variant' із config.json (V1..V7).",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        metavar="DIR",
        help="Перевизначити 'out_dir' із config.json.",
    )
    return parser.parse_args(argv)


def resolve_relative_icon_paths(config: dict, config_path: Path) -> None:
    """Відносні pages[].icon трактуються як відносні до config.json, а не до
    поточної робочої директорії процесу — так шлях 'icons/home.png' у
    конфігу залишається переносним незалежно від того, звідки викликано
    скрипт. Абсолютні шляхи лишаються без змін."""
    pages = config.get("pages")
    if not isinstance(pages, list):
        return
    config_dir = config_path.resolve().parent
    for page in pages:
        if not isinstance(page, dict):
            continue
        icon = page.get("icon")
        if isinstance(icon, str) and icon and not Path(icon).is_absolute():
            page["icon"] = str((config_dir / icon).resolve())


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        resolve_relative_icon_paths(config, Path(args.config))
        variant_key = args.variant or config.get("variant")
        if variant_key not in VARIANTS:
            allowed = ", ".join(sorted(VARIANTS))
            raise ValueError(f"Невідомий variant: {variant_key!r}. Дозволені значення: {allowed}.")

        validate_config(config)

        out_dir = Path(args.out_dir or config.get("out_dir") or "previews")
        out_path = out_dir / f"{variant_key}.png"

        warning = render(config, variant_key, out_path)
        if warning:
            sys.stderr.write(f"[WARN] {warning}\n")

        print(f"OK: {out_path} ({VARIANTS[variant_key]['layout']})")
        return 0
    except Exception as exc:  # noqa: BLE001 - усі помилки зводяться в exit code 1
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
