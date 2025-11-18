# 🎭 態度判定機能 - 設計仕様書

## 📋 概要

`client.py`から抽出した態度判定・コマンド分類機能を、Webベースの音声対話システムに統合。  
ユーザーの発言内容（態度）に応じて、スマートスピーカーの応答を動的に変更します。

---

## 🏗️ アーキテクチャ

```
┌─────────────────┐
│   Web Browser   │
│   (音声入力)     │
└────────┬────────┘
         │ POST /api/command
         │ FormData: {text, audio}
         ▼
┌─────────────────────────────────┐
│     Flask Server (app.py)        │
│  ┌──────────────────────────┐   │
│  │ 1. 話者識別 (identify.py)│   │
│  │    → MOTHER/CHILD        │   │
│  └──────────────────────────┘   │
│  ┌──────────────────────────┐   │
│  │ 2. 態度分析              │   │
│  │    (attitude_analyzer.py)│   │
│  │    → polite/rude/neutral │   │
│  └──────────────────────────┘   │
│  ┌──────────────────────────┐   │
│  │ 3. コマンド分類          │   │
│  │    → TV_ON/LIGHT_OFF etc.│   │
│  └──────────────────────────┘   │
│  ┌──────────────────────────┐   │
│  │ 4. 応答生成              │   │
│  │    (話者×態度×コマンド) │   │
│  └──────────────────────────┘   │
│  ┌──────────────────────────┐   │
│  │ 5. JSONログ保存          │   │
│  │    → logs/YYYYMMDD.json  │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
         │
         ▼
   ┌──────────┐
   │ JSON応答 │
   └──────────┘
```

---

## 📁 ファイル構成

### 新規作成

- **`attitude_analyzer.py`**  
  コマンド分類・態度判定・応答生成ロジック

### 更新したファイル

- **`app.py`**  
  - `attitude_analyzer`モジュールのインポート
  - `/api/command`エンドポイントに態度判定機能追加
  - JSONログ保存機能追加
  - `logs/`ディレクトリの自動作成

- **`static/js/app.js`**  
  - `addLogEntry()`関数にcommand, attitude引数追加
  - UI表示に態度アイコン・コマンドラベル追加

---

## 🎯 機能仕様

### 1. コマンド分類

| コマンドID   | トリガー単語          | 説明           |
|-------------|--------------------|---------------|
| `TV_ON`     | テレビ + つけ       | テレビをON     |
| `TV_OFF`    | テレビ + けし/消し   | テレビをOFF    |
| `LIGHT_ON`  | 電気 + つけ         | 電気をON       |
| `LIGHT_OFF` | 電気 + けし/消し     | 電気をOFF      |
| `GET_SNACK` | おやつ + ちょうだい  | おやつを要求   |
| `EXIT`      | 終了               | システム終了   |

### 2. 態度判定

| 態度      | トリガー単語                                  | アイコン |
|----------|---------------------------------------------|---------|
| `polite` | ください、お願い、ちょうだい、つけて           | 😊      |
| `rude`   | つけろ、くれ、しろ、やれ、だまれ、うるさい     | 😠      |
| `neutral`| 上記以外                                     | 😐      |

### 3. 応答ロジック

#### 母親 (MOTHER)

```python
if attitude == "polite":
    "はい、お母さん。{コマンド実行}。"
elif attitude == "rude":
    "お母さん、承知しました。{コマンド実行}。"
else:
    "かしこまりました。{コマンド実行}。"
```

#### 子供 (CHILD)

```python
if attitude == "polite":
    if command == "GET_SNACK":
        "いい子ですね。おやつを用意します。"
    else:
        "はい、{コマンド実行}。"
elif attitude == "rude":
    "そんな言い方はダメですよ。お母さんを呼んでください。"
else:
    if command == "GET_SNACK":
        "おやつは宿題が終わってからね。"
    elif command == "TV_ON":
        "テレビは勉強が終わってからです。"
    else:
        "それはお母さんに頼んでください。"
```

---

## 💾 JSONログ形式

`logs/YYYYMMDD_HHMMSS.json`

```json
{
  "timestamp": "2025-11-18T14:30:45.123456",
  "speaker": "CHILD",
  "user_text": "電気をつけてください",
  "command": "LIGHT_ON",
  "attitude": "polite",
  "response": "はい、電気をつけます。",
  "sync_rate": 35,
  "audio_saved": true,
  "audio_path": "uploads/input.wav",
  "confidence": {
    "parent": 0.12,
    "child": 0.88
  },
  "method": "GMM"
}
```

---

## 🎨 UI表示

### ログエントリー例

```
CHILD                                    14:30:45
INPUT: 電気をつけてください 🎤 音声データ送信済 📊 GMM確信度: 88.0% 💡 電気ON 😊 丁寧
OUTPUT: はい、電気をつけます。
```

---

## 🧪 テスト方法

### 1. 態度分析モジュール単体テスト

```bash
cd /Users/harutotanaka/Documents/3A/voice-dialogue-system/new-smart-speaker
python3 attitude_analyzer.py
```

### 2. Webシステムテスト

1. サーバー起動
```bash
python3 app.py
```

2. ブラウザで http://127.0.0.1:5001 にアクセス

3. テストケース

| 発言例                | 期待される結果                              |
|----------------------|-------------------------------------------|
| 電気をつけてください   | コマンド: LIGHT_ON, 態度: polite, 応答: ○  |
| 電気つけろ           | コマンド: LIGHT_ON, 態度: rude, 応答: NG   |
| テレビをつけて (母)   | コマンド: TV_ON, 態度: polite, 応答: ○     |
| おやつちょうだい      | コマンド: GET_SNACK, 態度: polite, 応答: ○ |

### 3. JSONログ確認

```bash
ls -ltr logs/
cat logs/20251118_143045.json
```

---

## 🔧 カスタマイズ

### 態度判定ルールの追加

`attitude_analyzer.py` の `judge_attitude()` を編集：

```python
def judge_attitude(words):
    joined = words if isinstance(words, str) else "".join(words)
    
    # 新しいルール追加
    very_polite = ["何卒", "恐れ入りますが"]
    for vp in very_polite:
        if vp in joined:
            return "very_polite"  # 新しい態度レベル
    
    # 既存のルール...
```

### コマンドの追加

`attitude_analyzer.py` の `classify_command()` を編集：

```python
def classify_command(words):
    joined = words if isinstance(words, str) else "".join(words)
    
    # 新しいコマンド追加
    if "音楽" in joined:
        if "かけ" in joined:
            return "MUSIC_PLAY"
    
    # 既存のルール...
```

### 応答メッセージのカスタマイズ

`attitude_analyzer.py` の `get_response_by_attitude()` を編集：

```python
command_messages = {
    "TV_ON": "テレビをつけます",
    "MUSIC_PLAY": "音楽を再生します",  # 追加
    # ...
}
```

---

## 📊 統計分析

### ログから態度傾向を分析

```python
import json
import glob

logs = glob.glob("logs/*.json")
attitudes = {"polite": 0, "rude": 0, "neutral": 0}

for log_file in logs:
    with open(log_file) as f:
        data = json.load(f)
        att = data.get("attitude")
        if att in attitudes:
            attitudes[att] += 1

print(attitudes)
# {'polite': 45, 'rude': 3, 'neutral': 12}
```

---

## 🚀 今後の拡張

- [ ] 感情分析 (happy/sad/angry)
- [ ] 音声トーン分析（librosaで音高・音量解析）
- [ ] 機械学習ベースの態度分類（BERT等）
- [ ] リアルタイムダッシュボード（態度の時系列変化）
- [ ] 多言語対応（英語・中国語など）

---

## 📝 まとめ

態度判定機能により、スマートスピーカーが：

✅ **丁寧な子供には優しく応答**  
✅ **乱暴な子供には教育的に対応**  
✅ **母親には常に従順**  
✅ **すべての対話をJSON形式で記録**  

これにより、より人間らしい対話体験を実現！
