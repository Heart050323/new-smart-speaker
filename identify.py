import pickle
import numpy as np
import librosa
import os

# グローバル変数でモデルをキャッシュ
_models = None

# 特徴量抽出関数（train_gmm.pyと共通化しておくと便利）
def extract_features(wav_path, sr=16000, n_mfcc=13):
    y, sr = librosa.load(wav_path, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T  # (フレーム数, 次元数)

def load_models():
    """モデルを遅延ロード"""
    global _models
    if _models is None:
        model_path = "models/gmm.pkl"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}\ntrain_gmm.pyでモデルを学習してください。")
        with open(model_path, "rb") as f:
            _models = pickle.load(f)   # 例: {"parent": gmm_parent, "child": gmm_child}
    return _models

def identify(wav_path):
    models = load_models()
    features = extract_features(wav_path)
    scores = {}
    for label, model in models.items():
        scores[label] = model.score(features)  # 対数尤度

    # softmaxで確信度に変換
    exp_scores = np.exp(list(scores.values()))
    probs = exp_scores / np.sum(exp_scores)

    result = dict(zip(scores.keys(), probs))
    predicted = max(result, key=result.get)

    return predicted, result

if __name__ == "__main__":
    # テスト用: 未知の音声ファイルを指定
    wav_path = "data/test/child2_b01.wav"
    label, confidence = identify(wav_path)
    print("判定:", label)
    print("確信度:", confidence)
