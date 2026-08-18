---
name: pbi-naftogaz-theme
description: Use when застосування бренд-теми Нафтогаз до Power BI звіту (PBIP, PBIR enhanced) або коли потрібні логотипи Нафтогазу у звіті. Triggers - 'тема Нафтогаз', 'Naftogaz theme', 'ребренд під Нафтогаз', 'нафтогазівські кольори', 'логотип Нафтогазу'. NOT for авторства тем з нуля (pbi-theme-json), інших брендів (theme-factory), піктограм даних (icon-set-manager).
---

# Naftogaz Theme

## Overview

Чотири готові бренд-теми Нафтогазу (повний `visualStyles` на базі `pbi-theme-json/assets/master-theme.json`) плюс PNG-логотипи з прозорим фоном. Один скрипт перемикає звіт на обрану палітру та реєструє логотипи.

Бренд-константи: навій `#0C375E`, азур `#00A1DF` (джерело: logo-color-uk.svg, naftogaz.com).

## Робочий цикл

**Крок 0 — спитати палітру. Завжди. AskUserQuestion, не вгадувати:**

| Ключ | Ядро палітри | Коли |
|---|---|---|
| `classic` (Recommended) | `#0C375E` `#00A1DF` `#F2A900` | корпоративний стандарт |
| `energy` | `#0C375E` `#FFD500` `#0057B7` | національні синьо-жовті акценти |
| `flame` | `#0C375E` `#00A1DF` `#0E7490` | стримана моно-синя гама |
| `dark` | фон `#0E1F33`, дані `#00A1DF` `#4FC3F7` | темний режим |

Крок 1 — застосувати:
`python scripts/apply_naftogaz_theme.py "<X.Report>" --palette <ключ>` (`--no-logos` — без логотипів).

Крок 2 — схемна валідація: `pbir_schema_validate.py "<X.Report>/definition"` → 0 помилок.

Крок 3 — жива перевірка: відкрити `.pbip`, скріншоти, закривати через «Не зберігати».

## Логотипи (PNG, прозорий фон, реєструються автоматично)

| Файл | Вміст | Палітри |
|---|---|---|
| `naftogaz_logo_full_light.png` | знак + «Нафтогаз Група», навій | світлі |
| `naftogaz_logo_full_dark.png` | білий текст, знак із вирізом | `dark` |
| `naftogaz_logo_icon_light.png` | навій квадрат, біле полумʼя | світлі |
| `naftogaz_logo_icon_dark.png` | білий квадрат, полумʼя-виріз | `dark` |

«Виріз» = прозорість: полумʼя набуває колір фону під логотипом (офіційний стиль футера naftogaz.com).

## Common mistakes

| Помилка | Наслідок | Правильно |
|---|---|---|
| Палітра «за замовчуванням» без питання | не той бренд-режим | Крок 0 завжди |
| `dark`-палітра + `*_light` логотип | навій зливається з темним фоном | пари light↔світлі, dark↔`dark` |
| Звіт PBIR-Legacy | скрипт свідомо відмовить | рецепт wiring: `pbi-theme-json/reference.md` §4 |
| Хук валідації хибно блокує Write у `.Report` | правка не зберігається | писати python-скриптом, перевіряти python-ом |
| Прибрати стару тему з RegisteredResources «для чистоти» руками | ризик зламати посилання | рендериться лише `customTheme`; стара тема не шкодить |
| Виріз композитом `DstOut`, коли destination без альфи | полумʼя стає чорним, а не прозорим — на темному прев'ю невидимо | `magick sq.png -alpha set flame.png -compose DstOut -composite PNG32:out.png`; перевірка: `alpha-min=0` |

## Регенерація асетів

Теми: `python scripts/build_themes.py` — потребує `pbi-theme-json/assets/master-theme.json`; далі валідація проти `reportThemeSchema-2.155.json` (0 помилок). Логотипи: джерела в `assets/logos/*.svg`, рендер ImageMagick `-background none`.

## Verify before done

Скрипт відпрацював → `report.json`: `customTheme.name = naftogaz-<ключ>.json` → тема й логотипи лежать у `RegisteredResources` і зареєстровані в `resourcePackages` → `pbir_schema_validate` 0 помилок → жива перевірка в Desktop.
