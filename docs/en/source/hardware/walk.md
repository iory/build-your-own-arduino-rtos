# Learning to walk (reinforcement learning)

The chapter 13 quadruped walks with **a policy trained by reinforcement learning
(PPO)**. The training side, which did not fit in the book, is supported here.

## Try it in the browser

A simulation that runs the trained policy in **MuJoCo (WebAssembly)**. The same
neural network you flash onto the robot runs a 50 Hz control loop inside the
browser. Use the sliders to change the forward and turning commands.

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
sample code `src/gait.cpp` + `src/leg_ik.cpp` ported to the browser as is. It walks
well enough on flat ground, but this robot is asymmetric front to back, so its speed
nearly doubles depending on the direction (0.156 m/s vs 0.089 m/s). Tuning the
coefficients by hand can only suit one direction — that is the motivation for RL.

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

Performance in simulation: 0.165 m/s (0.66 body lengths/s) for a forward command of
0.12 m/s, and 0.20 m/s for the maximum command of 0.15 m/s, so it walks about 40%
faster than commanded. The diagonal trot is about 3.1 Hz (gait period 0.32 s). Both
were measured by walking the same model as the simulation above for 20 s and
averaging the last 10 s. The low speed is a property of the robot, set by the servos'
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
as the browser simulation above**. Flash it and it walks, but first you need to
**calibrate your own robot** (servo IDs, rotation directions and zero points differ
from robot to robot).

```{figure} ../_static/quadruped_walk.gif
:name: fig-walk-real
:width: 80%

The book's robot (8 servos driven by your own OS) walking (1.5x speed)
```

### 1. Calibrate the servos from the PC

Set the driver board's jumper to **B (USB → SERVO)** and connect the board's USB
Type-C to the PC. You drive and measure the servos directly from the PC, without
flashing the Arduino.

```bash
cd code/13_quadruped/host
uv sync                                        # installs pyserial and numpy

uv run python quad_host.py scan                # do all 8 answer? is the baud rate right?
uv run python quad_host.py calibrate --write-middle
uv run python quad_host.py stand               # hold the home pose to check
```

`calibrate` is interactive (**hang the robot or hold it in your hand**). It measures,
in order, which ID drives which joint, the rotation direction (sign) and the zero
point, and writes them to `host/calib.json`. `--write-middle` writes the zero point
into the servo's EEPROM, so every joint's zero becomes 2048.

The port is found automatically. Add `--port` only if another USB serial device gets
picked by mistake (names look like `/dev/ttyACM0` on Linux, `/dev/cu.usbmodem...` on
macOS and `COM3` on Windows). OS-specific pitfalls are covered in
{doc}`../getting-started/linux` and {doc}`../getting-started/windows`.

### 2. Copy the calibration into the firmware

Copy the values from `host/calib.json` into `include/quad_calib.h`.

| `calib.json` | `quad_calib.h` |
|---|---|
| `id` | `QUAD_SERVO_ID` |
| `sign` | `QUAD_SERVO_SIGN` |
| `zero` | `QUAD_SERVO_ZERO` (leave all at 2048 if you used `--write-middle`) |

Both use the same order (FL_hip, FL_knee, RL_hip, RL_knee, RR_hip, RR_knee, FR_hip,
FR_knee). **The values already in `quad_calib.h` are for the book's robot; used as
they are, your robot will thrash.**

### 3. Flash the Arduino and walk

Set the jumper back to **A (UART → SERVO)** and connect the board's UART header (TX /
RX / GND) to the Arduino's D1 / D0 / GND with three wires (**RX to RX, TX to TX**; see
"Things to know before wiring" in {doc}`bom`).

```bash
pio run -d code/13_quadruped -t upload
pio device monitor -d code/13_quadruped -b 115200
```

Type the commands in the serial monitor, **in this order**:

1. `iktest` — checks the FK/IK round trip without moving the legs
2. **With the robot hanging**, `stand` — rises to the home pose in 2 s. All four legs
   should look the same; if one is mirrored, that leg's sign is reversed
3. Still hanging, `rl 0.06 0` — moves the legs with the trained policy
4. Put it on the floor and `rl 0.12 0` (`rl <forward m/s> <turn rad/s>`). `stop` holds
   the home pose; `free` turns the torque off

While it walks, a line like this is printed every second:

```
loop avg 3210 us  max 6980 us  late 0/50  skipped 0  read_fail 0
```

`skipped` counts missed control periods (50 Hz) and `read_fail` servos that did not
answer; **both should stay at 0**. If they grow, suspect the wiring or the power.

```{warning}
- Power the 8 servos **from a battery**. Never from the PC's USB (each stalls at 2.7 A)
- Do `stand` and the first `rl` **with the robot hanging**. With a wrong sign or ID it
  does not walk badly — it thrashes
- Put rubber or silicone on the feet (bare plastic slips on hard floors)
```

## FAQ

**Can it get up after falling?** — No. With no IMU it cannot observe its own attitude
(even with training, the success rate was 1%). This is where adding an IMU pays off
most.

**Can it go faster?** — With 45 rpm servos and 0.19 m legs, 0.05–0.2 m/s is what the
hardware can do (0.20 m/s at the maximum command in simulation). The limit is the
no-load speed, not torque, so going faster means changing the servos or the leg length.
