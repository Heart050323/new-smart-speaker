from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import sys
import json
import numpy as np

# identify.pyをインポート
try:
    from identify import identify
    SPEAKER_ID_AVAILABLE = True
    print("✅ 話者識別モジュール (identify.py) を読み込みました")
except Exception as e:
    SPEAKER_ID_AVAILABLE = False
    print(f"⚠️  話者識別モジュールが利用できません: {e}")
    print("   キーワードベースの判定を使用します")

# attitude_analyzer.pyをインポート
try:
    from attitude_analyzer import classify_command, judge_attitude, get_response_by_attitude
    ATTITUDE_ANALYZER_AVAILABLE = True
    print("✅ 態度分析モジュール (attitude_analyzer.py) を読み込みました")
except Exception as e:
    ATTITUDE_ANALYZER_AVAILABLE = False
    print(f"⚠️  態度分析モジュールが利用できません: {e}")

app = Flask(__name__)

# アップロードフォルダの設定
UPLOAD_FOLDER = 'uploads'
LOG_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'webm', 'wav', 'mp3', 'ogg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOG_FOLDER'] = LOG_FOLDER
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

def save_json_log(data):
    """
    データをJSONログとして保存
    logs/YYYYMMDD_HHMMSS.json に保存
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(app.config['LOG_FOLDER'], filename)
    
    # numpy型をPython標準型に変換
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj
    
    data = convert_numpy(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📝 JSONログを保存しました: {filepath}")
    return filepath

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
    speaker = "UNKNOWN"
    confidence = {}
    
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
                
                # 🔍 話者識別の実行
                if SPEAKER_ID_AVAILABLE and os.path.exists("models/gmm.pkl"):
                    try:
                        predicted_speaker, confidence = identify(filepath)
                        # GMM の出力 (parent/child) を MOTHER/CHILD に変換
                        speaker_map = {
                            "parent": "MOTHER",
                            "child": "CHILD"
                        }
                        speaker = speaker_map.get(predicted_speaker, "UNKNOWN")
                        print(f"🎯 話者識別結果: {speaker} (確信度: {confidence})")
                    except Exception as e:
                        print(f"❌ 話者識別エラー: {e}")
                        speaker = "UNKNOWN"
                else:
                    print("⚠️  話者識別モデルが見つかりません。キーワード判定を使用します。")
                    
            except Exception as e:
                print(f"❌ 音声ファイルの保存に失敗: {e}")
    
    # キーワードベース判定（GMM判定が失敗した場合のフォールバック）
    if speaker == "UNKNOWN" and user_text:
        mother_keywords = ['片付け', '掃除', '宿題', 'やりなさい', 'ダメ', '早く']
        is_mother = any(keyword in user_text for keyword in mother_keywords)
        speaker = "MOTHER" if is_mother else "CHILD"
        print(f"📝 キーワードベース判定: {speaker}")
    
    # 🎯 態度分析とコマンド分類
    command = None
    attitude = "neutral"
    
    if ATTITUDE_ANALYZER_AVAILABLE and user_text:
        try:
            command = classify_command(user_text)
            attitude = judge_attitude(user_text)
            print(f"💬 コマンド: {command}, 態度: {attitude}")
        except Exception as e:
            print(f"❌ 態度分析エラー: {e}")
    
    # 📊 シンクロ率の更新（確信度ベース）
    if confidence and 'parent' in confidence:
        # 母親の確信度を0-100のパーセンテージに変換
        mother_confidence = float(confidence.get('parent', 0))
        system_state["sync_rate"] = int(mother_confidence * 100)
        print(f"📈 シンクロ率を更新: {system_state['sync_rate']}% (母親確信度: {mother_confidence:.2%})")
    else:
        # 確信度がない場合は従来のロジック（キーワードベース）
        if speaker == "MOTHER":
            system_state["sync_rate"] = min(100, system_state["sync_rate"] + random.randint(15, 30))
        else:
            system_state["sync_rate"] = max(0, system_state["sync_rate"] - random.randint(5, 15))
        print(f"📈 シンクロ率を更新: {system_state['sync_rate']}% (キーワードベース)")
    
    # 🎭 応答生成（態度に応じた応答）
    if ATTITUDE_ANALYZER_AVAILABLE and command and attitude:
        response_text = get_response_by_attitude(command, attitude, speaker)
    else:
        # フォールバック：従来の応答
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
        "command": command,
        "attitude": attitude,
        "response": response_text,
        "sync_rate": system_state["sync_rate"],
        "audio_saved": audio_saved,
        "audio_path": audio_path,
        "confidence": confidence if confidence else None,
        "method": "GMM" if SPEAKER_ID_AVAILABLE and confidence else "keyword"
    }
    
    # 📝 JSONログとして保存
    try:
        save_json_log(log_entry)
    except Exception as e:
        print(f"❌ ログ保存エラー: {e}")
    
    system_state["conversation_log"].append(log_entry)
    
    # 最新10件のみ保持
    if len(system_state["conversation_log"]) > 10:
        system_state["conversation_log"] = system_state["conversation_log"][-10:]
    
    # numpy型をPython標準型に変換（JSON serializable）
    if confidence:
        confidence = {k: float(v) for k, v in confidence.items()}
    
    return jsonify({
        "speaker": speaker,
        "command": command,
        "attitude": attitude,
        "sync_rate": system_state["sync_rate"],
        "response": response_text,
        "timestamp": log_entry["timestamp"],
        "audio_saved": audio_saved,
        "audio_path": audio_path,
        "confidence": confidence if confidence else None,
        "method": "GMM" if SPEAKER_ID_AVAILABLE and confidence else "keyword"
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
