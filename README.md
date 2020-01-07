# AtCoderSupporter

[AtCoder](https://atcoder.jp)の自動テストと提出を行います。

## セットアップ・起動

1. `pip install bs4 termcolor colorama`を実行
2. [`AtCoderSupporter.py`](https://raw.githubusercontent.com/shun0923/AtCoderSupporter/master/AtCoderSupporter.py)をダウンロード
3. `python AtCoderSupporter.py`を実行

## コマンド一覧

### よく使うもの

|コマンド（省略形）|内容|
|-------|----|
|test (t) [contest_name] [task_number]|ビルドして入出力例でテスト、全て通ればそのまま提出も可能　　※contest_nameのみは不可|
|submit|テストせずに提出|
|run (r)|ビルドして実行|
|exit (e)|終了|
|[contest_name]|コンテスト名の設定（前回のコマンドと同じなら省略可）|

※1 [contest_name]や[task_number]などのオプションは、前回のコマンドと同じなら省略できます。

※2 [contest_name]とは問題URLに含まれる`https://atcoder.jp/contests/〇〇`の部分、[task_number]はアルファベットまたは数字(1-indexed)で指定してください。
基本的に企業コンにも対応しています。

### その他のコマンド

|コマンド（省略形）|内容|
|-------|----|
|download (d) [contest_name]|全テストケースの再ダウンロード|
|login (l)|再ログイン|
|check (c)|保存済みの情報を出力|
|check (c) src_path|設定されたソースコードのパスを出力|
|check (c) account|ログイン済みのアカウント情報を出力|
|src_path [path]|ソースコードのパスの変更|
