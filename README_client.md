# 🚀 セットアップ手順（Ubuntu）

この手順に沿えば、clone → 音響モデル配置 → 実行まで行えます。

---

## 1. リポジトリの取得

```bash
git clone https://github.com/Heart050323/new-smart-speaker.git
cd new-smart-speaker
````

---

## 2. 必要パッケージのインストール

### Julius（音声認識エンジン）

```bash
sudo apt update
sudo apt install julius
```

### 録音ツール（arecord）

```bash
sudo apt install alsa-utils
```

---

## 3. 音響モデル（HMM）の配置（※重要）

⚠ **音響モデル（JNASモノフォンモデル）は著作権のため GitHub に含めていません。
各自が手元で配置してください。**

必要なファイル：

* `binhmm-jnas-mono-mix16`（フォルダ）
* `mono.lst`（ファイル）

### 3-1. model フォルダを作成

```bash
mkdir -p asr/model
```

### 3-2. HMMフォルダをコピー

（例）授業で配布されたモデルが以下にある場合：

```
/home/<ユーザー名>/Downloads/dialogue-demo/asr/model/binhmm-jnas-mono-mix16
```

コピー：

```bash
cp -r ~/Downloads/dialogue-demo/asr/model/binhmm-jnas-mono-mix16 asr/model/
```

### 3-3. mono.lst を正しい場所に移動

Julius は mono.lst を **asr/mono.lst** に置く必要があります。

まず探す（任意）：

```bash
find ~ -name mono.lst
```

コピー：

```bash
cp ~/Downloads/dialogue-demo/asr/model/mono.lst asr/model/
```

その後、正しい位置へ移動：

```bash
mv asr/model/mono.lst asr/mono.lst
```

### ✔ 最終的な構成

```
new-smart-speaker/
 ├ asr/
 │   ├ grammar/
 │   ├ grammar-mic.jconf
 │   ├ mono.lst                 ← ここに置く！
 │   └ model/
 │       └ binhmm-jnas-mono-mix16/
 ├ client.py
 ├ tts.py
 ├ requirements.txt
 ├ start.sh（任意）
 └ README.md
```

---

## 4. Julius を module モードで起動（ターミナル①）

```bash
cd ~/new-smart-speaker
julius -C asr/grammar-mic.jconf -module
```

成功すると：

```
Module mode ready
waiting client at 10500
```

と表示されます。
このターミナルは閉じずにそのまま残します。

---

## 5. client.py を起動（ターミナル②）

別のターミナルを開く：

```bash
cd ~/new-smart-speaker
python3 client.py
```

client.py が行う処理：

* マイク録音
* Julius からの結果受信
* 認識単語の解析
* コマンド分類（電気つけて → LIGHT_ON など）
* 態度判定（polite / rude）
* JSONログ保存
* WAVファイル保存

---

## 6. 発話テスト例

```
電気つけて
```

出力：

```
--- RAW WORDS ---
['電気', 'つけて']
>>> COMMAND: LIGHT_ON
>>> ATTITUDE: polite
```

ログファイルが自動で `logs/` に保存されます。

---

# 🧩 トラブルシュート

---

## 🟥 Julius が「cannot access asr/model〜」と出る

音響モデルの配置が間違っています。

正しいコピー：

```bash
cp -r ~/Downloads/dialogue-demo/asr/model/binhmm-jnas-mono-mix16 asr/model/
mv asr/model/mono.lst asr/mono.lst
```

---

## 🟥 arecord エラー

Ubuntu → 設定 → サウンド → 入力
で使用するマイクデバイスを選択してください。

---

## 🟥 client.py が Julius に接続できない

* Julius を module モードで起動していない
* Port 10500 が別プロセスに占有されている

Julius を再起動してください。

---

# ⚠ 著作権について（重要）

Julius 用音響モデル（HMM, JNAS）は著作物です。

**GitHub にアップロードしたり公開することは禁止されています。**

本リポジトリでは model フォルダは空のままにしてあり、
各自が授業で配布されたモデルをローカルに配置することで回避しています。

