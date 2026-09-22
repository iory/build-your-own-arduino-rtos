// 仮想 UNO R4 WiFi（ブラウザ版）
//
// qemu-arduino-uno-r4 の WebAssembly ビルドを、このページの中で動かす。
// code/sim/board.py がやっていること（エミュレータの起動、LED の読み出し、
// シリアルの中継）を、サーバなしでブラウザだけで行う。
//
// QEMU とは wasm のヒープ（SharedArrayBuffer）を通して話す。起動すると
// QEMU が Module.unor4Attach() を呼び、SRAM・ポートの出力ラッチ・シリアルの
// リングの場所を教えてくれる（パッチ 0006 の「WebAssembly host interface」）。

// 実機と同じ RA4M1 のレジスタ／シンボル（code/sim/board.py と同じ値）
const FRAMEBUFFER_SYMBOL = '_ZL11framebuffer';   // Arduino_LED_Matrix の static framebuffer
const FRAMEBUFFER_BYTES = 12;                    // 96 LED = 12 バイト
const LED_D13_PORT = 1;                          // D13 = P102
const LED_D13_BIT = 1 << 2;

const POLL_MS = 16;                  // LED とシリアルを読む間隔
// QEMU が unor4Attach を呼ぶまでの待ち時間。これを過ぎたら、ホスト側の口を
// 持たない（パッチ 0006 より前の）QEMU だと判断して止める
const ATTACH_TIMEOUT_MS = 30000;
const CONSOLE_KEEP = 30000;          // シリアル画面に残す文字数
const CONSOLE_TRIM_AT = 40000;

// 章の一覧。dir は code/ の下のディレクトリ名、ELF は chapters/<dir>.elf に置く
const CHAPTERS = [
  { dir: '00_intro', title: '準備: 開発環境の確認' },
  { dir: '01_boot', title: '第1章: ブートシーケンス' },
  { dir: '02_baremetal', title: '第2章: ベアメタルからの出発' },
  { dir: '03_context_switch', title: '第3章: コンテキストスイッチの実装' },
  { dir: '04_scheduler', title: '第4章: プリエンプティブスケジューラ' },
  { dir: '05_shell', title: '第5章: 対話型シェル' },
  { dir: '06_memory_protection', title: '第6章: メモリ保護' },
  { dir: '07_led_matrix', title: '第7章: LEDマトリクス可視化' },
  { dir: '08_interpreter', title: '第8章: 簡易インタプリタ' },
  { dir: '09_integration', title: '第9章: 統合とロボット制御' },
  { dir: '10_freertos', title: '第10章: FreeRTOSで同じことをやってみる' },
  { dir: '11_tiny_python', title: '第11章: TinyPython' },
  { dir: 'adv1_sync', title: '応用編 第1章: ロックと同期' },
  { dir: 'adv2_syscall', title: '応用編 第2章: ユーザー／カーネルモードと SVC' },
  { dir: 'adv3_heap', title: '応用編 第3章: ヒープ自作' },
];
const DEFAULT_CHAPTER = '04_scheduler';

const $ = (id) => document.getElementById(id);

// ---- ELF から静的シンボルのアドレスを引く（board.py の find_symbol と同じ） ----
function findSymbol(buf, name) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  if (dv.getUint32(0) !== 0x7f454c46 || buf[4] !== 1) return null;   // ELF32 のみ
  const shoff = dv.getUint32(0x20, true);
  const shentsize = dv.getUint16(0x2e, true);
  const shnum = dv.getUint16(0x30, true);
  const section = (i) => {
    const off = shoff + i * shentsize;
    return {
      type: dv.getUint32(off + 4, true),
      offset: dv.getUint32(off + 0x10, true),
      size: dv.getUint32(off + 0x14, true),
      link: dv.getUint32(off + 0x18, true),
    };
  };
  const SHT_SYMTAB = 2;
  const want = new TextEncoder().encode(name);
  for (let i = 0; i < shnum; i++) {
    const sh = section(i);
    if (sh.type !== SHT_SYMTAB) continue;
    const strtab = section(sh.link).offset;
    for (let off = sh.offset; off < sh.offset + sh.size; off += 16) {
      const nameOff = dv.getUint32(off, true);
      if (nameOff === 0) continue;
      const start = strtab + nameOff;
      let match = buf[start + want.length] === 0;
      for (let k = 0; match && k < want.length; k++) match = buf[start + k] === want[k];
      if (match) return dv.getUint32(off + 4, true);
    }
  }
  return null;
}

// ---- 画面 ----
function setStatus(text, kind = '') {
  const el = $('status');
  el.textContent = text;
  el.dataset.kind = kind;
}

function appendConsole(text) {
  const el = $('console');
  const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 20;
  el.textContent += text;
  if (el.textContent.length > CONSOLE_TRIM_AT) {
    el.textContent = el.textContent.slice(-CONSOLE_KEEP);
  }
  if (atBottom) el.scrollTop = el.scrollHeight;
}

function showError(message) {
  setStatus('停止', 'error');
  const el = $('error');
  el.textContent = message;
  el.hidden = false;
}

async function placeLeds() {
  const cells = await (await fetch('matrix_cells.json')).json();
  const board = $('board');
  const make = (cls, cell) => {
    const el = document.createElement('div');
    el.className = 'led ' + cls;
    el.style.left = cell.x + '%';
    el.style.top = cell.y + '%';
    board.appendChild(el);
    return el;
  };
  return { pixels: cells.matrix.map((c) => make('px', c)), d13: make('d13', cells.d13) };
}

function selectedChapter() {
  const want = new URLSearchParams(location.search).get('ch') || DEFAULT_CHAPTER;
  return CHAPTERS.find((c) => c.dir === want) || null;
}

function fillChapterMenu(current) {
  const sel = $('chapter');
  for (const c of CHAPTERS) {
    const opt = document.createElement('option');
    opt.value = c.dir;
    opt.textContent = c.title;
    opt.selected = current && c.dir === current.dir;
    sel.appendChild(opt);
  }
  // QEMU は止め直せないので、章を変えるときはページごと読み込み直す
  sel.addEventListener('change', () => {
    const url = new URL(location.href);
    url.searchParams.set('ch', sel.value);
    location.href = url.href;
  });
}

// ---- QEMU とのやり取り ----
function makeLink(info, fbAddr, leds) {
  const heap = info.heap;                     // 呼ぶたびに今の HEAPU8 を返す
  const ringWords = info.rings >>> 2;
  const OUT_HEAD = 0, OUT_TAIL = 1, IN_HEAD = 2, IN_TAIL = 3, OUT_DROPPED = 4;
  const decoder = new TextDecoder('utf-8');
  const encoder = new TextEncoder();
  const words = () => new Int32Array(heap().buffer);
  let dropped = 0;

  function drainSerial() {
    const w = words();
    const head = Atomics.load(w, ringWords + OUT_HEAD) >>> 0;
    let tail = Atomics.load(w, ringWords + OUT_TAIL) >>> 0;
    const n = (head - tail) >>> 0;
    if (n === 0) return;
    // SharedArrayBuffer の上のビューは TextDecoder に渡せないので、普通の配列に写す
    const bytes = new Uint8Array(n);
    const h = heap();
    const base = info.rings + info.outOffset;
    for (let i = 0; i < n; i++, tail++) bytes[i] = h[base + (tail % info.outSize)];
    Atomics.store(w, ringWords + OUT_TAIL, tail | 0);
    appendConsole(decoder.decode(bytes, { stream: true }));

    const lost = Atomics.load(w, ringWords + OUT_DROPPED) >>> 0;
    if (lost !== dropped) {
      dropped = lost;
      $('dropped').textContent = `シリアル出力の取りこぼし: ${lost} バイト`;
      $('dropped').hidden = false;
    }
  }

  function send(text) {
    const bytes = encoder.encode(text);
    const w = words();
    let head = Atomics.load(w, ringWords + IN_HEAD) >>> 0;
    const tail = Atomics.load(w, ringWords + IN_TAIL) >>> 0;
    const room = info.inSize - ((head - tail) >>> 0);
    if (bytes.length > room) {
      appendConsole(`\n[入力が多すぎます: ${bytes.length} バイト中 ${room} バイトしか入りません]\n`);
      return;
    }
    const h = heap();
    const base = info.rings + info.inOffset;
    for (const b of bytes) h[base + (head++ % info.inSize)] = b;
    Atomics.store(w, ringWords + IN_HEAD, head | 0);
  }

  function drawLeds() {
    const h = heap();
    if (fbAddr !== null) {
      const off = info.sram + (fbAddr - info.sramBase);
      for (let p = 0; p < FRAMEBUFFER_BYTES * 8; p++) {
        leds.pixels[p].classList.toggle('on', ((h[off + (p >> 3)] >> (p & 7)) & 1) === 1);
      }
    }
    const podrAddr = info.podr + 2 * LED_D13_PORT;
    const podr = h[podrAddr] | (h[podrAddr + 1] << 8);
    leds.d13.classList.toggle('on', (podr & LED_D13_BIT) !== 0);
  }

  return { drainSerial, drawLeds, send };
}

async function main() {
  const chapter = selectedChapter();
  fillChapterMenu(chapter);
  if (!chapter) {
    showError('その章はブラウザでは動きません。一覧から選んでください。');
    return;
  }
  document.title = `仮想 UNO R4 WiFi — ${chapter.title}`;

  if (!self.crossOriginIsolated) {
    // coi-serviceworker が有効になるまでの最初の 1 回は、ここに来てから自動で読み込み直す
    setStatus('準備中…');
    if (!('serviceWorker' in navigator)) {
      showError('このブラウザは Service Worker を使えないため、エミュレータを動かせません'
                + '（SharedArrayBuffer にクロスオリジン分離が必要です）。');
    }
    return;
  }

  const leds = await placeLeds();
  setStatus('ファームウェアを読み込み中…');
  const elfRes = await fetch(`chapters/${chapter.dir}.elf`);
  if (!elfRes.ok) {
    showError(`chapters/${chapter.dir}.elf を読み込めませんでした（HTTP ${elfRes.status}）。`);
    return;
  }
  const elf = new Uint8Array(await elfRes.arrayBuffer());
  const fbAddr = findSymbol(elf, FRAMEBUFFER_SYMBOL);

  setStatus('QEMU を読み込み中…（初回は約 15 MB）');
  const createModule = (await import('./qemu/qemu-system-arm.js')).default;

  let link = null;
  const form = $('form');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!link) return;
    const input = $('line');
    link.send(input.value + '\n');
    input.value = '';
  });

  const attachTimer = setTimeout(() => {
    if (!link) {
      showError('QEMU がページとつながりませんでした。この QEMU には、ブラウザから'
                + 'シリアルと LED を扱う口（qemu-arduino-uno-r4 のパッチ 0006）が'
                + '入っていない可能性があります。');
    }
  }, ATTACH_TIMEOUT_MS);

  await createModule({
    // -serial none: シリアルは QEMU の中のリング経由（ページが読み書きする）。
    // -icount は付けない。WebAssembly の QEMU は命令をインタプリタで実行するので、
    // shift=4（48 MHz 相当に固定）だと実機の約 1/12 の速さになる。付けなければ
    // タイマと点滅は実時間どおりに進み、重い計算だけが実機より遅くなる。
    arguments: ['-M', 'arduino-uno-r4', '-kernel', '/fw.elf',
                '-display', 'none', '-serial', 'none', '-monitor', 'none'],
    preRun: [(m) => { m.FS.writeFile('/fw.elf', elf); }],
    print: (line) => console.log('[qemu]', line),
    printErr: (line) => {
      if (!line.includes('unsupported syscall')) console.warn('[qemu]', line);
    },
    unor4Attach: (info) => {
      clearTimeout(attachTimer);
      link = makeLink(info, fbAddr, leds);
      setInterval(() => { link.drainSerial(); link.drawLeds(); }, POLL_MS);
      setStatus('動作中', 'ok');
      $('line').disabled = false;
      $('send').disabled = false;
    },
    onAbort: (what) => showError(`QEMU が止まりました: ${what}`),
  });
}

main().catch((err) => {
  console.error(err);
  showError(`起動できませんでした: ${err.message || err}`);
});
