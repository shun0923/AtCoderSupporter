# AtCoderSupporter

[AtCoder](https://atcoder.jp)の自動テストと提出を行います。

## セットアップ・起動

1. `pip install lxml`を実行
2. [`AtCoderSupporter.py`](https://raw.githubusercontent.com/shun0923/AtCoderSupporter/master/AtCoderSupporter.py)をダウンロード
3. `python AtCoderSupporter.py`を実行

## 実行中のコマンド

### よく使うもの

|コマンド（省略形）|内容|
|-------|----|
|test (t)|ビルドして入出力例でテスト、全て通ればそのまま提出も可能|
|submit (s)|テストせずに提出|
|run (r)|ビルドして実行|
|exit (e)|終了|
|その他|コンテスト名の設定（前回の起動時と同じなら省略可）|

※
「コンテスト名」とは問題URLに含まれる`https://atcoder.jp/contests/〇〇`の部分です。
企業コンにも対応しています。
ex. abc100, kuronekoyamato-contest2019

### その他のコマンド

|コマンド（省略形）|内容|
|-------|----|
|download (d) [contest_name]|全テストケースの再ダウンロード|
|login (l)|再ログイン|
|check (c) src_path|設定されたソースコードのパスを出力|
|check (c) account|ログイン済みのアカウント情報を出力|
|src_path [path]|ソースコードのパスの変更|
