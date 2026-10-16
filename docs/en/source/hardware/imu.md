# Balancing with an IMU

The policy in {doc}`walk` sees only joint angles and joint velocities. When the body
tilts or gets pushed into a spin, nothing in its observation says so directly.

This page puts an **IMU** (inertial measurement unit, a sensor for the body's tilt and
rotation rate) on the front of the body and walks with a policy trained on its
readings as well. When pushed, the robot braces with its legs and brings the body
back, and while stopped it keeps standing instead of just locking its joints.

```{note}
The IMU version is not in the book; it exists only on this support site. A robot
without an IMU keeps walking with the policy from {doc}`walk`. Which one you get is
decided only by the firmware build you upload.
```

## What changes

| | Without IMU ({doc}`walk`) | IMU version |
|---|---|---|
| Observation | 87 values (command, gait phase, joint angles, joint velocities, previous action, 3 steps of history each) | **105 values**: the 87 above plus the body's **angular velocity** (3) and **gravity direction** (3), 3 steps of history each |
| Training | Walking on flat ground | Walking on flat ground, then finished with the training pushes made 3× stronger |
| When pushed | Cannot see the body's tilt | Sees tilt and rotation and braces with its legs to recover |
| When stopped (`stop`) | Locks the joints at the home pose (the standing pose it starts walking from) | Keeps running the policy at zero velocity (**balance**), so it still braces when pushed |
| Network and control rate | Fully connected [96, 64], 50 Hz | Same |

The gravity direction is a unit vector saying "which way is down, seen from the body".
Standing level it is (0, 0, −1). Lowering the head makes x (forward) positive;
lowering the right side makes y (left) negative.

## Push it in the browser

The simulation from "Try it in the browser" in {doc}`walk` can run the IMU policy too.
The one below opens with "RL policy (with IMU)" at zero forward
speed. **Push** gives the body a sudden velocity in a random direction, as
large as the Strength slider says. Switch Control to "RL policy" (no IMU)
and push the same way to compare. When the robot falls the simulation stops, and the
bottom right shows how many times it was pushed and how many times it fell.

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../../assembly/quadruped/walk/index.html?mode=imu&vx=0&lang=en"
     target="_blank" rel="noopener">Open the IMU simulation ↗</a>
</p>
<iframe src="../../assembly/quadruped/walk/index.html?mode=imu&vx=0&lang=en"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="Quadruped IMU push simulation"></iframe>
```

Falls out of 60 pushes each, standing at zero forward speed in the same simulation:

| Push | Without IMU | IMU version |
|---|---|---|
| 1.2 m/s | 3 | 2 |
| 1.6 m/s | 6 | 6 |
| 2.0 m/s | 18 | 6 |
| 2.4 m/s | 25 | 12 |

Training pushes reach at most 0.75 m/s even for the IMU version, but in the
simulation the feet slide away along the floor, so neither policy falls below about
1 m/s. The difference shows from about 2 m/s. While standing, the policy without the
IMU also stays tilted by about 6°; the IMU version stands almost exactly level.

Pushed **while walking** (0.12 m/s forward), on the other hand, it does no better: at
1.6 m/s the IMU version fell more often (out of 60: 32 without the IMU, 41 with it).
What the IMU policy gained is bracing while standing.

## What you need

On top of the parts in {doc}`bom` (Feetech version) or {doc}`krs_bom` (KRS version), two things:

| | |
|---|---|
| IMU board | A board carrying a QMI8658 (a 6-axis IMU from QST: 3-axis accelerometer + 3-axis gyro), I2C address **0x6B** |
| Cable | One Qwiic cable (a 4-pin I2C connector, 3.3 V), plugged into the UNO R4 WiFi's Qwiic connector |

The robot used for this site carries a custom sensor board with a QMI8658. This board is planned to go on sale.

Mount the board **on the 45° face at the front of the body, with its 4-pin connector
pointing down**. The policy has to receive its readings in the same frame it was
trained in, so the firmware assumes this orientation and rotates the chip axes into
the body axes (x forward, y left, z up) with `R_BODY_CHIP` in
`code/13_quadruped/src/quad_imu.cpp`. If you use a different board or orientation,
change it there; "Checking the orientation" below tells you whether it is right.

## Uploading

Follow "Walking the real robot" in {doc}`walk`, but add **`_imu`** to the name of the
build target (the PlatformIO env).

```bash
cd code
pio run -d 13_quadruped -e uno_r4_wifi_rcb4_imu -t upload   # Kondo KRS (RCB-4mini) version
pio run -d 13_quadruped -e uno_r4_wifi_imu -t upload        # Feetech version
```

Over WiFi, use `uno_r4_wifi_rcb4_udp_imu` / `uno_r4_wifi_udp_imu`. The `_imu` targets
use `include/arduino_quad_policy_imu.h` instead of `include/arduino_quad_policy.h` as
the policy and include the code that reads the IMU.

```{warning}
For about 10 seconds after power-on the firmware measures the gyro's zero point.
**Do not move the robot during that time.** The boot message
`IMU: chip acc[g] ...` means it succeeded.
```

If the IMU is not found or calibration fails, the firmware prints
`!! IMU 無しで動かす` ("running without the IMU") and feeds the policy the readings of
a robot standing still and level (angular velocity 0, gravity (0, 0, −1)). Each
once-a-second status line then ends with `imu=level`. On flat ground it still walks
like this, but tilts and pushes no longer reach the policy.

## Checking the orientation

Before walking, type `imu` in the serial monitor (115200 baud) and check the values.
`body g` is the gravity direction seen from the body; `target rad` is the joint
targets the policy produced.

1. With the robot on the floor, `imu`. `body g` should be close to `0 0 -1`
2. Lower the head and type `imu`: the first value of `body g` (x) should be
   **positive**. Lower the right side and type `imu`: the second value (y) should be
   **negative**. If either is reversed, the board orientation and `R_BODY_CHIP` do
   not match
3. **Lift the robot so its feet are off the floor**, hold it level and send `stop`.
   Then tilt it, typing `imu` each time: the legs should move and `target rad`
   should change. If it does not change, the IMU readings are not reaching the policy

The policy never trained with its feet in the air, so how the legs move in step 3
means nothing; only whether they move does. These are the values from step 3 on the
KRS version (order: FL_hip, FL_knee, RL_hip, RL_knee, RR_hip, RR_knee, FR_hip,
FR_knee):

| Held | `body g` | `target rad` |
|---|---|---|
| Level | −0.04 0.00 −1.00 | 1.11 −1.77 1.28 −1.76 1.27 −1.73 1.17 −1.77 |
| Head down about 45° | 0.71 −0.01 −0.71 | 1.10 −1.16 0.57 −1.59 0.94 −1.73 0.54 −1.81 |
| Right side down about 50° | 0.04 −0.78 −0.63 | 0.98 −1.41 0.83 −1.52 0.98 −1.77 0.87 −1.63 |

## Walking and pushing

The commands are the same as in {doc}`walk`. Suspend the robot for the first try.

| Command | What it does |
|---|---|
| `rl 0.1 0` | Walk forward. The second number is the turn rate (rad/s) |
| `rl 0 0` | Stand in place, bracing when pushed |
| `stop` | Stop into balance (keep running the policy at zero velocity) |
| `stand` | Switch the policy off and lock the joints at the home pose |
| `imu` | Print the angular velocity, gravity direction and joint targets once |

The keyboard control in `host/quad_host.py serial` / `wifi` works unchanged; the
space bar stops the robot into balance.

On the KRS version, pushing the robot from the side and from the front and back
during `rl 0 0` tilted the body by up to 25°; it braced with its legs, came back,
and did not fall.

```{note}
Over WiFi the robot keeps walking at the last velocity it received for **5 seconds**
after commands stop arriving, then stops (into balance on the IMU version). WiFi
packets can arrive late in bursts, and stopping right away made the robot stop and
restart over and over, which looked jerky. The cost is that it keeps walking for 5
seconds if the PC goes away (about 50 cm at 0.1 m/s), so give it room.
```

## Training the policy yourself

In the same setup as "Training on your own GPU" in {doc}`train`, setting the
environment variable `ARDUINO_QUAD_IMU=full` adds the angular velocity and gravity
direction to the policy's observation. The distributed policy was trained for 3000
iterations of walking, then continued for 1000 iterations in `ArduinoQuad-Robust`
with the training pushes made 3× stronger (`ARDUINO_QUAD_PUSH_SCALE=3`).

```bash
cd 13_quadruped
source rl/scripts/env.sh
export ARDUINO_QUAD_IMU=full

# 1. Learn to walk
./rl/scripts/train.sh ArduinoQuad-Walk --env.scene.num-envs=4096 \
    --agent.max-iterations 3000

# 2. Make the pushes 3x stronger and continue from the policy of step 1
ARDUINO_QUAD_PUSH_SCALE=3 ./rl/scripts/train.sh ArduinoQuad-Robust \
    --env.scene.num-envs=4096 --agent.max-iterations 1000 \
    --agent.resume True --agent.load-run <run of step 1> \
    --agent.load-checkpoint <last checkpoint of step 1>
```

`<run of step 1>` is the folder step 1 created under `logs/rsl_rl/arduino_quad_velocity/`,
and `<last checkpoint of step 1>` is the `model_*.pt` with the highest number in it.

| Environment variable | Meaning | Default |
|---|---|---|
| `ARDUINO_QUAD_IMU` | `none` (no IMU) / `gyro` (angular velocity only) / `full` (angular velocity + gravity direction) | `none` |
| `ARDUINO_QUAD_PUSH_SCALE` | Multiplier on how hard the robot is pushed during training | 1 |
| `ARDUINO_QUAD_IMU_TILT_DEG` | Randomise the board's mounting tilt by up to this many degrees | 0 |
| `ARDUINO_QUAD_IMU_GYRO_BIAS` | Randomise the gyro's zero offset by up to this many rad/s per axis | 0 |
| `ARDUINO_QUAD_IMU_DELAY_MAX` | Delay the IMU readings by 0 to this many control steps (20 ms each) | 0 |

The last three only disturb what the policy (actor) sees; the value function (critic)
still trains on the exact values.

Keep `ARDUINO_QUAD_IMU=full` set when exporting too. The observation layout is read
out of the training environment, so forgetting it exports the layout without the IMU.
Rename the resulting `arduino_quad_policy.h` to `include/arduino_quad_policy_imu.h`
and the `_imu` targets will use it.

```bash
cd "$ARDUINO_QUAD_UPSTREAM"
ARDUINO_QUAD_IMU=full python "$ARDUINO_QUAD_ROOT/host/export_quad_policy.py" \
    logs/rsl_rl/arduino_quad_velocity/<run of step 2>/<last checkpoint of step 2> \
    <output directory> ArduinoQuad-Robust
```

```{note}
The CPU trainer ("Training without a GPU" in {doc}`train`) does not support the IMU
version yet. Its policy observation is fixed to the 87 values without the IMU.
```

## Not yet

- **Getting up after a fall** is not trained in the IMU version either.
- **Slopes and tilted floors** were never in training. The training floor is always
  level, so do not expect it to keep the body level on a slope.
- **Pushes while walking**: as "Push it in the browser" above shows, the IMU version
  does no better than the policy without it in simulation.
- Only the KRS version (USB and WiFi) has been checked on hardware. The Feetech
  `_imu` targets have only been checked to build.
