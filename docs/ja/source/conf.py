"""Sphinx configuration (ja)."""

import os

project = "『つくりながら学ぶ！リアルタイムOS自作入門』サポートページ"
author = "Iori Yanokura"
copyright = "2026, Iori Yanokura"
language = "ja"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]

myst_enable_extensions = ["colon_fence", "dollarmath"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# GitHub Pages では BASE_URL=/build-your-own-arduino-rtos/ を渡す
_base = os.environ.get("BASE_URL", "/")

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/iory/build-your-own-arduino-rtos",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Language",
            "icon": "fa-solid fa-language",
            "type": "dropdown",
            "items": [
                {"name": "English", "url": _base + "en/"},
            ],
        },
    ],
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "footer_end": [],
}

html_title = "RTOS自作入門 サポートページ"
