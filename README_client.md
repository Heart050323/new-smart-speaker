# 🚀 セットアップ手順（Ubuntu）

以下の手順に従えば、clone しただけで誰でも動かせます。

---

## 1. リポジトリの取得

```bash
git clone https://github.com/Heart050323/new-smart-speaker.git
cd new-smart-speaker
````

---

## 2. 必要パッケージのインストール

### Julius（音声認識）

```bash
sudo apt update
sudo apt install julius
```

### 録音（arecord）

Ubuntu 標準で入っているが、念のため：

```bash
sudo apt install alsa-utils
```

---

## 3. 音響モデルの配置（重要）

⚠ **著作権のため GitHub に含めていません。**

授業配布の音響モデル
**binhmm-jnas-mono-mix16**（JNAs モノラルモデル）を次の位置にコピーしてください：

```
new-smart-speaker/asr/model/binhmm-jnas-mono-mix16
new-smart-speaker/asr/model/mono.lst
```

これが無いと Julius は起動しません。

---

## 4. Julius の起動（ターミナル1）

```bash
cd new-smart-speaker
julius -C asr/grammar-mic.jconf -module
```

成功すると以下のように表示されます：

```
Module mode ready
waiting client at 10500
```

---

## 5. クライアント（ASR）起動（ターミナル2）

別のターミナルを開いて：

```bash
cd new-smart-speaker
python3 client.py
```

これで録音 → 認識 → コマンド分類 → 態度判定 → JSON保存
が動作します。

---

# 🎧 発話例（動作チェック）

* 「電気つけて」 → polite + LIGHT_ON
* 「電気つけろ」 → rude + LIGHT_ON
* 「おやつください」 → polite + GET_SNACK
* 「テレビけして」 → TV_OFF

結果は `logs/` に以下のように保存されます：

```
temp_xxx.wav      # 録音データ
20251117_153000.json   # 認識ログ
```
