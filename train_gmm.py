import os
import librosa
import numpy as np
import pickle
import pathlib
from sklearn.mixture import GaussianMixture

# --- 特徴量抽出 ---
def extract_mfcc(path, sr=16000, n_mfcc=13):
    """WAVファイルからMFCC特徴量を抽出"""
    y, sr = librosa.load(path, sr=sr)
    # 無音を除去（オプション）
    y, _ = librosa.effects.trim(y, top_db=20)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T  # (フレーム数, 次元)

# --- 話者ごとのモデル学習 ---
def train_gmm(wav_files, n_components=8):
    """複数のwavファイルから特徴量をまとめてGMMを学習"""
    features = np.vstack([extract_mfcc(f) for f in wav_files])
    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type='diag',
        max_iter=200,
        random_state=42
    )
    gmm.fit(features)
    return gmm

# --- 判定関数 ---
def predict_speaker(test_wav, models):
    """未知のwavを判定し、ラベルと確信度を返す"""
    feat = extract_mfcc(test_wav)
    scores = {spk: model.score(feat) for spk, model in models.items()}
    best_spk = max(scores, key=scores.get)

    # 確信度をsoftmaxで算出
    exp_scores = np.exp(list(scores.values()))
    probs = exp_scores / np.sum(exp_scores)

    return best_spk, dict(zip(scores.keys(), probs))

# --- メイン処理例 ---
if __name__ == "__main__":
    # フォルダ構造例:
    # data/parent/*.wav
    # data/child/*.wav


    base_dir = "data"
    speakers = ["parent", "child"]

    # 学習
    models = {}
    for spk in speakers:
        wav_files = [os.path.join(base_dir, spk, f)
                     for f in os.listdir(os.path.join(base_dir, spk))
                     if f.endswith(".wav")]
        models[spk] = train_gmm(wav_files)

    

    pathlib.Path("models").mkdir(exist_ok=True)
    with open("models/gmm.pkl", "wb") as f:
        pickle.dump(models, f)



    # 判定テスト
    test_file = "data/child/child_b05.wav"
    label, probs = predict_speaker(test_file, models)
    print("判定:", label)
    print("確信度:", probs)









