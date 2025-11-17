# お母さんスイッチ - Voice Command System

近未来的なハッカー風デザインの音声対話システムのWeb GUI

## 🎯 最新アップデート（v2.0）

- ✅ **ファイル分割**: CSS・JavaScriptを分離して可読性を向上
- ✅ **音声録音機能**: MediaRecorder APIで音声データをキャプチャ
- ✅ **音声データ送信**: テキストと音声ファイルを同時にサーバーへ送信
- ✅ **話者識別準備**: 保存された音声ファイルで話者識別が可能に

## � プロジェクト構成

```
new-smart-speaker/
├── app.py                      # Flaskバックエンド（音声ファイル受信対応）
├── tts.py                      # TTS機能
├── requirements.txt            # Python依存関係
├── start.sh                    # 起動スクリプト
├── templates/
│   └── index.html             # メインHTML（軽量化）
├── static/
│   ├── css/
│   │   └── styles.css         # スタイルシート（分離）
│   └── js/
│       └── app.js             # メインJavaScript（分離）
└── uploads/                   # 音声ファイル保存先（自動生成）
    └── input.wav              # 最新の録音データ
```

## ✨ 機能

### フロントエンド（static/js/app.js）
- 🎤 **Web Speech API**: 日本語音声認識
- 🔴 **MediaRecorder API**: 音声録音（webm形式）
- 📤 **FormData送信**: テキスト + 音声ファイルを同時送信
- 🎨 **リアルタイムUI更新**: ステータス・シンクロ率・ログ表示
- 🗣️ **音声合成**: システム応答の読み上げ

### バックエンド（app.py）
- 📥 **音声ファイル受信**: FormDataから音声ファイルを取得
- 💾 **ファイル保存**: `uploads/input.wav` として保存
- 🔍 **話者判定（準備完了）**: 保存された音声で識別可能
- 📊 **シンクロ率管理**: MOTHER/CHILDに応じて増減
- 🔄 **状態管理**: 会話履歴・システム状態の保持

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. サーバーの起動

```bash
python app.py
```

サーバーが起動したら、ブラウザで以下にアクセス:
```
http://localhost:5001
```

## 使い方

1. **マイクボタンをクリック**: 音声認識を開始
2. **話しかける**: 日本語で話しかけると自動で認識
3. **話者判定**: 
   - 「片付けなさい」「宿題やりなさい」などの母親らしい言葉 → MOTHER判定
   - その他の発言 → CHILD判定
4. **シンクロ率**: 
   - MOTHER判定で上昇（+15〜30%）
   - CHILD判定で下降（-5〜15%）
5. **応答**: システムが音声で返答

## UIコンポーネント

### システムステータス（左上）
- 現在の状態: IDLE / LISTENING / PROCESSING / SPEAKING
- 稼働時間表示

### 話者判定パネル（左中）
- 👩 MOTHER: 管理者権限（赤色）
- 🧒 CHILD: ユーザー権限（青色）
- 👤 UNKNOWN: 待機中（グレー）

### コントロールパネル（左下）
- START/STOP LISTENING: 音声認識の開始/停止
- RESET SYSTEM: システム状態をリセット

### シンクロ率ゲージ（右上）
- 0-30%: USER LEVEL（青色）
- 30-60%: ELEVATED（黄色）
- 60-90%: ADMIN（オレンジ色）
- 90-100%: MAXIMUM（赤色）

### 音声入力表示（右中）
- リアルタイムで認識中のテキストを表示

### 会話ログ（右下）
- 最新10件の会話履歴を表示
- CLEARボタンでログをクリア

## API エンドポイント

### POST /api/command
音声コマンドを送信（**v2.0: FormData対応**）

**Request (FormData):**
```
text: "ユーザーの発言内容" (string)
audio: 音声ファイル (Blob/File, webm形式)
```

**Response:**
```json
{
  "speaker": "MOTHER" | "CHILD",
  "sync_rate": 0-100,
  "response": "システムの応答テキスト",
  "timestamp": "ISO8601形式のタイムスタンプ",
  "audio_saved": true | false,
  "audio_path": "uploads/input.wav"
}
```

### GET /api/status
現在のシステム状態を取得

**Response:**
```json
{
  "sync_rate": 0-100,
  "speaker": "MOTHER" | "CHILD" | "UNKNOWN",
  "status": "IDLE" | "LISTENING" | "PROCESSING" | "SPEAKING",
  "log_count": 0-10
}
```

### POST /api/reset
システム状態をリセット

## ブラウザ対応

- ✅ Google Chrome（推奨）
- ✅ Microsoft Edge
- ❌ Firefox（Web Speech APIの制限あり）
- ❌ Safari（Web Speech APIの制限あり）

**注意**: 音声認識機能を使用するには、Google ChromeまたはEdgeブラウザが必要です。

## カスタマイズポイント

### デザイン変更
`templates/index.html`の`<style>`セクションで以下をカスタマイズ可能:
- カラースキーム（現在は緑ベース）
- アニメーション速度
- フォント

### 話者判定ロジック
`app.py`の`command()`関数で判定ロジックをカスタマイズ:
```python
mother_keywords = ['片付け', '掃除', '宿題', 'やりなさい', 'ダメ', '早く']
```

### シンクロ率の増減幅
```python
system_state["sync_rate"] = min(100, system_state["sync_rate"] + random.randint(15, 30))
```

## 将来の拡張

- [ ] 機械学習モデルによる高精度な話者認識
- [ ] 感情分析の追加
- [ ] 複数ユーザーの登録・管理
- [ ] 会話履歴の永続化（データベース連携）
- [ ] IoTデバイス連携（スマート家電の制御）
- [ ] カスタムコマンドの登録機能

## ライセンス

MIT License

## 作者

田中 悠飛 (03250433)
音声認識を利用した新時代のスマートスピーカーを作るプロジェクト
``` bash
# 1. コードを持ってくる
git pull

# 2. (まだなら) 仮想環境を作って有効化
python3 -m venv venv
source venv/bin/activate

# 3. リストを使って一括インストール
pip install -r requirements.txt
```
によってpython環境を有効化してください.

