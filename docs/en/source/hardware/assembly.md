# Assembly — 8-DoF quadruped

First build the three kinds of units (the body with its servos, the left legs and
the right legs), then attach the legs to the body.

You need **40 M3×6 screws and 16 M2×6 screws**, and **the screws that come with the
STS3215 servos are enough** (eight servos include plenty). Nothing else to buy.

The step images below are CAD renders whose labels are in Japanese; the steps are
spelled out in English next to each one.

::::{grid} 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_parts.jpg
:target: ../_static/quadruped_parts.jpg
:alt: The parts: 9 printed parts (body ×1, leg bracket ×4, leg link ×4), 8 STS3215 servos and the bundled screws

The parts: 9 printed parts (body ×1, leg bracket ×4, leg link ×4), 8 STS3215 servos and the bundled screws
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_screws.jpg
:target: ../_static/quadruped_screws.jpg
:alt: The screws that come with the STS3215 (3 kinds)

The screws that come with the STS3215 (3 kinds)
```

:::
::::

## Interactive 3D viewer

Plays the assembly step by step as an animation in the browser. Drag to rotate the
view and use the slider to step back and forth.

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../../assembly/quadruped/index.html"
     target="_blank" rel="noopener">Open the viewer full screen ↗</a>
  &nbsp;
  <a class="sd-btn sd-btn-outline-primary" href="../../assembly/quadruped/instructions.pdf"
     target="_blank" rel="noopener">PDF instructions</a>
</p>
<iframe src="../../assembly/quadruped/index.html"
        style="width:100%; height:75vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="Quadruped assembly viewer"></iframe>
```

---

## Units

The robot is built from three kinds of units (sub-assemblies) first; the legs go on
the body last. There are **81 individual parts (8 kinds)** in total.

| Unit | Qty | Parts inside |
|---|---|---|
| body_servo (body + 4 servos) | ×1 | 13 |
| leg_left (left leg) | ×2 | 11 |
| leg_right (right leg) | ×2 | 11 |

| Part | Qty |
|---|---|
| Screw M3×6 | ×40 |
| Screw M2×6 | ×16 |
| STS3215 (case + horn) | ×8 |
| bracket_outline | ×4 |
| leg_link1 | ×4 |
| Body | ×1 |

## Building the units

Each kind of unit is shown once; **×N** is how many the whole robot uses. Build them
from top to bottom and you will have every unit you need.

:::{dropdown} STS3215 servo (fitting the horn) **×8**
:open:

Only if the horn arrived detached. If it is already fitted, skip this unit.

1. Place the **STS3215_horn** (base).

   ![STS3215 step 1](assembly_img/units/STS3215/step_01.png)

2. **STS3215_case** onto the horn — coaxial φ4.8 mm (×2), 2 mating faces.

   ![STS3215 step 2](assembly_img/units/STS3215/step_02.png)

```{figure} ../_static/quadruped_horn_screw.jpg
:target: ../_static/quadruped_horn_screw.jpg
:width: 50%

Hold the screwdriver tip in line with the screw hole. If the tip is at an angle the force does not get through and the screw head strips easily
```

:::

:::{dropdown} body_servo (fixing 4 servos in the body) **×1**

Parts: body ×1, STS3215 ×4, M3x6 ×8

1. Place the **body** (base).

   ![body_servo step 1](assembly_img/units/body_servo/step_01.png)

2. **STS3215-4** — insert into the body (coaxial φ4.2 mm ×4, 2 mating faces).

   ![body_servo step 2](assembly_img/units/body_servo/step_02.png)

3. 🔩 Tighten **M3x6 ×2** (STS3215-4 ↔ body).

   ![body_servo step 3](assembly_img/units/body_servo/step_03.png)

4. **STS3215-3** — insert into the body.

   ![body_servo step 4](assembly_img/units/body_servo/step_04.png)

5. 🔩 Tighten **M3x6 ×2**.

   ![body_servo step 5](assembly_img/units/body_servo/step_05.png)

6. **STS3215-2** — fit to the body (2 mating faces).

   ![body_servo step 6](assembly_img/units/body_servo/step_06.png)

7. 🔩 Tighten **M3x6 ×2**.

   ![body_servo step 7](assembly_img/units/body_servo/step_07.png)

8. **STS3215-1** — fit to the body (2 mating faces).

   ![body_servo step 8](assembly_img/units/body_servo/step_08.png)

9. 🔩 Tighten **M3x6 ×2**.

   ![body_servo step 9](assembly_img/units/body_servo/step_09.png)

```{figure} ../_static/quadruped_body_servo.jpg
:target: ../_static/quadruped_body_servo.jpg
:width: 50%

The body with its four servos fixed (the real thing)
```

:::

::::::{dropdown} leg_left (left leg) **×2**

Parts: STS3215 ×1, bracket_outline ×1, leg_link1 ×1, M3x6 ×4, M2x6 ×4

1. Place the **STS3215** (base).

   ![leg_left step 1](assembly_img/units/leg_left/step_01.png)

2. **bracket_outline** — insert on the horn side of the servo (coaxial φ3.2 mm ×4, 2 mating faces).

   ![leg_left step 2](assembly_img/units/leg_left/step_02.png)

3. 🔩 Tighten **M3x6 ×4** (servo ↔ bracket).

   ![leg_left step 3](assembly_img/units/leg_left/step_03.png)

4. **leg_link1** — insert on the case side of the servo (coaxial φ2.0 mm ×4, 2 mating faces).

   ![leg_left step 4](assembly_img/units/leg_left/step_04.png)

5. 🔩 Tighten **M2x6 ×4** (servo ↔ link).

   ![leg_left step 5](assembly_img/units/leg_left/step_05.png)

**Photos of the real thing** (the steps are the same for left and right legs):

:::::{grid} 2 3 3 3
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_bracket_seat_1.jpg
:target: ../_static/quadruped_bracket_seat_1.jpg
:alt: Where the leg bracket meets the horn

Where the leg bracket meets the horn
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_seat_2.jpg
:target: ../_static/quadruped_bracket_seat_2.jpg
:alt: The same part from another angle

The same part from another angle
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_1.jpg
:target: ../_static/quadruped_bracket_1.jpg
:alt: "Step 2: the bracket onto the horn side of the servo"

Step 2: the bracket onto the horn side of the servo
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_2.jpg
:target: ../_static/quadruped_bracket_2.jpg
:alt: "Step 3: tightening the screws"

Step 3: tightening the screws
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_3.jpg
:target: ../_static/quadruped_bracket_3.jpg
:alt: "Step 3: all four M3x6 screws tightened"

Step 3: all four M3x6 screws tightened
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_leg_link_1.jpg
:target: ../_static/quadruped_leg_link_1.jpg
:alt: "Step 4: the leg link onto the case side of the servo"

Step 4: the leg link onto the case side of the servo
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_leg_link_2.jpg
:target: ../_static/quadruped_leg_link_2.jpg
:alt: "Step 4: inserted"

Step 4: inserted
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_legs_x4.jpg
:target: ../_static/quadruped_legs_x4.jpg
:alt: Four servos with their brackets (two left, two right)

Four servos with their brackets (two left, two right)
```

:::
:::::
::::::

:::{dropdown} leg_right (right leg) **×2**

Parts: STS3215 ×1, bracket_outline ×1, leg_link1 ×1, M3x6 ×4, M2x6 ×4
(same as the left leg, with the bracket mirrored)

1. Place the **STS3215** (base).

   ![leg_right step 1](assembly_img/units/leg_right/step_01.png)

2. **bracket_outline** — insert on the horn side of the servo.

   ![leg_right step 2](assembly_img/units/leg_right/step_02.png)

3. 🔩 Tighten **M3x6 ×4**.

   ![leg_right step 3](assembly_img/units/leg_right/step_03.png)

4. **leg_link1** — insert on the case side of the servo.

   ![leg_right step 4](assembly_img/units/leg_right/step_04.png)

5. 🔩 Tighten **M2x6 ×4**.

   ![leg_right step 5](assembly_img/units/leg_right/step_05.png)
:::

```{warning}
Before you start, **give every servo a unique ID** (they all ship with the same ID,
so connect and set them one at a time; once they are in the robot you cannot tell
them apart).

The zero point is set **in software after assembly**, so the horn angle does not
matter while you build. See chapter 13 for the procedure.
```

## Final assembly

Attach the pre-built units to the body (body_servo).

### Step 1: place body_servo

![Step 1](assembly_img/step_001.png)

### Step 2: attach leg_right (first)

Insert the leg link onto the servo horn at the rear of the body (coaxial φ3.0 mm ×4).

![Step 2](assembly_img/step_002.png)

### Step 3: 🔩 tighten M3x6 ×4

![Step 3](assembly_img/step_003.png)

### Step 4: attach leg_right (second)

![Step 4](assembly_img/step_004.png)

### Step 5: 🔩 tighten M3x6 ×4

![Step 5](assembly_img/step_005.png)

### Step 6: attach leg_left (first)

Insert onto the servo horn on the other side. It goes in the opposite direction to
the right legs.

![Step 6](assembly_img/step_006.png)

### Step 7: 🔩 tighten M3x6 ×4

![Step 7](assembly_img/step_007.png)

### Step 8: attach leg_left (second)

![Step 8](assembly_img/step_008.png)

### Step 9: 🔩 tighten M3x6 ×4

![Step 9](assembly_img/step_009.png)

The robot is complete. For wiring, power-up and calibration, see chapter 13.

---

The CAD data was exported with
[solidworks_urdf_exporter2](https://github.com/jsk-ros-pkg/solidworks_urdf_exporter2).
