# 話者同定プロジェクト

## 実行環境
- OS: Ubuntu 22.04 / 24.04 推奨
- Python: 3.12.x
- pip: 最新版 (`sudo apt install python3-pip`)
- libasoun2-dev (`sudo apt install build-essential portaudio19-dev libasound2-dev`)

  インストールしておいてほしい諸々
  python3 -m venv .venv      仮想環境作成
  source .venv/bin/activate　　　　仮想環境に変更
  pip install -r requirements.txt　　　　インストール



推奨フォルダ構造
project_root/
├── data/                # 学習用データ
│   ├── parent/          # 親の音声
│   │   ├── session1_b01.wav
│   │   ├── session1_b02.wav
│   │   └── ...
│   └── child/           # 子供の音声
│       ├── session1_b01.wav
│       ├── session1_b02.wav
│       └── ...
├── models/
│   └── gmm.pkl        ← 学習済みモデル
├── record_hybrid.py     # 録音用スクリプト
├── train_gmm.py         # 学習・判定用スクリプト
├── sentence.txt         # 録音用の台本
├── requirements.txt     # 依存ライブラリ
└── README.md            # このファイル


Ubunruならシェルでかんたんに音声ファイル名を変更できる
たとえばs3→childならdata/childフォルダで

cd ~/memberB/data/child

# s3_bXX.wav → child_bXX.wav に一括変換
for f in s3_b*.wav; do
    mv "$f" "child_${f#s3_}"
done




各Pythonファイルの使い方
１．録音用スクリプト(record_hybrid.py)
サンプリングレートなどは固定
SR = 16000        # サンプリングレート 16kHz
CH = 1            # チャンネル数 1（モノラル）
SAMPLE_WIDTH = 2  # サンプル幅 2バイト = 16bit PCM

使い方：python record_hybrid.py --speaker [speaker]
sentence.txtを参照して、録音対象の文章を提示し、data/speaker/speaker_bXX.wavで保存

２.学習判定用スクリプト(train_gmm.py)
使い方：python train_gmm.py
入力：data/parent/とdata/child/のWAVファイル（可変）(l49あたりの配列の中身を変えればいい)

出力：標準出力に判定結果
判定: child
確信度: {'parent': 0.05, 'child': 0.95}

models/gmm.pklにモデルファイルを保存

３.判定用スクリプト(identify.py)
使い方：identify.py --wav [音声ファイルのパス]
入力：学習済みモデルファイル：models/gmm.pkl
入力；判定対象のWAVファイルファイル
出力：標準出力に判定結果と確信度を表示
判定: child
確信度: {'parent': 0.22, 'child': 0.77}

※確信度はGMMスコアをsoftmax変換して０〜１の範囲に正規化

