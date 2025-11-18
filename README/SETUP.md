# 🚀 お母さんスイッチ - セットアップガイド

このガイドに従って、システム全体をセットアップします。

---

## 📋 前提条件

- **OS**: macOS / Ubuntu / Windows (WSL2)
- **Python**: 3.8以上
- **ブラウザ**: Google Chrome / Microsoft Edge（音声認識機能使用のため）

---

## 🔧 ステップ1: 基本セットアップ

### 1-1. リポジトリクローン

```bash
git clone https://github.com/Heart050323/new-smart-speaker.git
cd new-smart-speaker
```

### 1-2. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

**インストールされるパッケージ:**
- Flask（Webサーバー）
- librosa（音声処理）
- scikit-learn（機械学習）
- numpy（数値計算）
- webrtcvad（音声検出）
- sounddevice（録音）
- simpleaudio（音声再生）

### 1-3. 必要なフォルダ作成

```bash
mkdir -p data/parent data/child models logs uploads
```

---

## 🎤 ステップ2: 話者識別モデルの学習

### 2-1. sentence.txtの作成

録音用の台本ファイルを作成します。

**フォーマット**: `番号:漢字表記:ひらがな読み`

```bash
cat > sentence.txt << 'EOF'
b01:電気をつけて:でんきをつけて
b02:電気を消して:でんきをけして
b03:テレビをつけて:てれびをつけて
b04:テレビを消して:てれびをけして
b05:おやつちょうだい:おやつちょうだい
b06:宿題やりなさい:しゅくだいやりなさい
b07:早く片付けなさい:はやくかたづけなさい
b08:お風呂入りなさい:おふろはいりなさい
b09:もう寝なさい:もうねなさい
b10:ご飯食べなさい:ごはんたべなさい
EOF
```

### 2-2. 母親の音声を録音

```bash
python3 record_hybrid.py --speaker parent --sentence sentence.txt
```

**操作方法:**
1. 録音対象を指定: `b[1,2,3,4,5,6,7,8,9,10]` または 空Enter（全文）
2. モード選択: `full`（完全自動）または `cmd`（手動）

**fullモード（推奨）:**
- 台本が自動的に表示される
- お手本音声が再生される（sample/フォルダがある場合）
- 話すと自動で録音開始・終了
- 途中で `skip`, `stop`, `quit` で割り込み可能

**cmdモード:**
- `r` - 録音（お手本再生後）
- `R` - 録音（お手本なし）
- `l` - 録音済み音声を再生
- `n` - 次の文へ
- `q` - 終了

### 2-3. 子供の音声を録音

```bash
python3 record_hybrid.py --speaker child --sentence sentence.txt
```

同様の手順で録音します。

### 2-4. データ確認

```bash
ls -R data/
```

以下のような構成になっていることを確認：

```
data/
├── parent/
│   ├── parent_b01.wav
│   ├── parent_b02.wav
│   └── ... (10ファイル以上推奨)
└── child/
    ├── child_b01.wav
    ├── child_b02.wav
    └── ... (10ファイル以上推奨)
```

### 2-5. GMMモデル学習

```bash
python3 train_gmm.py
```

**出力:**
```
判定: child
確信度: {'parent': 0.08, 'child': 0.92}
```

学習済みモデルが `models/gmm.pkl` に保存されます。

---

## 🌐 ステップ3: Webサーバー起動

### 3-1. サーバー起動

```bash
python3 app.py
```

または起動スクリプトを使用：

```bash
chmod +x start.sh
./start.sh
```

**成功時の出力:**

```
✅ 話者識別モジュール (identify.py) を読み込みました
 * Running on http://127.0.0.1:5001
 * Running on http://10.100.79.140:5001
```

### 3-2. ブラウザでアクセス

```
http://localhost:5001
```

---

## 🎮 ステップ4: 使用方法

### Web GUIモード

1. **マイクボタンをクリック** → 音声認識・録音開始
2. **話しかける** → リアルタイムでテキスト表示
3. **認識確定** → 自動で録音停止 & サーバーへ送信
4. **システム応答**:
   - 話者識別（GMM）が実行される
   - MOTHER（母親）または CHILD（子供）を判定
   - シンクロ率が更新される
   - 応答メッセージが表示・読み上げられる

### ログの確認

会話ログパネルに以下の情報が表示されます：

- **🎤 音声データ送信済**: 音声ファイルが正常に送信された
- **📊 GMM確信度**: 話者識別の確信度（%）
- **🔤 キーワード判定**: GMM未使用時のフォールバック

---

## 🔧 オプション: Julius音声認識の統合

### Julius セットアップ（Ubuntu）

#### 4-1. Juliusインストール

```bash
sudo apt update
sudo apt install julius
```

#### 4-2. 音響モデル配置

⚠ **音響モデルは著作権のため同梱していません**

授業で配布されたモデルを配置：

```bash
mkdir -p asr/model
cp -r <配布場所>/binhmm-jnas-mono-mix16 asr/model/
cp <配布場所>/mono.lst asr/mono.lst
```

#### 4-3. Julius起動（ターミナル①）

```bash
julius -C asr/grammar-mic.jconf -module
```

**成功時:**
```
Module mode ready
waiting client at 10500
```

#### 4-4. client.py起動（ターミナル②）

```bash
python3 client.py
```

発話すると：
```
[REC] recording...
--- RAW WORDS ---
['電気', 'つけて']
>>> COMMAND: LIGHT_ON
>>> ATTITUDE: polite
```

ログが `logs/` に保存されます。

---

## 📊 動作確認

### テスト1: 話者識別

```bash
python3 identify.py
```

確信度が表示されればOK。

### テスト2: Web GUI

1. `http://localhost:5001` にアクセス
2. マイクボタンをクリック
3. 「電気をつけて」と話す
4. ログに確信度が表示される

### テスト3: Julius連携（オプション）

1. Julius起動
2. `python3 client.py` 実行
3. コマンド分類が正常に動作する

---

## 🐛 トラブルシューティング

### ❌ identify.py でエラー

**原因**: `models/gmm.pkl` が存在しない

**解決策:**
```bash
python3 train_gmm.py
```

### ❌ Web GUIで「確信度」が表示されない

**原因**: GMM モデルが読み込めていない

**確認:**
```bash
ls models/gmm.pkl
```

**サーバーログを確認:**
```
✅ 話者識別モジュール (identify.py) を読み込みました
```

### ❌ 音声が録音できない

**macOS**: システム環境設定 → セキュリティとプライバシー → マイク → Chromeを許可

**Ubuntu**: `alsamixer` でマイク音量を確認

### ❌ Julius が起動しない

**原因**: 音響モデルのパスが間違っている

**確認:**
```bash
ls asr/model/binhmm-jnas-mono-mix16
ls asr/mono.lst
```

---

## 📈 次のステップ

### 精度向上

- 録音データを増やす（各話者20ファイル以上推奨）
- 異なる発話内容で録音
- GMMのパラメータ調整（`train_gmm.py`の`n_components`）

### 機能拡張

- IoT連携（実際の家電制御）
- 複数話者対応（祖父母、兄弟など）
- 感情分析の追加
- データベース連携

---

## 🎉 完了！

これで「お母さんスイッチ」システムが完全に動作します！

次は ARCHITECTURE.md を参照して、システムの内部動作を理解してください。
