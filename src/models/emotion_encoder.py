# src/models/emotion_encoder.py
import torch.nn as nn

class EmotionEncoder(nn.Module):
    """
    情感特征编码模块
    可将情感标签转换为稠密向量，支持细粒度情感控制
    """
    
    def __init__(self, num_emotions=5, embed_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(num_emotions, embed_dim)
        self.projection = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim)
        )
    
    def forward(self, emotion_ids):
        emb = self.embedding(emotion_ids)
        return self.projection(emb)