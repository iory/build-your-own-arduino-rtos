---
og:description: Where to start reading the book on building a real-time OS on the Arduino UNO R4 WiFi, picked by what you are curious about.
---

# Start From What You Are Curious About

The book builds up from Chapter 1, but you do not have to read it in order.
Pick whatever you are curious about below. If you run into a term you do not
know, go back to an earlier chapter at that point.

## I want to see it running first

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Run your own OS in the browser
:link: getting-started/simulator
:link-type: doc
The same firmware as on the real board, running in QEMU inside your browser.
Nothing to install.
:::

:::{grid-item-card} Walk the quadruped in the browser
:link: hardware/walk
:link-type: doc
The trained walking policy in a physics simulation.
Steer it forward and turn with sliders.
:::
::::

## "Why?" about the computer you use every day

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Why do other apps keep running while one does heavy work?
:link: chapters/ch04
:link-type: doc
Chapter 4: a timer interrupt forcibly switches the running task.
:::

:::{grid-item-card} Why does the OS survive when an app crashes?
:link: chapters/ch06
:link-type: doc
Chapter 6: catch a divide by zero or a write to a bad address,
and stop only the task that caused it.
:::

:::{grid-item-card} How do `top` and Task Manager count CPU %?
:link: chapters/ch07
:link-type: doc
Chapter 7: show the CPU usage the OS counts on the LED matrix.
:::

:::{grid-item-card} What does the CPU do the moment you power it on?
:link: chapters/ch01
:link-type: doc
Chapter 1: follow the path from reset to `main()`.
:::

:::{grid-item-card} What happens inside `malloc`?
:link: chapters/adv3
:link-type: doc
Advanced 3: write `malloc` / `free` yourself.
:::

:::{grid-item-card} How is a "file" made?
:link: chapters/adv4
:link-type: doc
Advanced 4: put a filesystem on top of the flash memory.
:::
::::

## Start from what you like

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} I want to make a robot walk
:link: chapters/ch13
:link-type: doc
Chapter 13: drive eight servos from your own OS to walk a quadruped.
Parts and assembly are in {doc}`hardware/index`.
:::

:::{grid-item-card} I like Python
:link: chapters/ch11
:link-type: doc
Chapter 11: build a small Python that runs on the microcontroller.
Chapter 8 before it builds an even smaller language.
:::

:::{grid-item-card} I use FreeRTOS at work
:link: chapters/ch10
:link-type: doc
Chapter 10: solve the same problem with FreeRTOS and compare the designs.
:::

:::{grid-item-card} I like electronics
:link: chapters/ch12
:link-type: doc
Chapter 12: understand PWM generation and A/D conversion at the register level.
:::
::::

## I want to break something that works

Chapters 4, 6, and 7 end with "break it" experiments: change one place in the
code, predict what will happen, then run it. They also work in the browser
version.

- {ref}`ch04-break`
- {ref}`ch06-break`
- {ref}`ch07-break`
