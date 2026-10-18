// 面接練習ページの設定（高校卒業程度版）
// 現在の合言葉は「otsu-koukou2026」です。
// 変更方法：index.html を「index.html#setup」で開き、新しい合言葉を入力して表示された passHash を下に貼り付けます。
window.APP_CONFIG = {
  title: '大津町 二次面接練習（高卒）',
  passHash: '21trlx7jeqi',
  defaultSeconds: 60,

  // ---- AI採点・成績の記録（Google Apps Script）。使わない場合は空のままにします ----
  // すでに大卒版で設定ずみの場合は、大卒版の config.js から endpoint と appToken をそのままコピーして使えます。
  endpoint: '',
  appToken: ''
};
