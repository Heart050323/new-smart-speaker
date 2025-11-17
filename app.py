from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# アップロードフォルダの設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webm', 'wav', 'mp3', 'ogg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限

# グローバル状態（実際のシステムと連携する際に置き換える）
system_state = {
    "sync_rate": 0,
    "speaker": "UNKNOWN",
    "status": "IDLE",
    "conversation_log": []
}

def allowed_file(filename):
    """許可された拡張子かチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def command():
    """
    音声コマンドを受け取り、処理結果を返す
    
    Request (FormData):
    - text: ユーザーの発言内容（テキスト）
    - audio: 音声ファイル（Blob/File）
    
    Response JSON:
    {
        "speaker": "MOTHER" or "CHILD",
        "sync_rate": 0-100,
        "response": "システムの応答テキスト",
        "timestamp": "ISO8601形式のタイムスタンプ",
        "audio_saved": True/False,
        "audio_path": "保存されたファイルパス"
    }
    """
    # テキストデータの取得
    user_text = request.form.get('text', '')
    
    # 音声ファイルの処理
    audio_saved = False
    audio_path = None
    
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file and audio_file.filename:
            # ファイル名を安全化して保存
            filename = 'input.wav'  # 固定ファイル名で上書き保存
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                audio_file.save(filepath)
                audio_saved = True
                audio_path = filepath
                print(f"✅ 音声ファイルを保存しました: {filepath}")
                print(f"📊 ファイルサイズ: {os.path.getsize(filepath)} bytes")
            except Exception as e:
                print(f"❌ 音声ファイルの保存に失敗: {e}")
    
    # モックアップ: 話者判定（実際はMLモデルで判定）
    # TODO: ここで保存した音声ファイルを使って話者識別を行う
    # 例: speaker = speaker_identification_model(audio_path)
    
    # キーワードベースで簡易判定（暫定）
    mother_keywords = ['片付け', '掃除', '宿題', 'やりなさい', 'ダメ', '早く']
    is_mother = any(keyword in user_text for keyword in mother_keywords)
    
    speaker = "MOTHER" if is_mother else "CHILD"
    
    # シンクロ率の更新（母の発言で上昇、子の発言で下降）
    if speaker == "MOTHER":
        system_state["sync_rate"] = min(100, system_state["sync_rate"] + random.randint(15, 30))
    else:
        system_state["sync_rate"] = max(0, system_state["sync_rate"] - random.randint(5, 15))
    
    # 応答生成（モックアップ）
    if speaker == "MOTHER":
        responses = [
            "はい、お母さん。承知しました。",
            "かしこまりました。すぐに対応します。",
            "了解しました。実行します。",
            "お母さんの指示を受理しました。"
        ]
    else:
        responses = [
            "権限が不足しています。お母さんを呼んでください。",
            "アクセスが拒否されました。",
            "その操作には管理者権限が必要です。",
            "認証レベルが不足しています。"
        ]
    
    response_text = random.choice(responses)
    
    # ログに追加
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "speaker": speaker,
        "user_text": user_text,
        "response": response_text,
        "sync_rate": system_state["sync_rate"],
        "audio_saved": audio_saved
    }
    system_state["conversation_log"].append(log_entry)
    
    # 最新10件のみ保持
    if len(system_state["conversation_log"]) > 10:
        system_state["conversation_log"] = system_state["conversation_log"][-10:]
    
    return jsonify({
        "speaker": speaker,
        "sync_rate": system_state["sync_rate"],
        "response": response_text,
        "timestamp": log_entry["timestamp"],
        "audio_saved": audio_saved,
        "audio_path": audio_path
    })

@app.route('/api/status', methods=['GET'])
def status():
    """現在のシステム状態を取得"""
    return jsonify({
        "sync_rate": system_state["sync_rate"],
        "speaker": system_state["speaker"],
        "status": system_state["status"],
        "log_count": len(system_state["conversation_log"])
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    """システム状態をリセット"""
    system_state["sync_rate"] = 0
    system_state["speaker"] = "UNKNOWN"
    system_state["status"] = "IDLE"
    system_state["conversation_log"] = []
    
    return jsonify({"message": "System reset successfully"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
