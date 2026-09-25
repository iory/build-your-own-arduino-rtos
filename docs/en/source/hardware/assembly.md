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

(servo-id)=
## Give each servo an ID

**Before building the units, give the eight servos the IDs 1 to 8.** All eight share
one bus, and the microcontroller addresses each servo by its ID. New STS3215 servos,
however, **all ship as ID 1**, so out of the box they cannot be told apart.

Set the IDs with **one servo connected at a time**. With two ID-1 servos on the bus,
a "change ID 1 to 2" command reaches both of them and both become ID 2. The tool
still sees what looks like one servo, so nothing tells you it went wrong.

### What you need

- A PC (Windows / macOS / Linux)
- The driver board (Waveshare Bus Servo Adapter (A)) and a USB Type-C cable
- The 12 V AC adapter (item 3 in the [parts list](bom.md))
- An STS3215 (just one to start with)
- Masking tape and a pen, for number labels

### Install the tool

IDs are set with [feetech-cli](https://github.com/iory/feetech-cli). With the uv you
installed while setting up (if you have not yet, see "Install uv" for
[macOS](../getting-started/macos.md) / [Windows](../getting-started/windows.md) /
[Linux](../getting-started/linux.md) first), one line installs the `feetech` command:

```console
$ uv tool install feetech-cli
```

uv takes care of Python, so there is nothing else to install. The command goes into
the same place as uv itself, so any shell where `uv` runs also finds `feetech`.

### Connect

1. Put **both jumpers on B (USB-SERVO)**. A is the position for driving the servos
   from an Arduino; left on A, the PC cannot see the servo.
2. Plug a single servo into one of the board's 3-pin connectors (D V G).
3. Plug the AC adapter into the board's DC jack. **The servo cannot be powered from
   USB**, so without this it does not answer.
4. Connect the board to the PC with the USB Type-C cable.

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/servo_id_setup.jpg
:target: ../_static/servo_id_setup.jpg
:alt: A PC, the AC adapter, the driver board and a single servo connected together

The whole setup. PC to board over USB Type-C, board powered from the AC adapter,
exactly one servo
```

:::
:::{grid-item}

```{figure} ../_static/servo_id_wiring.jpg
:target: ../_static/servo_id_wiring.jpg
:alt: The driver board with the DC jack, the USB Type-C cable and the servo cable plugged in

At the board: DC jack (power) on the left, USB Type-C (PC) next to it, and the servo
cable in a 3-pin connector at the top. The PWR LED lights red when power is on
```

:::
:::{grid-item}

```{figure} ../_static/servo_id_jumper.jpg
:target: ../_static/servo_id_jumper.jpg
:alt: Both jumpers in the B position. The board is printed with A = UART-SERVO and B = USB-SERVO

Both jumpers on **B (USB-SERVO)**. What A and B mean is printed on the board
```

:::
::::

### Number them one by one

1. Check the servo is visible.

   ```console
   $ feetech scan
   Found 1 servo(s) on /dev/cu.usbmodem59710813431 at 1.00Mbps:
     id   1  model   777  position  4095 (+179.9 deg)  12.3V  32C
   ```

   A single `id 1` line means you are ready. The port name depends on your system
   (`COM3` or similar on Windows); the tool finds it by itself, so there is nothing to
   pass.

2. Write the new ID. It is written once you answer `y`. The first servo can keep
   ID 1, so this step starts with the second one.

   ```console
   $ feetech set-id 1 2
   Change servo 1 to id 2? This writes the servo EEPROM. [y/N] y
   Servo 1 is now id 2.
   ```

   The ID is stored in the servo's EEPROM, so it survives a power cycle.

3. Run `feetech scan` again and check the servo answers at its new ID.

4. **Label the servo.** Once they are mixed up, the only way to tell them apart is to
   connect them one by one again. A label on a face that stays visible after assembly
   also helps later, when wiring or replacing a servo.

5. Unplug it, connect the next new servo and go back to step 1. The third one gets
   `feetech set-id 1 3`, the fourth `feetech set-id 1 4`, and so on up to 8.

```{figure} ../_static/servo_set_id.gif
:alt: feetech scan finds a servo at ID 1, feetech set-id 1 2 changes it to ID 2, and a second scan finds it at ID 2

Steps 1 to 3 on real hardware
```

```{figure} ../_static/servo_id_label.jpg
:target: ../_static/servo_id_label.jpg
:width: 50%
:alt: A servo with a label reading "ID:1" on its side

A servo with its number label
```

### Which servo goes where

Each ID belongs to one joint of one leg. The assignment is the one in the firmware's
`include/quad_calib.h` (`QUAD_SERVO_ID`), so **mount the servos exactly as shown.** A
servo in the wrong place receives another joint's commands.

```{figure} assembly_img/servo_ids.png
:target: assembly_img/servo_ids.png
:alt: The quadruped seen from above and from the left, with each servo's ID marked. Front right 1 and 2, front left 3 and 4, rear right 5 and 6, rear left 7 and 8; the hip is odd and the knee even on every leg

Servo ID assignment. Seen from above, the front (the walking direction) is the end
with the tab in the middle of the body's short side
```

Use these servos when building the units below.

| Unit | Servos inside | IDs to use |
|---|---|---|
| body_servo (body) | the hips of all four legs | 1 (front right), 3 (front left), 5 (rear right), 7 (rear left) |
| leg_right (right leg) ×2 | the knees of the right legs | 2 (front right), 6 (rear right) |
| leg_left (left leg) ×2 | the knees of the left legs | 4 (front left), 8 (rear left) |

### Troubleshooting

| Symptom | Check |
|---|---|
| `feetech scan` finds nothing | The AC adapter is plugged in (PWR LED), the jumpers are on B, the servo cable is fully seated |
| No port is found | The USB cable carries data (a charge-only cable shows no port) |
| A servo whose bus speed was changed before is not found | `feetech scan --all-baudrates` tries every speed |
| `id 2 is already used by another servo on this bus` | A servo with that ID is also connected. Leave only one and try again |

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
Before you start, **give every servo its ID** ([Give each servo an ID](#servo-id)).
Once they are in the robot you cannot tell them apart.

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
