# models 目录说明

本目录提供项目中的模型结构原型代码，用于流程验证与接口占位。

## 文件说明

- `base_model.py`：`EmoTTSModel` 主体结构（文本嵌入 + 情感嵌入 + Transformer + mel 预测头）。
- `emotion_encoder.py`：独立情感编码模块。
- `lora_config.py`：LoRA 配置入口（按后续训练脚本补全）。
- `vocoder.py`：声码器相关占位文件。
- `__init__.py`：模块导出。

## 当前状态

- 主要用于研究原型阶段，不等同于最终生产可用模型。
- 训练与推理完整链路仍需结合 `src/train.py` / `src/inference.py` 的后续版本实现。

