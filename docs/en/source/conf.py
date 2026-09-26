"""Sphinx configuration (en)."""

import json
import os

project = "Build Your Own Arduino RTOS — Book Support"
author = "Iori Yanokura"
copyright = "2026, Iori Yanokura"
language = "en"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_togglebutton",
    "sphinxext.opengraph",
    "sphinx_sitemap",
]

myst_enable_extensions = ["colon_fence", "dollarmath"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["bambu-open.js"]

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
                {"name": "日本語", "url": _base + ""},
            ],
        },
    ],
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "footer_end": [],
}

html_title = "Arduino RTOS Book Support"

# ファビコンは scripts/make_brand_images.py が第0章のスケッチの "OS" から作る。
# PNG 版と apple-touch-icon は _templates/layout.html で読み込む。
html_favicon = "_static/favicon.svg"

# SNS で共有されたときのプレビュー（OGP）。ogp_image は ogp_site_url からの相対。
SITE_URL = "https://iory.github.io/build-your-own-arduino-rtos/"
ogp_site_url = SITE_URL + "en/"
ogp_image = "_static/og_image.png"
ogp_image_alt = "Cover of the book and the word OS on an LED matrix"
ogp_social_cards = {"enable": False}
ogp_custom_meta_tags = ['<meta name="twitter:card" content="summary_large_image">']

# 検索エンジン向けのサイトマップ（sphinx-sitemap）。英語版は /en/の
# sitemap.xml に出る。既定の URL 形式は言語コードを前に付けて存在しない
# /en/ 付きの URL を作るので、ページのパスだけにする。
html_baseurl = SITE_URL + "en/"
sitemap_url_scheme = "{link}"
sitemap_excludes = ["search.html", "genindex.html"]

# Google Search Console の所有権確認タグ。CF_BEACON_TOKEN と同じく公開 HTML に
# そのまま出る値なので、ワークフローの env でだけ持たせる。未設定なら出さない。
html_context = {
    "google_site_verification": os.environ.get("GOOGLE_SITE_VERIFICATION", ""),
}


# Cloudflare Web Analytics のビーコン。トークンは公開 HTML に出るものなので
# 秘密ではないが、値の重複を避けるためワークフローの env でだけ持たせている。
# ローカルビルドでは未設定になり、ビーコンを出さない（自分の閲覧を数えない）。
_cf_beacon_token = os.environ.get("CF_BEACON_TOKEN", "")


def setup(app):
    """Cloudflare Web Analytics のビーコンを全ページに差し込む。"""
    if not _cf_beacon_token:
        return
    app.add_js_file(
        "https://static.cloudflareinsights.com/beacon.min.js",
        type="module",
        **{"data-cf-beacon": json.dumps({"token": _cf_beacon_token})},
    )
