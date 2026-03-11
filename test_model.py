# test_model.py
import torch
from src.models import EmoTTSModel

# 初始化模型
model = EmoTTSModel(vocab_size=1000, embed_dim=256, num_emotions=5)

# 模拟输入
batch_size = 2
text_ids = torch.randint(0, 1000, (batch_size, 50))  # 随机文本 token
emotion_ids = torch.randint(0, 5, (batch_size,))     # 随机情感标签

# 前向传播
output = model(text_ids, emotion_ids)
print(f"✓ 模型测试通过！输出形状：{output.shape}")
# 预期输出：[2, 50, 80]