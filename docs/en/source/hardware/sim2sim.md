# Train in Genesis, walk in MuJoCo (sim2sim)

The policy in {doc}`walk` is trained in MuJoCo (mjlab) and walks in the same MuJoCo.
This page trains the same task in **a different physics simulator, Genesis**, and
walks that policy **in MuJoCo in the browser**. Running a policy in a simulator other
than the one it was trained in is called **sim2sim**.

If a policy walks by leaning on quirks of the physics engine it was trained in (how
soft the contacts are, how friction is resolved, small differences in integration),
it stops walking when moved to another simulator. If it still walks there, that is
one more piece of confidence before taking it to the real robot (sim2real).

```{note}
The Genesis version is support-site-only material, not in the book. The policy
flashed to the robot is still the one from {doc}`walk` (trained in MuJoCo).
```

## Try it in the browser

The simulation below opens with "RL policy (trained in Genesis)" selected. **The
weights trained in Genesis run in the WebAssembly build of MuJoCo.** The physics is
the same as in {doc}`walk` (only the four toe spheres touch the floor; the servos are
position control plus back-EMF viscous damping; commands arrive 20–35 ms late), and
so are the policy's inputs and outputs (87 observations, 8 joints). Switch Control to
"RL policy" to compare with the policy trained in MuJoCo.

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../../assembly/quadruped/walk/index.html?mode=genesis&lang=en"
     target="_blank" rel="noopener">Open the sim2sim simulation ↗</a>
</p>
<iframe src="../../assembly/quadruped/walk/index.html?mode=genesis&lang=en"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="Quadruped policy trained in Genesis, walking in MuJoCo"></iframe>
```

Measured by running the same MuJoCo WASM as the browser page under Node, 5 runs of
20 s per command (averaged over the last 10 s):

| Command | Forward [m/s] | Turn [rad/s] | Falls |
|---|---|---|---|
| forward 0.06 m/s | 0.057 | −0.026 | 0 / 5 |
| forward 0.09 m/s | 0.086 | 0.000 | 0 / 5 |
| forward 0.12 m/s | 0.110 | 0.022 | 0 / 5 |
| forward 0.15 m/s | 0.132 | 0.034 | 0 / 5 |
| turn 0.3 rad/s | −0.006 | 0.155 | 0 / 5 |

## The same policy in Genesis and in MuJoCo

`rl/genesis/sim2sim.py` walks one policy in both Genesis and MuJoCo with the same
commands and the same measurements. The MuJoCo side is the CPU trainer's environment
(`rl/cpu/quad_env.py`), the same physics as the browser page. Below is the
distributed policy (seed 1, iteration 2299), 64 robots × 20 s per command, speeds
averaged over the last 10 s.

| Command vx, wz | Genesis fwd / turn | MuJoCo fwd / turn | Falls (G / M) | Diagonal sync (G / M) | Slip [mm/s] (G / M) |
|---|---|---|---|---|---|
| 0.06, 0 | 0.061 / −0.015 | 0.057 / −0.023 | 0 / 0 | 0.81 / 0.80 | 17 / 27 |
| 0.09, 0 | 0.091 / −0.002 | 0.087 / 0.001 | 0 / 0 | 0.85 / 0.85 | 19 / 30 |
| 0.12, 0 | 0.113 / 0.012 | 0.111 / 0.024 | 0 / 0 | 0.89 / 0.85 | 21 / 30 |
| 0, 0.3 | 0.000 / 0.130 | −0.006 / 0.153 | 0 / 0 | 0.72 / 0.63 | 18 / 25 |
| 0.06, −0.3 | 0.053 / −0.153 | 0.047 / −0.168 | 0 / 0 | 0.80 / 0.80 | 21 / 28 |

Diagonal sync is the fraction of time the two diagonal pairs (front-left + rear-right,
front-right + rear-left) touch down and lift off together; a clean trot is close to 1.
Slip is the mean horizontal speed of the toes while they are on the ground.

- **Forward speed agrees within 0.006 m/s.** MuJoCo is slightly slower; at the
  0.06 and 0.09 m/s commands it falls 0.003 m/s short.
- **No robot falls in either.** With the training-time domain randomization (friction,
  mass, center of mass, servo gains and so on varied per robot) all 64 robots still
  stayed up in MuJoCo (0.082 m/s at the 0.09 m/s command).
- **Toe slip is about 1.5 times larger in MuJoCo** (about 20 → 30 mm/s). The contacts
  are resolved differently, and in MuJoCo the toes drift a little more.
- Both turn at about half the command (0.13–0.17 rad/s for 0.3 rad/s). That is a
  property of the Genesis policy itself.

### The other way: the MuJoCo policy in Genesis

The distributed MuJoCo policy (the one in {doc}`walk`) also walks when moved to
Genesis with the same script (32 robots × 12 s, no falls in either).

| Command vx, wz | Genesis fwd / turn | MuJoCo fwd / turn |
|---|---|---|
| 0.12, 0 | 0.117 / −0.002 | 0.120 / −0.008 |
| 0, 0.3 | −0.001 / 0.174 | −0.004 / 0.214 |
| 0.06, −0.3 | 0.047 / −0.187 | 0.046 / −0.225 |

At the 0.06 and 0.09 m/s commands this policy stayed standing without walking off,
in both simulators.

## Training in Genesis

The training code is in `13_quadruped/rl/genesis/`. It reads the task (observations,
the 26 reward terms, commands, terminations, domain randomization, PPO settings)
straight from the CPU trainer's `rl/cpu/task.py` and only replaces the physics with
Genesis on the GPU. The checkpoint format is the same as the mjlab and CPU trainers,
so the same exporter writes the robot header and the browser JSON.

```bash
cd 13_quadruped/rl/genesis               # from docs/os-on-arduino/code
uv sync                                   # genesis-world 1.4.4 + rsl-rl-lib 5.0.1 + mujoco 3.7.0
export ARDUINO_QUAD_HOME_HEIGHT=0.11 ARDUINO_QUAD_GAIT_PERIOD=0.32
uv run train.py --num-envs 4096 --iterations 2300 --seed 1
uv run sim2sim.py --checkpoint logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt

# robot header (.h / .npz / .json) and the browser's policy_genesis.json
uv run python ../../host/export_quad_policy.py \
    logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt outdir --backend genesis
uv run python ../../host/make_walk_bundle.py outdir \
    ../../../../docs/assembly/quadruped/walk/policy_genesis.json
```

On one RTX 4090, 4096 environments × 2300 iterations took **about 41 minutes**
(0.72–0.79 s per iteration, with two runs going at once on separate GPUs). Seed 2
learned to walk too, but its body swayed more (roll and pitch 4–5°, against 1–2° for
seed 1), so seed 1 is the one distributed.

`render.py` writes the walk to an mp4. The robot walks in MuJoCo (default) or Genesis
(`--sim genesis`), and either way MuJoCo draws the frames. On a machine without a
display, add `MUJOCO_GL=egl`.

```bash
MUJOCO_GL=egl uv run render.py \
    --checkpoint logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt --out walk.mp4
```

### Training on Google Colab

Even without a GPU of your own, a notebook takes you from training to export in the
browser.

```{raw} html
<p>
  <a href="https://colab.research.google.com/github/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/rl/colab/genesis_colab.ipynb"
     target="_blank" rel="noopener">
    <img src="https://colab.research.google.com/assets/colab-badge.svg"
         alt="Open In Colab"></a>
</p>
```

What the notebook does:

1. Checks the GPU (**Runtime → Change runtime type → T4 GPU**)
2. Fetches the code and installs the training stack (genesis-world + rsl_rl + MuJoCo)
3. **Walks the distributed MuJoCo policy in Genesis**, to check the environment is
   put together correctly
4. Runs 30 iterations on the GPU you were given to **measure the training speed** and
   estimate the total time
5. Trains (checkpoints go to Google Drive, so a dropped session can resume)
6. Walks the trained policy in both Genesis and MuJoCo to compare them, and **shows
   the walk as two videos side by side** (MuJoCo on the left, Genesis on the right)
7. Exports the robot's `.h` and the browser's `policy_genesis.json`

Put the exported `policy_genesis.json` in `docs/assembly/quadruped/walk/` and "RL policy
(trained in Genesis)" in the browser simulation above becomes your own policy.

### How it differs from the MuJoCo trainers

| | MuJoCo (mjlab, CPU version) | Genesis version |
|---|---|---|
| Physics | MuJoCo (mjlab: MuJoCo Warp on the GPU; CPU version: `mujoco.rollout`) | Genesis (GPU) |
| Task numbers | `rl/cpu/task.py` | reads the same file |
| Toe friction | the toe's value is used (`priority`) | Genesis takes the larger of the two, so the floor is set to the minimum 0.01 and the toe's value applies |
| 0 rad command right after a reset, rewards one physics step stale | reproduced from mjlab (`rl/cpu/README.md`) | not reproduced (they are details of mjlab's implementation, not of the robot) |
| Rough ground, ERFI | available (environment variables) | not available (asking for them stops with an error) |

```{note}
With `uv run ../../host/export_quad_policy.py` (no `python` in between), uv treats
`host/`, where the script lives, as a separate project and runs it in an environment
without torch, which fails. Write `uv run python ...`.
```

## References

- Genesis (genesis-world 1.4.4): <https://pypi.org/project/genesis-world/1.4.4/>
- Where a contact's friction is set to the larger of the two: `genesis/engine/solvers/rigid/collider/contact.py`
  in genesis-world 1.4.4
