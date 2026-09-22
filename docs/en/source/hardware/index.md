# Quadruped Assembly

Chapter 13 drives an 8-servo quadruped from your own OS.

```{figure} ../_static/quadruped_walk.gif
:name: fig-quadruped-walk
:width: 80%

The quadruped walking on your own OS, driving 8 servos (1.5x speed)
```

| Item | Qty | Notes |
|---|---|---|
| FEETECH STS3215 serial bus servo (12V) | 8 | [Akizuki Denshi 130969](https://akizukidenshi.com/catalog/g/g130969/) |
| Bus servo driver board (Waveshare 25514) | 1 | [Akizuki Denshi 131227](https://akizukidenshi.com/catalog/g/g131227/) |
| 12V 5A AC adapter | 1 | bench use only |
| 3D-printed body & legs | 1 set | STL downloads below |
| Arduino UNO R4 WiFi | 1 | |

The full bill of materials with purchase links, power-supply sizing, and
3D-printing settings is currently **Japanese only**:

```{raw} html
<p><a href="../../hardware/bom.html">部品表（BOM） — on the Japanese site ↗</a></p>
```

## STL downloads

Print quantities: body ×1, bracket ×4, link ×4 (left and right legs use
the same parts). Units are millimeters.

```{raw} html
<ul>
  <li><a href="../../assembly/quadruped/stl/body.stl">body.stl</a> (×1, 230 × 110 × 50 mm)</li>
  <li><a href="../../assembly/quadruped/stl/bracket_outline.stl">bracket_outline.stl</a> (×4, 128 × 52 × 12 mm)</li>
  <li><a href="../../assembly/quadruped/stl/leg_link1.stl">leg_link1.stl</a> (×4, 80 × 52 × 26 mm)</li>
  <li><a href="../../assembly/quadruped/stl/body.3mf">body.3mf</a> — Bambu Studio project, body plate, author-tested settings (X1C, 0.28 mm, ABS)</li>
  <li><a href="../../assembly/quadruped/stl/leg_parts.3mf">leg_parts.3mf</a> — Bambu Studio project, all 8 leg parts</li>
</ul>
```

## Photos

::::{grid} 2 3 3 3
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_parts.jpg
:target: ../_static/quadruped_parts.jpg
:alt: All parts: 9 printed parts, 8 STS3215 servos, and the bundled screws

All parts: 9 printed parts, 8 STS3215 servos, and the bundled screws
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_body_servo.jpg
:target: ../_static/quadruped_body_servo.jpg
:alt: Body with four servos fixed

Body with four servos fixed
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_legs_x4.jpg
:target: ../_static/quadruped_legs_x4.jpg
:alt: Four servos with leg brackets attached

Four servos with leg brackets attached
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_driver_board.jpg
:target: ../_static/quadruped_driver_board.jpg
:alt: Driver board: A/B jumper (yellow), USB Type-C and DC jack

Driver board: A/B jumper (yellow), USB Type-C and DC jack
```

:::
::::

## Interactive assembly guide

An interactive 3D assembly viewer shows every step as an animation
(UI labels are in Japanese, but the 3D animation itself is
language-independent):

```{raw} html
<p><a href="../../assembly/quadruped/index.html" target="_blank" rel="noopener">
Open the 3D assembly viewer ↗</a></p>
```
