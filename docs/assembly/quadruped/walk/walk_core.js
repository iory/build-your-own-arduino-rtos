// 学習済み方策 (87 -> [96, 64] -> 8, ELU) と観測ベクトルの組み立て。
// host/quad_policy.py の JS 移植で、同じ契約に従う:
//   - 各観測項は履歴 3 段を持ち、古い順に並ぶ
//   - 初回 push は全スロットを同じ値で埋める (mjlab の CircularBuffer と同じ)
//   - 歩容位相は |cmd| < 0.1 のとき 0 固定
//   - サーボ目標 = default_q + action_scale * action

export class QuadPolicy {
  constructor(bundle) {
    this.meta = bundle.meta;
    this.obsMean = Float32Array.from(bundle.obs_mean);
    this.obsStd = Float32Array.from(bundle.obs_std);
    this.defaultQ = Float32Array.from(bundle.default_joint_pos);
    this.actionScale = Float32Array.from(bundle.action_scale);
    this.layers = [];
    for (let i = 0; i < bundle.n_layers; i++) {
      const w = bundle['w' + i];
      this.layers.push({
        w: Float32Array.from(w.flat()),
        rows: w.length, cols: w[0].length,
        b: Float32Array.from(bundle['b' + i]),
      });
    }
    this.nj = this.meta.act_dim;
    this.obsDim = this.meta.obs_dim;
    this.dt = this.meta.control_dt;
    this.gaitPeriod = this.meta.gait_period_s;
    this.jointNames = this.meta.action_joint_order;
    this.layout = {};
    for (const e of this.meta.obs_layout) this.layout[e.term] = e;
    this.hist = this.layout.joint_pos.history;
    this.terms = ['command', 'phase', 'joint_pos', 'joint_vel', 'actions']
        .filter(t => t in this.layout);
    this.clip = this.meta.clip_actions;
    this.reset();
  }

  reset() {
    const h = this.hist, nj = this.nj;
    this.buf = {
      command: this._zeros(h, 3), phase: this._zeros(h, 2),
      joint_pos: this._zeros(h, nj), joint_vel: this._zeros(h, nj),
      actions: this._zeros(h, nj),
    };
    this.head = h - 1;
    this.filled = 0;
    this.lastAction = new Float32Array(nj);
    this.stepI = 0;
  }

  _zeros(h, n) {
    return Array.from({length: h}, () => new Float32Array(n));
  }

  _push(vals) {
    this.head = (this.head + 1) % this.hist;
    for (const k in vals) this.buf[k][this.head].set(vals[k]);
    if (this.filled === 0) {
      for (const k in vals) {
        for (let s = 0; s < this.hist; s++) this.buf[k][s].set(vals[k]);
      }
    }
    this.filled = Math.min(this.filled + 1, this.hist);
  }

  phase(t, cmd) {
    const norm = Math.hypot(cmd[0], cmd[1], cmd[2]);
    if (norm < 0.1) return [0, 0];
    const ph = ((t % this.gaitPeriod) + this.gaitPeriod) % this.gaitPeriod
        / this.gaitPeriod;
    return [Math.sin(ph * 2 * Math.PI), Math.cos(ph * 2 * Math.PI)];
  }

  // q, qd: 方策順の関節角 [rad] / 角速度 [rad/s]。cmd: [vx, vy, wz] (vy は 0)。
  // 返り値: 関節目標角 [rad]。
  step(q, qd, cmd) {
    const t = this.stepI * this.dt;
    const dq = new Float32Array(this.nj);
    for (let i = 0; i < this.nj; i++) dq[i] = q[i] - this.defaultQ[i];
    this._push({
      command: cmd, phase: this.phase(t, cmd),
      joint_pos: dq, joint_vel: qd, actions: this.lastAction,
    });

    const obs = new Float32Array(this.obsDim);
    for (const key of this.terms) {
      const e = this.layout[key];
      let o = e.offset;
      for (let s = 0; s < this.hist; s++) {
        const slot = this.buf[key][(this.head + 1 + s) % this.hist];
        obs.set(slot, o);
        o += e.size_per_step;
      }
    }

    let x = new Float32Array(this.obsDim);
    for (let i = 0; i < this.obsDim; i++) {
      x[i] = (obs[i] - this.obsMean[i]) / this.obsStd[i];
    }
    for (let li = 0; li < this.layers.length; li++) {
      const {w, rows, cols, b} = this.layers[li];
      const y = new Float32Array(rows);
      for (let r = 0; r < rows; r++) {
        let acc = b[r];
        const base = r * cols;
        for (let c = 0; c < cols; c++) acc += w[base + c] * x[c];
        y[r] = (li < this.layers.length - 1)
            ? (acc > 0 ? acc : Math.expm1(Math.min(acc, 0)))   // ELU
            : acc;
      }
      x = y;
    }
    if (this.clip) {
      for (let i = 0; i < this.nj; i++) {
        x[i] = Math.max(-this.clip, Math.min(this.clip, x[i]));
      }
    }
    this.lastAction = Float32Array.from(x);
    this.stepI += 1;

    const targets = new Float32Array(this.nj);
    for (let i = 0; i < this.nj; i++) {
      targets[i] = this.defaultQ[i] + this.actionScale[i] * x[i];
    }
    return targets;
  }
}

// MuJoCo の model/data に方策を接続する。qpos/qvel のインデックスは
// 関節名から引く (方策の出力順とアクチュエータ順は XML で一致している)。
export function makeController(mujoco, model, data, policy) {
  const qadr = [], vadr = [];
  for (const name of policy.jointNames) {
    const j = model.jnt(name);
    qadr.push(Number(j.qposadr[0] !== undefined ? j.qposadr[0] : j.qposadr));
    vadr.push(Number(j.dofadr[0] !== undefined ? j.dofadr[0] : j.dofadr));
    j.delete?.();
  }
  const nSub = Math.max(1, Math.round(policy.dt / model.opt.timestep));
  const q = new Float32Array(policy.nj), qd = new Float32Array(policy.nj);
  return {
    nSub,
    // 1 制御周期ぶん進める: 観測 -> 方策 -> ctrl 書き込み -> 物理 nSub 回
    controlStep(cmd) {
      for (let i = 0; i < policy.nj; i++) {
        q[i] = data.qpos[qadr[i]];
        qd[i] = data.qvel[vadr[i]];
      }
      const targets = policy.step(q, qd, cmd);
      for (let i = 0; i < policy.nj; i++) data.ctrl[i] = targets[i];
      for (let s = 0; s < nSub; s++) mujoco.mj_step(model, data);
    },
  };
}
