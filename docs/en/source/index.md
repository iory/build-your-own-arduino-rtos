---
og:description: "Support site for the Japanese book on building a preemptive real-time OS from scratch on the Arduino UNO R4 WiFi: setup, per-chapter sample code, quadruped assembly, and errata."
---

# Build Your Own Arduino RTOS — Book Support

Support site for the (Japanese) book on building a preemptive
real-time OS from scratch on the **Arduino UNO R4 WiFi**.

```{raw} html
<video src="_static/promo.mp4" poster="_static/og_image.png" controls muted playsinline loop preload="metadata"
       style="width:100%; border-radius:8px;"
       aria-label="Book trailer: from booting your own OS to a walking quadruped"></video>
```

```{note}
The book is written in Japanese; this English version of the support
site currently covers setup and per-chapter build instructions.
Full translations are in progress.
```

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} 🚀 Getting Started
:link: getting-started/index
:link-type: doc
What you need and how to set up Arduino IDE / PlatformIO.
:::

:::{grid-item-card} 💻 Running Without the Board
:link: getting-started/simulator
:link-type: doc
Run the same firmware on your PC when you do not have the board.
:::

:::{grid-item-card} 📖 Chapter Support
:link: chapters/index
:link-type: doc
Sample code locations, build commands, common pitfalls.
:::

:::{grid-item-card} 🤖 Quadruped Assembly
:link: hardware/index
:link-type: doc
Hardware for the chapter-13 quadruped robot.
:::

:::{grid-item-card} ❓ FAQ / Errata
:link: faq
:link-type: doc
Troubleshooting and corrections.
:::
::::

## About the Book

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item}
:columns: 12 12 4 4

```{image} _static/book_cover.jpg
:alt: Cover of the book (Japanese edition)
:width: 240px
:align: center
:target: https://book.mynavi.jp/ec/products/detail/id=152331
```

:::

:::{grid-item}
:columns: 12 12 8 8
*つくりながら学ぶ！リアルタイムOS自作入門* (Japanese edition),
by Iori Yanokura, published by Mynavi Publishing on September 18, 2026.
ISBN 978-4-8399-9187-6. Available in print and as a PDF.

{bdg-link-primary}`Mynavi Books (print / PDF)<https://book.mynavi.jp/ec/products/detail/id=152331>`
{bdg-link-primary}`Amazon.co.jp<https://www.amazon.co.jp/dp/4839991871>`
{bdg-link-primary}`Rakuten Books<https://books.rakuten.co.jp/rb/18716697/>`
{bdg-link-primary}`honto (ebook)<https://honto.jp/isbn/9784839991876>`
:::
::::

```{toctree}
:hidden:
getting-started/index
chapters/index
hardware/index
faq
errata
```
