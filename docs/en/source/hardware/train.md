# Training the walking policy yourself

The policy that walks the chapter 13 quadruped works without any training if you use
[the distributed one](walk.md). This page covers **retraining it yourself** — the
starting point when you want to change the rewards, raise the speed limit or get a
different gait.

There are two ways in. With an NVIDIA GPU, use the **mjlab version**; without one, use
the **CPU version**, which runs the same task on plain MuJoCo — 2048 environments for
2300 iterations takes about 69 minutes on a six-core laptop. You can also run the mjlab
version on Google Colab (the free T4) instead. Whichever you train with, the checkpoint
format is the same and the same steps export the header for the real robot.

## How the training code is organised

Training runs on
[unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab)
(the [mjlab](https://github.com/mujocolab/mjlab) + rsl_rl PPO training framework).
`docs/os-on-arduino/code/13_quadruped/rl/` is **an overlay placed on top of** that
upstream; it is not a program that runs on its own.

| File | Contents |
|---|---|
| `robot_cfg.py` | Robot definition (actuators, initial pose, `home` angles) |
| `env_cfgs.py` | Observations, commands, domain randomisation |
| `rewards.py` | Reward terms (velocity tracking, gait, posture, energy, ...) |
| `rl_cfg.py` | PPO hyperparameters and the network [96, 64] |
| `runner.py` | Training runner with ERFI (torque disturbances) added |
| `scripts/` | Environment setup, training, playback, video export |
| `cpu/` | The CPU version that trains the same task without mjlab ("Training without a GPU" below) |

`setup.sh` clones the upstream into `.upstream/unitree_rl_mjlab` and places `rl/` as
`src/tasks/velocity/config/arduino_quad` with a **symbolic link**. The upstream
imports everything under `src/tasks/` automatically, so that alone registers the
following four tasks.

| Task ID | Purpose |
|---|---|
| `ArduinoQuad-Flat` | Flat ground, plain velocity recipe (to check the setup) |
| `ArduinoQuad-Walk` | Flat ground + gait shaping (**the main one; this is the trot**) |
| `ArduinoQuad-Robust` | Same as Walk but with perturbed initial states (hardening before the real robot) |
| `ArduinoQuad-Recovery` | Getting up from a fallen pose |

## Training on Google Colab (if you have no GPU)

A notebook that takes you from environment setup to exporting the Arduino header,
in the browser alone.

```{raw} html
<p>
  <a href="https://colab.research.google.com/github/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/rl/colab/arduino_quad_colab.ipynb"
     target="_blank" rel="noopener">
    <img src="https://colab.research.google.com/assets/colab-badge.svg"
         alt="Open In Colab"></a>
</p>
```

What the notebook does (its explanations are in Japanese):

1. Check the GPU (**Runtime → Change runtime type → T4 GPU**)
2. Fetch the code and install the training environment (mjlab + MuJoCo Warp + rsl_rl)
3. **Play back the distributed trained policy as a video** — by this point you know the
   simulator, the policy and the export all work together
4. Run 30 iterations on the assigned GPU to **measure the training speed** and estimate
   the time needed
5. Train (checkpoints are saved to Google Drive)
6. Resume from where you left off if the session drops
7. Check the trained policy in a video and export it to `arduino_quad_policy.h`

```{note}
Colab's free tier drops the session after a few hours. If you keep the training logs on
Google Drive, `--agent.resume True` resumes as many times as you like. Section 6 of the
notebook sets this up.
```

### How long it takes on the free T4

Measured on 2026-08-31 on Colab's free tier (Tesla T4 15 GB, Python 3.13), running the
whole thing from setup to exporting the `.h`.

| | |
|---|---|
| Environment setup (`setup.sh`) | about 1 min |
| Training (2048 environments) | **1.42 s/iteration, 34,900 steps/s** |
| Time for the book's 4,500 iterations | **about 1.8 hours** |
| Policy playback (300-step video) | 5–6 min the first time (including GPU kernel generation), 3–4 min after that |
| Exporting the `.h` | about 1 min |

For comparison, the same settings on an RTX 4090 ran at 0.77 s/iteration and 63,700
steps/s. **The T4 is a little over half as fast as the 4090**, so even the free tier
finishes a book-sized training run in a realistic time.

### How many iterations until it walks

With the notebook's default settings (`ArduinoQuad-Walk`, 2048 environments) trained
for 1500 iterations, each checkpoint every 100 iterations was **played back for 6 s
at a command of 0.09 m/s and measured** (RTX 4090, one seed).

| Iteration | Measured forward [m/s] | Iteration | Measured forward [m/s] |
|---|---|---|---|
| 0 | −0.000 | 800 | 0.086 |
| 100 | **−0.219** | 900 | 0.071 |
| 200 | −0.194 | 1000 | 0.072 |
| 300 | 0.005 | 1100 | 0.096 |
| 400 | 0.014 | 1200 | 0.072 |
| 500 | 0.046 | 1300 | 0.086 |
| 600 | 0.046 | 1400 | 0.101 |
| 700 | 0.058 | 1499 | **0.089** |

**At 100–200 iterations it walks backwards.** It learns "don't fall over" before it
picks up the forward reward; that is not a failure. It turns forward around 300,
reaches the commanded speed around 800, and from there tracks it while swinging
between 0.07 and 0.10. Each point is a single episode, so ±0.02 m/s between
neighbouring points is within the noise.

```{note}
This is **a different policy trained with the default settings**, not a reproduction of
[the distributed policy](walk.md) (home height 0.11 m, gait period 0.32 s, 3999
iterations, 0.120 m/s at a 0.12 m/s command). The exported header records the home
angles used in training, so it stays consistent with the real robot as it is.
```


## Training on your own GPU

```bash
cd docs/os-on-arduino/code/13_quadruped
./rl/scripts/setup.sh                    # clone the upstream, place the overlay, install dependencies
source rl/scripts/env.sh                 # tell it where the robot's MJCF is
./rl/scripts/train.sh ArduinoQuad-Walk --env.scene.num-envs=4096
```

`setup.sh --no-install` only clones and places the files, skipping the dependencies.

### Pinned versions

`setup.sh` installs the dependencies **with pinned versions**. With what the upstream
(unitree_rl_mjlab) `setup.py` points to, this robot's configuration does not load.

| | | Why it is pinned |
|---|---|---|
| mjlab | 1.3.0 | 1.2.0 lacks the servos' back-EMF (`viscous_damping`) and the 27 ms command delay (`delay_min/max_lag`). The latter is key to sim2real and cannot be dropped |
| mujoco-warp | 3.7.0.1 | The version mjlab 1.3.0 requires |
| mujoco | 3.7.0 | With the latest version, importing mujoco-warp fails |
| warp-lang | 1.14.0 | With 1.16, kernel generation fails at the start of training |
| scipy | 1.15 or later | mjlab 1.3.0 uses it without declaring it |

`setup.sh` also applies a small compatibility patch to the cloned checkout that restores
`update_assets` (removed in mjlab 1.3.0), which the upstream robot definitions use.
Without it, all of `src/assets/robots` fails with ImportError and takes the
`ArduinoQuad-*` registration down with it.

This combination was **checked end to end, from setup to exporting the `.h`, on an RTX
4090 on 2026-08-31** (0.77 s/iteration and 63,700 steps/s with 2048 environments).

To watch the trained policy:

```bash
./rl/scripts/play.sh ArduinoQuad-Walk    # opens the viewer (needs a display)
```

On a server or Colab with no display, write an mp4 instead of opening the viewer:

```bash
source rl/scripts/env.sh
cd "$ARDUINO_QUAD_UPSTREAM"
python "$ARDUINO_QUAD_ROOT/rl/scripts/record_video.py" \
    --ckpt logs/rsl_rl/arduino_quad_velocity/<run>/model_1500.pt \
    --vx 0.09 --steps 300 --out walk.mp4
```

With `--bundle`, instead of a checkpoint it plays back **an exported policy** (the `.npz`
+ `.json` in `13_quadruped/`; pass the `13_quadruped` folder, as in
`--bundle "$ARDUINO_QUAD_ROOT"`) with the same numpy implementation as the real robot.

## Training without a GPU (the CPU version)

`rl/cpu/` trains the same tasks (`ArduinoQuad-Walk` / `-Robust`) on **plain MuJoCo**,
without mjlab. The physics runs on the CPU through `mujoco.rollout` (a C++ thread pool)
and PPO uses the same rsl-rl-lib 5.0.1 as the mjlab version. The network updates alone
can be put on a GPU.

```bash
cd docs/os-on-arduino/code/13_quadruped/rl/cpu
uv sync                                   # mujoco 3.7.0 + rsl-rl-lib 5.0.1 + torch
uv run train.py                           # ArduinoQuad-Walk, 2048 environments, CPU
uv run train.py --device cuda             # physics stays on the CPU, updates on the GPU
uv run evaluate.py --checkpoint logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt
```

The mjlab version (`rl/scripts/train.sh`) is still there. Both are the same task and the
checkpoint format is the same, so **either one can resume training from the other's
checkpoints, and the same exporter writes the header**. Add `--backend cpu` when
exporting a checkpoint trained with the CPU version.

```bash
uv run ../../host/export_quad_policy.py \
    logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt <output directory> --backend cpu
```

```{note}
On a server with no display, add `MUJOCO_GL=egl` when using `evaluate.py --video`.
Without it MuJoCo cannot create a GL context and fails while constructing the
`Renderer`.
```

### How long it takes

Measured on a laptop (Core i9-8950HK, 6 cores / 12 threads, 2018).

| Environments | Physics (24 steps) | One iteration (including the PPO update, CPU) |
|---|---|---|
| 2048 | 0.78 s | 1.55 s |
| 4096 | 1.50 s | 3.13 s |

That is about 63,000 env-steps/s, roughly the same as the mjlab version on an RTX 4090
(63,700 steps/s). On the same laptop, 2048 environments for 2300 iterations took
**68.9 minutes** end to end (1.80 s/iteration). The 1.55 s above is the benchmark alone;
real training also writes logs and checkpoints.

### How many iterations until it walks

From that run (`ARDUINO_QUAD_HOME_HEIGHT=0.11 ARDUINO_QUAD_GAIT_PERIOD=0.32`, 2048
environments, one seed), each checkpoint every 100 iterations was played back with
`evaluate.py` at **a command of 0.09 m/s, 32 environments, 12 s each**. Contact ratio is
the fraction of time each of the four feet is on the ground (min–max), diagonal sync is
the fraction of time the diagonal pair touches down and lifts off together, and slip is
the horizontal foot speed while in contact.

| Iteration | Forward [m/s] | Contact ratio | Diagonal sync | Slip [mm/s] | Falls |
|---|---|---|---|---|---|
| 0 | 0.000 | 0.00–1.00 | 0.00 | 0 | 0 |
| 100 | — | — | — | — | all |
| 200 | — | — | — | — | all |
| 300 | −0.003 | 0.00–0.99 | 0.33 | 19 | 0 |
| 400 | 0.036 | 0.21–0.86 | 0.44 | 75 | 0 |
| 600 | 0.026 | 0.28–0.82 | 0.31 | 79 | 0 |
| 800 | 0.088 | 0.38–0.78 | 0.53 | 73 | 0 |
| 1000 | 0.089 | 0.38–0.78 | 0.56 | 68 | 0 |
| 1500 | 0.088 | 0.36–0.77 | 0.55 | 62 | 0 |
| 1800 | 0.092 | 0.46–0.72 | 0.65 | 45 | 0 |
| 2000 | 0.090 | 0.46–0.67 | 0.69 | 41 | 0 |
| 2299 | 0.089 | 0.47–0.68 | 0.70 | 41 | 0 |

**At 100–200 iterations every robot falls over.** It cannot stand yet; this is the
stretch where it learns not to fall. It stops falling at 300, drifts sideways while
trying to move forward at 400–600 (the yaw rate reaches 0.36 rad/s there), and reaches
the commanded speed around 800.

**The speed plateaus at 1000 iterations, but the gait keeps improving until 2300.** The
four feet even out (contact ratio 0.38–0.78 → 0.47–0.68), the diagonal sync rises from
0.53 to 0.70 and the slip drops from 73 to 41 mm/s. The step up around 1500–1800 comes
right after the weight of `trot_guidance` (the reward that teaches the gait) reaches 0
at 1400 iterations. Stopping training by looking at the forward speed alone throws this
stretch away.

```{note}
That the CPU version is the same task as the mjlab one is checked by
`rl/cpu/parity_check.py`: it runs both from the same initial state with the same action
sequence and compares the joint angles, the observations and all 26 reward terms step by
step. How to run it, and the differences that remain, are in `rl/cpu/README.md`.
```

## Taking it to the real robot

Export the Arduino header from a checkpoint.

```bash
cd "$ARDUINO_QUAD_UPSTREAM"
python "$ARDUINO_QUAD_ROOT/host/export_quad_policy.py" \
    logs/rsl_rl/arduino_quad_velocity/<run>/model_1500.pt \
    <output directory> ArduinoQuad-Walk
```

It produces three files.

| File | Where it is used |
|---|---|
| `arduino_quad_policy.h` | Firmware (replace the one in `13_quadruped/include/`) |
| `arduino_quad_policy.npz` | The PC-direct version (`13_quadruped/host/quad_host.py`) |
| `arduino_quad_policy.json` | The same information in machine-readable form |

Besides the weights, it reads **the observation order, the history order, the
normalisation statistics, the home angles and the action scale** from the training
environment and writes them in. Copying these by hand gives a robot that "just
trembles" without any error. After exporting, it checks the numpy implementation
against PyTorch's output.

For running it on the robot, see "Walking the real robot" in {doc}`walk`. **Always hang
the robot first** before moving it.

## Common pitfalls

| Symptom | Cause and fix |
|---|---|
| It stops asking you to log in to wandb | mjlab's default logger is wandb. Add `--agent.logger tensorboard` |
| `MJCF が見つかりません` (MJCF not found) | You forgot `source rl/scripts/env.sh` (`$ARDUINO_QUAD_XML`) |
| `play.sh` hangs with no display | It is trying to open the viewer. Use `record_video.py` |
| `home 姿勢が環境と方策で違います` (home pose differs between environment and policy) | The policy and the environment were trained with different settings. Re-run with the `ARDUINO_QUAD_HOME_HEIGHT=...` the message suggests |
| Training converges to a policy that "stands still" | The commanded speed is unreachable. On this robot, 0.05–0.09 m/s fits within the servos' headroom |

(We will add to this as readers ask. Questions are welcome on
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).)
