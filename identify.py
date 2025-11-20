import pickle
import numpy as np
import torch
import librosa
import os
from speechbrain.inference import EncoderClassifier

# グローバル変数でモデルとECAPAエンコーダーをキャッシュ
_models = None
_classifier = None

def get_ecapa_classifier():
    """ECAPA-TDNNエンコーダーを遅延ロード"""
    global _classifier
    if _classifier is None:
        print("🔄 ECAPA-TDNNモデルをロード中...")
        _classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/ecapa"
        )
        print("✅ ECAPA-TDNNモデルのロード完了")
    return _classifier

def get_embedding(wav_path, sr=16000):
    """
    音声ファイルからECAPA-TDNNのembeddingを取得
    test_ECAPA.pyと同じ方法
    """
    print(f"🔍 embedding抽出開始: {wav_path}")
    
    # 音声読み込み
    signal, actual_sr = librosa.load(wav_path, sr=sr)
    print(f"   - 読み込み: サンプリングレート={actual_sr}Hz, サンプル数={len(signal)}")
    print(f"   - 長さ: {len(signal)/actual_sr:.2f}秒")
    print(f"   - RMSレベル: {np.sqrt(np.mean(signal**2)):.6f}")
    
    # float32に変換してtorch tensorに
    signal = signal.astype(np.float32)
    signal = torch.from_numpy(signal).unsqueeze(0)
    
    # ECAPA-TDNNでembeddingを取得
    classifier = get_ecapa_classifier()
    embedding = classifier.encode_batch(signal)
    embedding_np = embedding.squeeze().cpu().numpy()
    
    print(f"   - Embedding形状: {embedding_np.shape}")
    print(f"   - Embedding範囲: [{np.min(embedding_np):.3f}, {np.max(embedding_np):.3f}]")
    
    return embedding_np

def cosine_similarity(vec1, vec2):
    """コサイン類似度を計算"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def load_models():
    """話者embeddingモデルを遅延ロード"""
    global _models
    if _models is None:
        model_path = "models/ecapa.pkl"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")
        with open(model_path, "rb") as f:
            _models = pickle.load(f)   # {"parent": embedding_array, "child": embedding_array}
        print(f"✅ 話者モデルをロード: {list(_models.keys())}")
    return _models

def identify(wav_path):
    """
    音声ファイルから話者を識別
    test_ECAPA.pyと同じロジック
    """
    print(f"\n{'='*60}")
    print(f"🎯 話者識別開始: {wav_path}")
    
    # 登録済み話者embeddingをロード
    models = load_models()
    print(f"📚 登録話者: {list(models.keys())}")
    
    # テスト音声のembeddingを取得
    test_embedding = get_embedding(wav_path)
    
    # 各話者embeddingとの類似度を計算
    scores = {}
    print(f"\n📊 類似度計算:")
    for speaker, model_embedding in models.items():
        similarity = cosine_similarity(test_embedding, model_embedding)
        scores[speaker] = similarity
        print(f"   {speaker}: コサイン類似度 = {similarity:.6f}")
    
    # 最も類似度が高い話者を選択
    best_speaker = max(scores, key=scores.get)
    
    # softmaxで確信度に変換
    print(f"\n🔢 確信度計算 (softmax):")
    exp_scores = np.exp(list(scores.values()))
    probs_array = exp_scores / np.sum(exp_scores)
    probs = dict(zip(scores.keys(), probs_array))
    
    # float型に変換（JSON互換性）
    probs = {k: float(v) for k, v in probs.items()}
    
    print(f"   確信度: {probs}")
    
    print(f"\n✅ 識別結果:")
    print(f"   予測: {best_speaker}")
    print(f"   確信度: {probs[best_speaker]*100:.2f}%")
    print(f"{'='*60}\n")
    
    return best_speaker, probs

if __name__ == "__main__":
    # テスト用: 未知の音声ファイルを指定
    test_files = [
        "data/test/child2_b01.wav",
        "uploads/input.wav"
    ]
    
    for wav_path in test_files:
        if os.path.exists(wav_path):
            label, confidence = identify(wav_path)
            print("判定:", label)
            print("確信度:", confidence)
            print("\n")
        else:
            print(f"⚠️  ファイルが見つかりません: {wav_path}\n")
