#!/usr/bin/env python3
"""
態度分析・コマンド分類モジュール
client.pyから抽出した態度判定とコマンド分類機能
"""

import re


def classify_command(words):
    """
    認識された単語リストからコマンドを分類
    
    Args:
        words: 単語のリスト or 文字列
    
    Returns:
        str: コマンド名 (TV_ON, TV_OFF, LIGHT_ON, LIGHT_OFF, GET_SNACK, EXIT, None)
    """
    if isinstance(words, str):
        joined = words
    else:
        joined = "".join(words)

    if "テレビ" in joined:
        if "つけ" in joined:
            return "TV_ON"
        if "けし" in joined or "消し" in joined:
            return "TV_OFF"

    if "電気" in joined:
        if "つけ" in joined:
            return "LIGHT_ON"
        if "けし" in joined or "消し" in joined:
            return "LIGHT_OFF"

    if "おやつ" in joined:
        if "ちょうだい" in joined or "ください" in joined:
            return "GET_SNACK"
        return "SNACK"

    if "アラーム" in joined:
        if "かけ" in joined:
            return "ALARM_ON"
        if "けし" in joined or "とめ" in joined:
            return "ALARM_OFF"

    if "音楽" in joined:
        if "かけ" in joined:
            return "MUSIC_ON"
        if "けし" in joined or "とめ" in joined:
            return "MUSIC_OFF"

    if "音量" in joined:
        if "上げ" in joined:
            return "VOLUME_UP"
        if "下げ" in joined:
            return "VOLUME_DOWN"

    if "カーテン" in joined:
        if "開け" in joined:
            return "CURTAIN_OPEN"
        if "閉め" in joined:
            return "CURTAIN_CLOSE"

    if "うるさい" in joined or "うるせ" in joined or "黙れ" in joined or "黙っ" in joined:
        return "INSULT"

    if "ありがとう" in joined:
        return "GRATITUDE"

    if "終了" in joined:
        return "EXIT"

    return None


def judge_attitude(words):
    """
    認識された単語リストから態度を判定
    
    Args:
        words: 単語のリスト or 文字列
    
    Returns:
        str: 態度 ("polite", "rude", "neutral")
    """
    if isinstance(words, str):
        joined = words
    else:
        joined = "".join(words)

    # 丁寧な表現
    polite = ["ください", "お願い", "ちょうだい", "つけて", "してください", "いただけ", "開けて", "閉めて", "上げて", "下げて"]
    
    # 乱暴な表現
    rude = ["つけろ", "くれ", "しろ", "やれ", "けせ", "開けろ", "閉めろ", "上げろ", "下げろ"]

    insult = ["うるさい", "うるせ", "黙れ", "黙っ"]
    gratitude = ["ありがとう"]

    # 丁寧な表現を優先チェック
    for p in polite:
        if p in joined:
            return "polite"

    # 乱暴な表現をチェック
    for r in rude:
        if r in joined:
            return "rude"

    for i in insult:
        if i in joined:
            return "insult"
            
    for g in gratitude:
        if g in joined:
            return "gratitude"

    return "neutral"


def get_response_by_attitude(command, attitude, speaker):
    """
    コマンド・態度・話者に応じた応答を生成
    
    Args:
        command: コマンド名
        attitude: 態度 (polite/rude/neutral)
        speaker: 話者 (MOTHER/CHILD)
    
    Returns:
        str: 応答メッセージ
    """
    
    # コマンド実行メッセージ
    command_messages = {
        "TV_ON": "テレビをつけます",
        "TV_OFF": "テレビを消します",
        "LIGHT_ON": "電気をつけます",
        "LIGHT_OFF": "電気を消します",
        "GET_SNACK": "おやつを用意します",
        "SNACK": "おやつの要求を受け取りました",
        "ALARM_ON": "アラームをセットします",
        "ALARM_OFF": "アラームを止めます",
        "MUSIC_ON": "音楽を再生します",
        "MUSIC_OFF": "音楽を止めます",
        "VOLUME_UP": "音量を上げます",
        "VOLUME_DOWN": "音量を下げます",
        "CURTAIN_OPEN": "カーテンを開けます",
        "CURTAIN_CLOSE": "カーテンを閉めます",
        "INSULT": "そんな言い方はよくありません",
        "GRATITUDE": "どういたしまして",
        "EXIT": "システムを終了します"
    }
    
    base_message = command_messages.get(command, "コマンドを実行します")
    
    # 母親の場合
    if speaker == "MOTHER":
        if attitude == "polite":
            return f"はい、お母さん。{base_message}。"
        elif attitude == "rude":
            return f"お母さん、承知しました。{base_message}。"
        elif attitude == "insult":
            return f"お母さん、悲しいです。{base_message}。"
        elif attitude == "gratitude":
            return f"どういたしまして、お母さん。"
        else:
            return f"かしこまりました。{base_message}。"
    
    # 子供の場合
    else:
        if attitude == "polite":
            if command in ["GET_SNACK"]:
                return f"いい子ですね。{base_message}。"
            else:
                return f"はい、{base_message}。"
        elif attitude == "rude":
            return "そんな言い方はダメですよ。お母さんを呼んでください。"
        elif attitude == "insult":
            return "そんなこと言う子は知りません。"
        elif attitude == "gratitude":
            return "どういたしまして。"
        else:
            # コマンドによって態度を変える
            if command in ["GET_SNACK"]:
                return "おやつは宿題が終わってからね。"
            elif command in ["TV_ON"]:
                return "テレビは勉強が終わってからです。"
            else:
                return "それはお母さんに頼んでください。"


# テスト用
if __name__ == "__main__":
    test_cases = [
        ("電気をつけてください", "CHILD"),
        ("電気つけろ", "CHILD"),
        ("テレビをつけて", "MOTHER"),
        ("おやつちょうだい", "CHILD"),
    ]
    
    for text, speaker in test_cases:
        command = classify_command(text)
        attitude = judge_attitude(text)
        response = get_response_by_attitude(command, attitude, speaker)
        
        print(f"\n入力: {text}")
        print(f"話者: {speaker}")
        print(f"コマンド: {command}")
        print(f"態度: {attitude}")
        print(f"応答: {response}")
