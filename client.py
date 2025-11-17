#!/usr/bin/env python3
import socket
import re
import subprocess
import uuid
import os
import json
from datetime import datetime

HOST = "localhost"
PORT = 10500


# -----------------------------------------------------------
# ログ保存フォルダ作成
# -----------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


# -----------------------------------------------------------
# 音声録音（arecord を使用）
# -----------------------------------------------------------
def record_audio(seconds=2):
    """
    arecord を使用して音声を録音し logs/temp_xxx.wav として保存。
    """
    filename = f"temp_{uuid.uuid4().hex}.wav"
    filepath = os.path.join(LOG_DIR, filename)

    cmd = [
        "arecord",
        "-d", str(seconds),
        "-r", "16000",
        "-f", "S16_LE",
        "-c", "1",
        filepath
    ]

    print("[REC] recording...")
    subprocess.run(cmd)
    print(f"[REC] saved → {filepath}")

    return filepath


# -----------------------------------------------------------
# WHYPO から単語を抽出
# -----------------------------------------------------------
def parse_julius_result(text):
    return re.findall(r'WORD="([^"]+)"', text)


# -----------------------------------------------------------
# コマンド分類
# -----------------------------------------------------------
def classify_command(words):
    joined = "".join(words)

    if "テレビ" in joined:
        if "つけ" in joined:
            return "TV_ON"
        if "けし" in joined:
            return "TV_OFF"

    if "電気" in joined:
        if "つけ" in joined:
            return "LIGHT_ON"
        if "けし" in joined:
            return "LIGHT_OFF"

    if "おやつ" in joined:
        if "ちょうだい" in joined or "ください" in joined:
            return "GET_SNACK"
        return "SNACK"

    if "終了" in joined:
        return "EXIT"

    return None


# -----------------------------------------------------------
# 態度分類
# -----------------------------------------------------------
def judge_attitude(words):
    joined = "".join(words)

    polite = ["ください", "ちょうだい", "つけて"]
    rude = ["つけろ", "くれ"]

    for p in polite:
        if p in joined:
            return "polite"

    for r in rude:
        if r in joined:
            return "rude"

    return "neutral"


# -----------------------------------------------------------
# JSONログ保存
# -----------------------------------------------------------
def save_json_log(data):
    """
    data を logs/YYYYMMDD_HHMMSS.json に保存する
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}.json"
    path = os.path.join(LOG_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"[LOG] saved → {path}")


# -----------------------------------------------------------
# Julius から1回分の認識結果を取得
# -----------------------------------------------------------
def recognize_once():
    """
    音声録音 → Julius認識 → 結果と音声を logs に保存 → dict で返す
    """

    # Step 1: 録音
    wav_path = record_audio()

    # Step 2: Julius module へ接続
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("[ASR] connected to Julius module")

    buffer = ""

    while True:
        data = sock.recv(1024).decode("utf-8", errors="ignore")
        buffer += data

        if "</RECOGOUT>" in buffer:

            words = parse_julius_result(buffer)

            if words:
                print("\n--- RAW WORDS ---")
                print(words)

                command = classify_command(words)
                attitude = judge_attitude(words)

                result = {
                    "wav_path": wav_path,
                    "raw_words": words,
                    "command": command,
                    "attitude": attitude
                }

                # ★追加：JSONログとして保存
                save_json_log(result)

                sock.close()
                return result

            buffer = ""


# テスト用
if __name__ == "__main__":
    out = recognize_once()
    print("\nFINAL OUTPUT:", out)

