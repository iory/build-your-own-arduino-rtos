# FAQ・トラブルシューティング

## 書き込みできない

- **ポートが見えない**: ケーブルがデータ通信対応か確認（充電専用
  ケーブルでは認識されません）
- **Linux で Permission denied**: `sudo usermod -aG dialout $USER`
  のあと再ログイン
- **書き込みが途中で失敗する**: リセットボタンを 2 回素早く押して
  ブートローダモードにしてから再試行

## シリアルモニタに何も出ない

- ボーレートが `115200` になっているか確認
- 書き込み直後は数秒待つ（USB の再列挙に時間がかかることがあります）

## その他

再現手順つきで
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へ報告してください。
