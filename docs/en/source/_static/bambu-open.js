// 「Bambu Studio で開く」ボタン
//
// Bambu Studio は URL スキームで渡された 3MF をダウンロードして、プロジェクト
// （配置・印刷設定ごと）として開く。ただし登録されるスキームが OS で違う。
//   Windows / Linux: bambustudio://open?file=<URL エンコードした URL>
//   macOS:           bambustudioopen://<URL エンコードした URL>
// （BambuStudio src/slic3r/GUI/GUI_App.cpp と src/platform/osx/Info.plist.in）
//
// ボタンは data-file に 3MF への相対パスを持ち、hidden で置いてある。ここで
// 絶対 URL に直して href を組み立ててから表示する。スクリプトが動かなければ
// ボタンは出ないまま（普通のダウンロードにすり替えることはしない）。
document.addEventListener("DOMContentLoaded", () => {
  const platform = navigator.userAgentData?.platform ?? navigator.platform ?? "";
  const isMac = /mac/i.test(platform);
  for (const a of document.querySelectorAll("a.bambu-open[data-file]")) {
    const fileUrl = encodeURIComponent(new URL(a.dataset.file, location.href).href);
    a.href = isMac
      ? `bambustudioopen://${fileUrl}`
      : `bambustudio://open?file=${fileUrl}`;
    a.hidden = false;
  }
});
