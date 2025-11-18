# 🎤 自動停止機能 - 仕様書

## 📋 概要

音声認識が一度完了したら、自動的にリスニングモードをオフにする機能を実装しました。  
ユーザーが話し終わった後、手動でボタンを押さなくても自動的に待機状態に戻ります。

---

## 🎯 動作仕様

### **変更前の動作**
1. マイクボタンをクリック → リスニング開始
2. 話しかける → 認識完了
3. **継続してリスニング中**（手動で停止が必要）
4. もう一度話しかける → 認識完了
5. ...（延々と継続）

### **変更後の動作**
1. マイクボタンをクリック → リスニング開始
2. 話しかける → 認識完了
3. **自動的にリスニング停止** ✨
4. 次に話す場合は、再度マイクボタンをクリック

---

## 🔧 実装詳細

### **修正ファイル**
- `static/js/app.js`

### **変更内容**

#### 1. **`recognition.onresult` イベント**

発話が確定（`isFinal`）したら、`isListening`フラグを`false`に設定：

```javascript
if (finalTranscript) {
    elements.voiceInput.innerHTML = `<span class="text-white">${escapeHtml(finalTranscript)}</span>`;
    // 🎯 発話が完了したら自動的にリスニングモードをオフ
    isListening = false;
    stopRecording(finalTranscript);
}
```

#### 2. **`recognition.onend` イベント**

リスニングモードがオフの場合、再起動せずにUIを元に戻す：

```javascript
recognition.onend = () => {
    console.log('🛑 音声認識終了');
    // リスニングモードがオフの場合は再起動しない
    if (isListening) {
        console.log('🔄 音声認識を再開');
        recognition.start();
    } else {
        console.log('✋ リスニングモードをオフにしました');
        elements.systemStatus.textContent = 'IDLE';
        elements.systemStatus.style.color = '#00ff41';
        
        // マイクボタンのUIを元に戻す
        elements.micButton.classList.remove('active');
        elements.micButton.innerHTML = `
            <span class="text-2xl">🎤</span>
            <div class="text-sm mt-1">START LISTENING</div>
        `;
        elements.micButton.classList.remove('bg-green-600', 'hover:bg-green-700');
        elements.micButton.classList.add('bg-red-600', 'hover:bg-red-700');
    }
};
```

#### 3. **`stopRecording` 関数**

録音停止時に音声認識も停止：

```javascript
function stopRecording(recognizedText) {
    if (!isRecording || !mediaRecorder) {
        return;
    }
    
    console.log('⏹️ 録音を停止します...');
    
    // 🎯 音声認識も停止
    if (recognition) {
        recognition.stop();
    }
    
    mediaRecorder.onstop = () => {
        console.log('✅ 録音停止完了');
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        processVoiceCommand(recognizedText, audioBlob);
        isRecording = false;
    };
    
    mediaRecorder.stop();
}
```

---

## 🎬 使用フロー

```
┌─────────────────────────────────┐
│ 1. マイクボタンをクリック        │
│    "START LISTENING"            │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 2. リスニング開始               │
│    ボタン: "STOP LISTENING"     │
│    ステータス: "LISTENING"      │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 3. ユーザーが話しかける         │
│    (例: "電気をつけて")         │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 4. 発話確定（isFinal）          │
│    → isListening = false        │
│    → recognition.stop()         │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 5. recognition.onend 発火       │
│    → UIを元に戻す               │
│    → ステータス: "IDLE"         │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 6. 処理完了後、待機状態         │
│    次の発話には再度ボタンクリック│
└─────────────────────────────────┘
```

---

## 🧪 テスト方法

### **基本動作テスト**

1. ブラウザで http://127.0.0.1:5001 にアクセス
2. **マイクボタン**をクリック
3. 「電気をつけて」と話す
4. 認識完了後、**自動的にリスニング停止**を確認
5. ボタンが赤色（"START LISTENING"）に戻ることを確認
6. ステータスが「IDLE」に戻ることを確認

### **連続発話テスト**

1. マイクボタンをクリック
2. 「テレビをつけて」と話す
3. **自動停止を確認**
4. 再度マイクボタンをクリック
5. 「電気を消して」と話す
6. **自動停止を確認**

### **エラーケーステスト**

1. マイクボタンをクリック
2. 何も話さずに待つ
3. `no-speech`エラーが表示されることを確認
4. リスニングが継続しないことを確認

---

## 📊 コンソールログ例

```
🎤 音声認識開始
🔴 録音開始
⏹️ 録音を停止します...
✅ 録音停止完了
📤 送信データ: {text: "電気をつけて", audioSize: 87236, audioType: "audio/webm"}
🛑 音声認識終了
✋ リスニングモードをオフにしました
📥 受信データ: {speaker: "MOTHER", command: "LIGHT_ON", attitude: "polite", ...}
```

---

## 🔄 ブラウザキャッシュクリア

JavaScriptの変更を反映するには：

### **方法1: ハードリロード**
- **Mac**: `Cmd + Shift + R`
- **Windows**: `Ctrl + F5` または `Ctrl + Shift + R`

### **方法2: 開発者ツール**
1. F12で開発者ツールを開く
2. ネットワークタブを開く
3. 「キャッシュを無効化」にチェック
4. ページをリロード

### **方法3: プライベートモード**
- シークレットウィンドウ/プライベートブラウジングで開く

---

## 🎨 UI変化

### **リスニング中**
```
┌───────────────────────┐
│   🎤                  │
│  STOP LISTENING       │  ← 緑色
└───────────────────────┘
ステータス: LISTENING (青色)
```

### **自動停止後**
```
┌───────────────────────┐
│   🎤                  │
│  START LISTENING      │  ← 赤色
└───────────────────────┘
ステータス: IDLE (緑色)
```

---

## ⚙️ カスタマイズ

### **自動停止を無効化したい場合**

`static/js/app.js`の該当箇所をコメントアウト：

```javascript
if (finalTranscript) {
    elements.voiceInput.innerHTML = `<span class="text-white">${escapeHtml(finalTranscript)}</span>`;
    // isListening = false;  // ← この行をコメントアウト
    stopRecording(finalTranscript);
}
```

### **タイムアウトで自動停止（応用）**

一定時間無音が続いたら停止する場合：

```javascript
let silenceTimer;

recognition.onresult = (event) => {
    clearTimeout(silenceTimer);
    
    // ... 既存の処理 ...
    
    if (!finalTranscript) {
        // 3秒無音が続いたら自動停止
        silenceTimer = setTimeout(() => {
            isListening = false;
            if (recognition) recognition.stop();
        }, 3000);
    }
};
```

---

## 🚀 今後の改善案

- [ ] 音声レベルメーター表示
- [ ] 発話開始検出の視覚的フィードバック
- [ ] 連続発話モードのトグルボタン
- [ ] 自動停止までの遅延時間設定（オプション）
- [ ] キーボードショートカット（スペースキーなど）

---

## 📝 まとめ

✅ **一度の発話で自動停止**  
✅ **手動でボタンを押す手間を削減**  
✅ **より自然な対話フロー**  
✅ **電力・リソースの節約**

スマートスピーカーらしい、直感的な操作が可能になりました！
