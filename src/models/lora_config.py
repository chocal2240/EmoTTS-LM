# src/models/lora_config.py
from peft import LoraConfig

def get_lora_config(r=8, lora_alpha=32):
    """获取 LoRA 配置，用于微调"""
    return LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        target_modules=["text_embedding", "transformer_encoder"],  # 根据实际层名调整
        lora_dropout=0.1,
        bias="none"
    )