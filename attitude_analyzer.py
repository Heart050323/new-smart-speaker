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
    polite = ["ください", "お願い", "ちょうだい", "つけて", "してください", "いただけ"]
    
    # 乱暴な表現
    rude = ["つけろ", "くれ", "しろ", "やれ", "だまれ", "うるさい"]

    # 丁寧な表現を優先チェック
    for p in polite:
        if p in joined:
            return "polite"

    # 乱暴な表現をチェック
    for r in rude:
        if r in joined:
            return "rude"

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
        "EXIT": "システムを終了します"
    }
    
    base_message = command_messages.get(command, "コマンドを実行します")
    
    # 母親の場合
    if speaker == "MOTHER":
        if attitude == "polite":
            return f"はい、お母さん。{base_message}。"
        elif attitude == "rude":
            return f"お母さん、承知しました。{base_message}。"
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
