# src/models/base_model.py
import torch
import torch.nn as nn

class EmoTTSModel(nn.Module):
    """
    基于文本的情感语音大模型
    输入：文本 + 情感标签
    输出：梅尔频谱图（后续由声码器转为音频）
    """
    
    def __init__(self, 
                 vocab_size=5000,      # 文本词汇表大小
                 embed_dim=512,        # 嵌入维度
                 num_heads=8,          # 注意力头数
                 num_layers=6,         # Transformer 层数
                 emotion_dim=128,      # 情感嵌入维度
                 num_emotions=5,       # 情感类别数
                 max_seq_len=512):     # 最大序列长度
        super().__init__()
        
        # 1. 文本编码器
        self.text_embedding = nn.Embedding(vocab_size, embed_dim)
        
        # 2. 情感编码器
        self.emotion_embedding = nn.Embedding(num_emotions, emotion_dim)
        
        # 3. Transformer 编码器（核心）
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=num_heads,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # 4. 频谱预测头
        self.mel_predictor = nn.Linear(embed_dim, 80)  # 80 维梅尔频谱
        
        # 5. 位置编码（简化版）
        self.pos_encoding = nn.Parameter(torch.randn(1, max_seq_len, embed_dim))
        
    def forward(self, text_ids, emotion_ids, text_lengths=None):
        """
        前向传播
        Args:
            text_ids: [batch, seq_len] 文本 token ID
            emotion_ids: [batch] 情感标签 ID
            text_lengths: [batch] 文本实际长度（用于 padding mask）
        Returns:
            mel_spec: [batch, seq_len, 80] 梅尔频谱
        """
        # 1. 文本嵌入
        text_emb = self.text_embedding(text_ids)  # [batch, seq_len, embed_dim]
        text_emb = text_emb + self.pos_encoding[:, :text_emb.size(1), :]
        
        # 2. 情感嵌入（广播到序列维度）
        emotion_emb = self.emotion_embedding(emotion_ids)  # [batch, emotion_dim]
        emotion_emb = emotion_emb.unsqueeze(1).expand(-1, text_emb.size(1), -1)
        
        # 3. 融合文本 + 情感
        fused_emb = text_emb + emotion_emb  # [batch, seq_len, embed_dim]
        
        # 4. Transformer 编码
        # 可选：添加 padding mask
        output = self.transformer_encoder(fused_emb)  # [batch, seq_len, embed_dim]
        
        # 5. 预测梅尔频谱
        mel_spec = self.mel_predictor(output)  # [batch, seq_len, 80]
        
        return mel_spec
    
    def generate(self, text_ids, emotion_ids, max_len=200):
        """
        推理生成（简化版）
        实际项目中可能需要自回归生成逻辑
        """
        self.eval()
        with torch.no_grad():
            mel_spec = self.forward(text_ids, emotion_ids)
        return mel_spec