#! /usr/bin/env python3
# record_hybrid.py : Python版録音スクリプト（record.pl 上位互換＋ハイブリッド）
# Author: チーム用

import wave
import webrtcvad
import sounddevice as sd
import numpy as np
from pathlib import Path
import argparse
import simpleaudio as sa
import threading
import queue


SR = 16000
CH = 1
SAMPLE_WIDTH = 2  # 16-bit PCM

#--speaker引数に渡した文字列がそのままファイル名に使われるので、話者ごとに別の名前を指定すれば何人でも録音可能。　python record_cli.py --speaker parentとかchild１とか

# --- ユーティリティ関数 ---
def play_wav(path):
    """WAVファイルを再生"""
    if Path(path).exists():
        wave_obj = sa.WaveObject.from_wave_file(str(path))
        play_obj = wave_obj.play()
        play_obj.wait_done()
    else:
        print(f"音声ファイルが見つかりません: {path}")

def load_sentences(sentence_file):
    """台本ファイルを読み込む (番号:漢字:かな)"""
    sentences = []
    with open(sentence_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) >= 3:
                num, kanji, kana = parts[0], parts[1], parts[2]
                sentences.append({"num": num, "kanji": kanji, "kana": kana})
    return sentences

def write_wave(path, audio):
    """録音データをWAV保存"""
    audio_i16 = np.int16(np.clip(audio, -1.0, 1.0) * 32767)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(CH)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SR)
        wf.writeframes(audio_i16.tobytes())

# --- 録音処理 ---
def record_one(sentence, out_dir, speaker, play_sample=True):
    """台本提示＋録音＋保存"""
    print(f"\n[{sentence['num']}] {sentence['kana']} / {sentence['kanji']}")
    if play_sample:
        sample_path = Path("sample") / f"{sentence['num']}.wav"
        if sample_path.exists():
            print("お手本を再生します...")
            play_wav(sample_path)

    print("話してください（自動で録音開始/終了します）...")

    #VADの感度は０〜３で数値が大きいほど激しく判定
    vad = webrtcvad.Vad(2)
    with sd.InputStream(samplerate=SR, channels=CH, dtype='int16') as stream:
        segment = []
        triggered = False
        silence_count = 0
        while True:
            audio_block, _ = stream.read(int(SR * 0.03))  # 30ms
            audio_block = audio_block.flatten()
            is_speech = vad.is_speech(audio_block.tobytes(), SR)

            if is_speech:
                if not triggered:
                    triggered = True
                    segment = []
                    print("録音開始...")
                segment.extend(audio_block.tolist())
                silence_count = 0
            else:
                if triggered:
                    silence_count += 1
                    if silence_count > int(1.0 / 0.03):  # 約1秒無音で終了
                        print("録音終了")
                        seg = np.array(segment, dtype=np.float32)

                        # 前に0.3秒の無音を追加
                        margin = int(SR * 0.3)
                        seg = np.concatenate([np.zeros(margin), seg])

                        # 末尾の無音を0.7秒削除して、残り0.3秒にする
                        seg = seg[:-int(SR * 0.7)]

                        dur = len(seg) / SR
                        if 0.8 <= dur <= 5.0:
                            fname = f"{speaker}_{sentence['num']}.wav"
                            path = Path(out_dir) / fname
                            write_wave(path, seg)
                            print(f"保存しました: {path} ({dur:.2f}s)")
                        else:
                            print(f"破棄: {dur:.2f}s (短すぎ/長すぎ)")
                        break




def parse_targets(targets_str):
    """入力文字列から録音対象番号を抽出"""
    if not targets_str:
        return []  # 空なら全文録音
    targets = []
    if targets_str.startswith("b[") and targets_str.endswith("]"):
        # 例: b[2,5,7]
        nums = targets_str[2:-1].split(",")
        targets = [f"b{n}" for n in nums]
    elif targets_str.startswith("b"):
        # 例: b13
        targets = [targets_str]
    return targets

def filter_sentences(sentences, targets):
    """対象番号に基づいて文リストをフィルタ"""
    if not targets:
        return sentences
    return [s for s in sentences if s["num"] in targets]


# 入力監視用のキュー
command_queue = queue.Queue()

def input_listener():
    """ユーザー入力を常時監視してコマンドをキューに入れる"""
    while True:
        cmd = input().strip()
        command_queue.put(cmd)

# --- ヘルプ表示 ---
def help_message():
    print("\n[使い方]")
    print("  r   : 録音する（お手本再生後）")
    print("  R   : 録音やり直し（お手本なし）")
    print("  l   : 録音済み音声を再生")
    print("  t   : お手本を再生")
    print("  n   : 次の文へ進む")
    print("  b   : 前の文へ戻る")
    print("  m X : 文章 X へ移動（例: m b01）")
    print("  h   : このメッセージ")
    print("  q   : 終了\n")

# --- コマンド操作モード ---
def interactive_loop(sentences, out_dir, speaker):
    i = 0
    while True:
        s = sentences[i]
        print(f"\n[{s['num']}] {s['kana']} / {s['kanji']}")
        print("% ", end="")
        cmd = input().strip()

        if cmd == "h":
            help_message()
        elif cmd == "r":
            sample_path = Path("sample") / f"{s['num']}.wav"
            if sample_path.exists():
                play_wav(sample_path)
            record_one(s, out_dir, speaker)
        elif cmd == "R":
            record_one(s, out_dir, speaker, play_sample=False)
        elif cmd == "l":
            out_file = Path(out_dir) / f"{speaker}_{s['num']}.wav"
            if out_file.exists():
                play_wav(out_file)
            else:
                print("録音済み音声がありません")
        elif cmd == "t":
            sample_path = Path("sample") / f"{s['num']}.wav"
            if sample_path.exists():
                play_wav(sample_path)
        elif cmd == "n":
            i = min(i + 1, len(sentences) - 1)
        elif cmd == "b":
            i = max(i - 1, 0)
        elif cmd.startswith("m "):
            target = cmd.split()[1]
            for j, s2 in enumerate(sentences):
                if s2["num"] == target:
                    i = j
                    break
        elif cmd == "q":
            print("終了します")
            break

# --- 完全自動進行モード（割り込み可能） ---
def auto_full(sentences, out_dir, speaker):
    # 入力監視スレッドを起動
    threading.Thread(target=input_listener, daemon=True).start()

    i = 0
    while i < len(sentences):
        s = sentences[i]
        print(f"\n[{s['num']}] {s['kana']} / {s['kanji']}")
        print("録音中... (skip/stop/quitで割り込み可能)")

        record_one(s, out_dir, speaker)  # 自動で録音開始→終了

        # 割り込みコマンド確認
        while not command_queue.empty():
            cmd = command_queue.get()
            if cmd == "skip":
                print("この文をスキップしました")
                break  # 次の文へ
            elif cmd == "stop":
                print("録音を中止しました。この文は破棄されます")
                break  # 次の文へ
            elif cmd == "quit":
                print("自動進行モードを終了します")
                return
        i += 1

    # 再開機能
    print("\n録音を中断しました。途中から再開する場合は文番号を入力してください (例: b15)")
    resume = input("再開番号 > ").strip()
    if resume:
        for j, s2 in enumerate(sentences):
            if s2["num"] == resume:
                auto_full(sentences[j:], out_dir, speaker)
                break

# --- メイン処理 ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, default="data")
    parser.add_argument("--speaker", type=str, required=True)
    parser.add_argument("--sentence", type=str, default="sentence.txt")
    args = parser.parse_args()

    Path(f"{args.out}/{args.speaker}").mkdir(parents=True, exist_ok=True)
    sentences = load_sentences(args.sentence)

    # 起動後に録音対象を指定
    targets_str = input("録音対象を指定してください (例: b[2,5,7] または b13、空Enterで全文録音) > ").strip()
    targets = parse_targets(targets_str)
    sentences = filter_sentences(sentences, targets)

    # モード選択（cmd と full のみ）
    mode = input("モード選択: cmd=コマンド操作 / full=完全自動 > ").strip()
    if mode == "full":
        auto_full(sentences, f"{args.out}/{args.speaker}", args.speaker)
    else:
        interactive_loop(sentences, f"{args.out}/{args.speaker}", args.speaker)

if __name__ == "__main__":
    main()
