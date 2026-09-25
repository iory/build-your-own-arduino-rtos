# Learning to walk (reinforcement learning)

The chapter 13 quadruped walks with **a policy trained by reinforcement learning
(PPO)**. The training side, which did not fit in the book, is supported here.

## Try it in the browser

A simulation that runs the trained policy in **MuJoCo (WebAssembly)**. The same
neural network you flash onto the robot runs a 50 Hz control loop inside the
browser. Use the sliders to change the forward and turning commands.

The physics is **the same as in training**. Only the four foot spheres touch the
ground, the servos are position-controlled (kp 25, kd 0.5) with a viscous damper for
the back-EMF and gearbox friction, and every command reaches the servo 20–35 ms late
(a band around the 27 ms measured on the real robot).

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../../assembly/quadruped/walk/index.html"
     target="_blank" rel="noopener">Open the walking simulation ↗</a>
</p>
<iframe src="../../assembly/quadruped/walk/index.html"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="Quadruped walking simulation"></iframe>
```

```{note}
The first load downloads about 16 MB (the physics engine in WASM and the robot model).
The simulation's UI labels are in Japanese.
```

The control switch compares **the sin/cos gait of section 13.5 in the book** (state
machine + trot) with the RL policy. The sin/cos gait lifts the swing leg along a sine
arc and converts it to joint angles with two-link IK (section 13.3); it is the book's
sample code `src/gait.cpp` + `src/leg_ik.cpp` ported to the browser as is. This
robot is asymmetric front to back, though, so the gait changes completely with the
direction: with the same 0.02 m stride (slider ±0.05) it barely moves forward
(0.006 m/s) but goes backward at 0.10 m/s. Forward, the slider at 0.12 (0.048 m
stride) gives 0.06 m/s, and at 0.15 it tips over sideways about one run in eight.
Tuning the coefficients by hand can only suit one direction — that is the motivation
for RL.

## Inside the policy

A single small MLP does all the walking, small enough to run inference every cycle
on the Arduino UNO R4.

| | |
|---|---|
| Input (observation) | **87 dimensions** = command (vx, vy, wz), gait phase (sin/cos), 8 joint angles, 8 joint velocities, the previous 8 actions, each with **3 steps of history** |
| Network | Fully connected [96, 64], ELU activation |
| Output | 8 (one per joint). Servo target = home angle + 0.25 × action |
| Control period | 50 Hz (0.02 s), gait clock 0.32 s |
| Sensors | **Joint angles and velocities only. No IMU** (the robot has none, so the policy cannot see the body's attitude) |

With no abduction joints it cannot move sideways (vy); it turns by taking longer
steps on one side.

Performance in simulation: 0.120 m/s (0.48 body lengths/s) for a forward command of
0.12 m/s, and 0.148 m/s for the maximum command of 0.15 m/s, so it tracks the command
closely. Turning reaches 0.213 rad/s for a 0.3 rad/s command. The diagonal trot runs at
3.13 Hz (gait period 0.32 s), the same at every speed. All of these were measured with
the same model and controller as the simulation above, five 20 s runs each, averaging
the last 10 s. The low speed is a property of the robot, set by the servos'
no-load speed, not a failure of training.

## Training code

Training uses PPO (rsl_rl) in
[mjlab (unitree_rl_mjlab)](https://github.com/unitreerobotics/unitree_rl_mjlab),
written as an overlay that swaps in the robot definition, rewards and environment
settings:

- Code: [docs/os-on-arduino/code/13_quadruped/rl](https://github.com/iory/learning-os-from-arduino/tree/main/docs/os-on-arduino/code/13_quadruped/rl)
- The full robot description (**URDF**, MJCF, meshes, RViz config, with a script that
  reproduces the MJCF from the SolidWorks export):
  [docs/os-on-arduino/code/13_quadruped/arduino_os_quad_robot](https://github.com/iory/learning-os-from-arduino/tree/main/docs/os-on-arduino/code/13_quadruped/arduino_os_quad_robot)

For sim2real it was trained with randomised friction (0.4–1.1), added mass (0–250 g
for the electronics), zero-point error (±1.7°), joint angles (±8.6°) and more, then
fine-tuned (robustified) with further randomised reset poses and velocities. That is
why it still walks if the assembly is a few degrees off.

**How to retrain it yourself is in {doc}`train`**, for when you want to change the
rewards or the speed limit, and **how to run it on Google Colab if you have no GPU**.

## Walking the real robot

Use the chapter 13 sample code,
[`code/13_quadruped/`](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/13_quadruped).
The trained policy is in `include/arduino_quad_policy.h`, and it is **the same policy
as the browser simulation above**.

Three values have to match your robot. The **servo IDs** follow the
{ref}`assembly table <servo-id>`, and the **rotation directions (sign)** are fixed by
how the legs are mounted, so a robot built as in the book keeps the values already in
`include/quad_calib.h`. That leaves the **zero point**, which is written into each
servo's EEPROM with the legs held straight. Because it lives in the servos, the
firmware does not need editing.

```{figure} ../_static/quadruped_walk.gif
:name: fig-walk-real
:width: 80%

The book's robot (8 servos driven by your own OS) walking (1.5x speed)
```

### 1. Wiring

The driver board and the Arduino UNO R4 WiFi sit side by side inside the body. The
eight servos are daisy-chained into the board's 3-pin connectors (D V G).

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_wiring_overview.jpg
:target: ../_static/quadruped_wiring_overview.jpg
:alt: The body seen from above, with eight ID-labelled servos, the driver board and the Arduino

Inside the body. Each label must sit where the {ref}`assembly table <servo-id>` puts
that ID
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_cable_routing.jpg
:target: ../_static/quadruped_cable_routing.jpg
:alt: A servo cable clipped into the hook on a leg bracket

The knee servo's cable runs through the hook on the leg bracket into the body
```

:::
::::

Connect the board's UART header to the Arduino with three wires. On this board
**TX goes to TX and RX to RX** ("Know this before wiring" in {doc}`bom`).

| Driver board | Arduino |
|---|---|
| TX | D1 (TX→1) |
| RX | D0 (RX←0) |
| GND | GND |

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_uart_wiring.jpg
:target: ../_static/quadruped_uart_wiring.jpg
:alt: Three wires from the board's UART header (TX RX GND) to the Arduino, jumpers on A

Board side: TX (blue), RX (green), GND (white). The jumpers here are on **A**, the
position for driving the servos from the Arduino
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_uart_pins.jpg
:target: ../_static/quadruped_uart_pins.jpg
:alt: Blue and green wires on the Arduino's D1 and D0, a white wire on GND

Arduino side: blue on D1 (TX→1), green on D0 (RX←0), white on GND
```

:::
::::

```{figure} ../_static/quadruped_wiring_done.jpg
:target: ../_static/quadruped_wiring_done.jpg
:width: 50%
:alt: The wired body from above, with the DC jack and a USB Type-C cable plugged into the board

Wiring done. The board takes power on the DC jack, and USB Type-C when the PC drives
the servos
```

### 2. Set the zero point from the PC

Put the driver board's jumpers on **B (USB-SERVO)** and connect the board's USB
Type-C to the PC. The Arduino is not involved; the PC drives the servos directly.

```bash
cd code/13_quadruped/host
uv sync                                  # installs numpy and feetech-cli

uv run python quad_host.py scan          # do all 8 answer?
uv run python quad_host.py zero          # make the straight-leg pose the zero point
```

`zero` switches the torque off and waits for **all four legs hanging straight down,
hip to foot** (**hold the robot up or suspend it**). The CAD is drawn so that this pose
is 0 degrees. Press Enter and the zero point goes into the EEPROM of all eight servos,
which are then checked to read 2048. It survives a power cycle.

::::{grid} 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_zero_side.jpg
:target: ../_static/quadruped_zero_side.jpg
:alt: A leg held straight down, seen from the side

The zero pose, from the side
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_zero_front.jpg
:target: ../_static/quadruped_zero_front.jpg
:alt: The same leg held straight down, seen from the front

The same pose from the front: thigh and shank in one line
```

:::
::::

With the zero point in place, the PC can already stand the robot up and walk it.

```bash
uv run python quad_host.py stand         # hold the home pose; Ctrl-C goes limp
uv run python quad_host.py teleop        # walk from the keyboard (the PC runs the policy)
```

Do `stand` **with the robot suspended first** and check that all four legs take the
same shape with the knees pulled back. If one leg comes out mirrored, that leg's ID or
mounting is wrong.

The `teleop` keys are below. Each press of `w` adds 0.02 m/s of forward speed, and
space stops the robot.

| Key | Action |
|---|---|
| `w` / `s` | forward speed ±0.02 m/s |
| `a` / `d` | turn rate ±0.05 rad/s |
| space | stop and hold the home pose |
| `0` | every joint to 0 degrees (legs straight). Suspended only |
| `x` / Ctrl-C | stop, go limp and quit |

```{raw} html
<figure style="margin:1.5rem auto; max-width:80%;">
  <video src="../_static/quadruped_walk_usb.mp4" poster="../_static/quadruped_walk_usb_poster.jpg"
         controls muted playsinline loop preload="metadata"
         style="width:100%; border-radius:8px;" aria-label="Walking with the PC driving the servos over USB"></video>
  <figcaption style="font-size:0.9em;">The PC runs the policy and drives the servos directly over USB (real time)</figcaption>
</figure>
```

### 3. Flash the Arduino and walk

Put the jumpers back on **A (UART-SERVO)**, connect the Arduino to the PC over USB and
flash it.

```bash
pio run -d code/13_quadruped -t upload
```

When flashing finishes the Arduino boots and rises to the home pose over 2 seconds.
From here **the Arduino runs the policy**, and the PC only sends velocity commands. To
drive it from the keyboard:

```bash
cd code/13_quadruped/host
uv run python quad_host.py serial        # send velocities over the Arduino's USB serial
```

The keys are the same as `teleop`, with two differences. `x` does not go limp: the
robot stops and keeps standing in the home pose. And if commands stop arriving for 0.3
seconds, the Arduino stops by itself and holds the home pose (for when the PC hangs or
the cable comes out).

```{raw} html
<figure style="margin:1.5rem auto; max-width:80%;">
  <video src="../_static/quadruped_walk_arduino.mp4" poster="../_static/quadruped_walk_arduino_poster.jpg"
         controls muted playsinline loop preload="metadata"
         style="width:100%; border-radius:8px;" aria-label="Walking with the Arduino running the policy"></video>
  <figcaption style="font-size:0.9em;">The Arduino UNO R4 WiFi runs the policy; the PC only sends the keyboard's velocity commands (real time)</figcaption>
</figure>
```

You can also type commands straight into a serial monitor
(`pio device monitor -d code/13_quadruped -b 115200`).

| Command | Action |
|---|---|
| `iktest` | FK/IK round-trip test. The legs do not move |
| `stand` / `stop` | move to the home pose over 2 s and hold |
| `rl <vx> <wz>` | walk with the trained policy, e.g. `rl 0.15 0` (forward m/s, turn rad/s) |
| `zero` | move every joint to 0 degrees and hold. Suspended only |
| `free` | switch the torque off |

While walking, a line like this appears every second (the book's robot, `rl 0.15 0`):

```
loop avg 5770 us  max 5797 us  late 0/51  skipped 0  read_fail 0
```

`loop avg` is the time one pass takes; anything inside the 20 ms control period
(50 Hz) is enough. `skipped` counts control periods that were dropped and `read_fail`
servos that did not answer; **both should stay at 0**. If they climb, suspect the
wiring or the power supply.

```{warning}
- Power the 8 servos **from the 12 V AC adapter or a battery**. Never from the PC's USB
  (stall current is 2.7 A per servo)
- Do `stand` and the first walk **with the robot suspended**. With a wrong ID or
  mounting it does not walk badly, it thrashes
```

```{tip}
Rubber or silicone on the feet makes them slip less. The robot walks on bare plastic
too, but on a hard, smooth floor such as wood flooring the feet slip more easily.
```

## FAQ

**Can it get up after falling?** — No. With no IMU it cannot observe its own attitude
(even with training, the success rate was 1%). This is where adding an IMU pays off
most.

**Can it go faster?** — With 45 rpm servos and 0.19 m legs, 0.05–0.2 m/s is what the
hardware can do (0.16 m/s at the maximum command in simulation). The limit is the
no-load speed, not torque, so going faster means changing the servos or the leg length.
