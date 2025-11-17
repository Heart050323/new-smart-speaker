# tts.py
import subprocess
import os
import time

def speak(text):
    print(f"System: {text}") # ログ確認用

    # Open JTalkの設定（パスは環境に合わせて確認してください）
    dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
    voice_path = "/usr/share/hts-voice/mei/mei_normal.htsvoice"
    output_file = "output.wav"

    # 音声生成
    cmd = [
        'open_jtalk',
        '-x', dic_path,
        '-m', voice_path,
        '-ow', output_file
    ]

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    p.communicate(text.encode('utf-8'))
    p.wait()

    # 再生 (aplayを使用)
    subprocess.run(['aplay', '-q', output_file])

if __name__ == "__main__":
    speak("お母さんスイッチ、システム起動。")