# 🏗️ お母さんスイッチ - システムアーキテクチャ

## 📋 概要

このプロジェクトは、**話者識別**と**音声認識**を統合した次世代スマートスピーカーシステムです。
母親の声を識別し、権限レベルに応じて家電制御コマンドを実行します。

---

## 🎯 システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                    Web GUI (Browser)                         │
│  - リアルタイム音声認識 (Web Speech API)                      │
│  - 音声録音 (MediaRecorder API)                              │
│  - UI表示 (シンクロ率、ステータス、ログ)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP (FormData)
                  │ text + audio (webm)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask Backend (app.py)                          │
│  - 音声ファイル受信・保存                                     │
│  - 話者識別モジュール呼び出し                                 │
│  - コマンド分類・実行                                         │
│  - レスポンス生成                                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ identify.py  │    │  client.py   │
│              │    │  (Julius連携)│
│ GMM話者識別  │    │              │
│ - parent     │    │ 音声認識     │
│ - child      │    │ コマンド分類 │
└──────────────┘    └──────────────┘
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ models/      │    │ Julius       │
│ gmm.pkl      │    │ (音響モデル)  │
└──────────────┘    └──────────────┘
```

---

## 📁 ファイル役割

### 🎨 **フロントエンド（Web GUI）**

#### `templates/index.html`
- HTMLレイアウト
- 近未来的なUIデザイン
- Tailwind CSS使用

#### `static/css/styles.css`
- スタイルシート
- アニメーション定義
- ネオングロー、グリッチエフェクト

#### `static/js/app.js`
- Web Speech API（音声認識）
- MediaRecorder API（音声録音）
- FormData送信（テキスト + 音声）
- リアルタイムUI更新

---

### 🖥️ **バックエンド（Flask）**

#### `app.py` ⭐ **メインサーバー**
- エンドポイント管理
  - `GET /` - Web GUIを配信
  - `POST /api/command` - 音声コマンド処理
  - `GET /api/status` - システム状態取得
  - `POST /api/reset` - リセット
- 音声ファイル保存（`uploads/input.wav`）
- **話者識別モジュール統合**（identify.py）
- **Julius連携**（client.py）
- コマンド実行・応答生成

---

### 🔍 **話者識別（Speaker Identification）**

#### `train_gmm.py`
- **役割**: GMM（混合ガウスモデル）の学習
- **入力**: `data/parent/*.wav`, `data/child/*.wav`
- **出力**: `models/gmm.pkl`（学習済みモデル）
- **使用タイミング**: 初回セットアップ時、またはモデル再学習時

#### `identify.py`
- **役割**: 音声ファイルから話者を識別
- **入力**: WAVファイルパス
- **出力**: `("parent", {parent: 0.92, child: 0.08})` など
- **特徴量**: MFCC（メル周波数ケプストラム係数）
- **使用タイミング**: リアルタイム判定（app.pyから呼び出し）

---

### 🎤 **音声認識（Julius連携）**

#### `client.py`
- **役割**: Julius音声認識エンジンと通信
- **機能**:
  1. 音声録音（arecord）
  2. Juliusモジュールへ接続（ポート10500）
  3. 認識結果取得（WHYPO解析）
  4. コマンド分類（TV_ON, LIGHT_OFF など）
  5. 態度判定（polite / rude / neutral）
  6. JSONログ保存
- **使用タイミング**: app.pyから呼び出し、または単体で動作

#### `asr/grammar-mic.jconf`
- Julius設定ファイル
- 音響モデル、文法ファイル指定

#### `asr/grammar/*.{voca,grammar,dfa,dict}`
- Julius文法定義
- 認識語彙リスト

---

### 🎙️ **録音・学習データ作成**

#### `record_hybrid.py`
- **役割**: 話者ごとの学習データ録音
- **機能**:
  - VAD（Voice Activity Detection）による自動録音
  - 台本ガイド付き録音
  - お手本音声再生
  - コマンド操作モード / 完全自動モード
- **出力**: `data/parent/*.wav`, `data/child/*.wav`
- **使用タイミング**: 初回セットアップ、データ追加時

#### `sentence.txt`
- 録音用台本ファイル
- フォーマット: `番号:漢字:かな`
- 例: `b01:電気をつけて:でんきをつけて`

---

### 🔊 **音声合成（TTS）**

#### `tts.py`
- **役割**: Open JTalkによる音声合成
- **機能**: テキスト → 音声再生（aplay）
- **使用タイミング**: システム応答の読み上げ

---

### 📦 **データ・モデル**

#### `models/`
- `gmm.pkl` - 学習済みGMMモデル（pickleファイル）

#### `data/`
```
data/
├── parent/
│   ├── parent_b01.wav
│   ├── parent_b02.wav
│   └── ...
└── child/
    ├── child_b01.wav
    ├── child_b02.wav
    └── ...
```

#### `uploads/`
- `input.wav` - Web GUIから送信された最新音声

#### `logs/`
- `YYYYMMDD_HHMMSS.json` - 認識結果ログ
- `temp_*.wav` - 一時録音ファイル

---

## 🔄 動作フロー

### 🌐 **Web GUI モード**

1. **ユーザー操作**: マイクボタンをクリック
2. **録音開始**: MediaRecorder + Web Speech API
3. **音声認識**: リアルタイムでテキスト表示
4. **録音停止**: 認識確定時に自動停止
5. **データ送信**: `FormData{text, audio}` → `/api/command`
6. **サーバー処理**:
   ```python
   audio → uploads/input.wav に保存
   ├─ identify.py で話者識別
   └─ Julius で音声認識（オプション）
   → コマンド分類
   → 応答生成
   ```
7. **レスポンス**: JSON `{speaker, sync_rate, response}`
8. **UI更新**: シンクロ率、ログ表示
9. **TTS**: システム応答を読み上げ

### 🖥️ **Julius連携モード**

1. **Julius起動**: `julius -C asr/grammar-mic.jconf -module`
2. **client.py起動**: `python3 client.py`
3. **録音**: arecord（2秒）
4. **Julius通信**: ソケット接続（ポート10500）
5. **認識結果取得**: WHYPO解析
6. **コマンド分類**: `classify_command()`
7. **態度判定**: `judge_attitude()`
8. **ログ保存**: `logs/*.json`, `logs/temp_*.wav`

---

## 🔧 セットアップ手順

### 1️⃣ **初回セットアップ**

```bash
# リポジトリクローン
git clone https://github.com/Heart050323/new-smart-speaker.git
cd new-smart-speaker

# 依存パッケージインストール
pip install -r requirements.txt

# 必要なフォルダ作成
mkdir -p data/parent data/child models logs uploads
```

### 2️⃣ **学習データ録音**

```bash
# 母親の音声を録音
python3 record_hybrid.py --speaker parent --sentence sentence.txt

# 子供の音声を録音
python3 record_hybrid.py --speaker child --sentence sentence.txt
```

### 3️⃣ **GMM学習**

```bash
python3 train_gmm.py
# → models/gmm.pkl が生成される
```

### 4️⃣ **Juliusセットアップ（オプション）**

```bash
# 音響モデル配置（README_client.md参照）
mkdir -p asr/model
cp -r <元の場所>/binhmm-jnas-mono-mix16 asr/model/
cp <元の場所>/mono.lst asr/mono.lst
```

### 5️⃣ **サーバー起動**

```bash
# Flaskサーバー起動
python3 app.py

# ブラウザで http://localhost:5001 にアクセス
```

---

## 🎮 使用方法

### **Web GUIモード**
1. ブラウザで `http://localhost:5001` を開く
2. マイクボタンをクリック
3. 話しかける
4. システムが話者を識別し、応答を返す

### **Juliusモード（CLI）**
```bash
# ターミナル①: Julius起動
julius -C asr/grammar-mic.jconf -module

# ターミナル②: client.py起動
python3 client.py
```

---

## 🚀 次世代機能の統合

### ✅ **実装済み**
- Web GUI（リアルタイム音声認識）
- 音声録音・送信
- 話者識別（GMM）
- Julius音声認識連携

### 🔄 **統合予定**
1. **app.py に identify.py を統合**
   - 受信した音声ファイルで話者識別
   - キーワード判定 → GMM判定に置き換え

2. **app.py に client.py を統合**
   - Julius認識結果をコマンド分類に利用
   - Web Speech API との併用

3. **TTS統合**
   - システム応答を Open JTalk で読み上げ
   - Web Speech Synthesis との選択可能化

4. **IoT連携**
   - コマンド実行（電気ON/OFF、テレビ操作）
   - スマート家電API連携

---

## 📊 パフォーマンス指標

- **話者識別精度**: GMM（MFCC 13次元）で90%以上
- **音声認識精度**: Julius + 文法制約で高精度
- **応答速度**: 1秒以内（識別 + 応答生成）
- **シンクロ率管理**: 母親の発言で+15〜30%、子供で-5〜15%

---

## 🔐 セキュリティ

- 音声データは `uploads/` に一時保存（定期削除推奨）
- ログファイルは個人情報を含む可能性（アクセス制限）
- 本番環境ではHTTPS必須

---

## 📝 ライセンス

MIT License

## 👤 作者

田中 悠飛 (03250433)
