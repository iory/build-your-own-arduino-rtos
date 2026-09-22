# Training the walking policy yourself

The policy that walks the chapter 13 quadruped works without any training if you use
[the distributed one](walk.md). This page covers **retraining it yourself** — the
starting point when you want to change the rewards, raise the speed limit or get a
different gait.

Training needs an NVIDIA GPU. **If you do not have one, you can do the whole thing on
Google Colab (the free T4).**

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
[the distributed policy](walk.md) (home height 0.11 m, gait period 0.32 s, 3498
iterations, 0.115 m/s at a 0.12 m/s command). The exported header records the home
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
