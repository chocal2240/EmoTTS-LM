# EmoTTS-LM

文本驱动的心理咨询场景情感语音合成项目（Qwen3-TTS + LoRA）。

本仓库当前定位是研究型仓库：提供已发布数据集、阶段性实验结果、原型代码与文档材料。

## 项目目标

围绕心理健康辅助交互场景，构建可控制情感与语速的中文语音合成流程，重点关注“安抚/平静/鼓励”等表达风格。

## 当前成果

- 完成 PsyQA 文本清洗、规范化与扩展。
- 生成并发布情感语音数据集（1500 条）。
- 完成 LoRA 定向微调与阶段性验证。
- 提供论文草稿与数据集卡片，支持结果说明与复核。

## 关键结果

- BERT 弱监督情感分类准确率：0.9659
- 发布数据量：1500
- 情感分布：calm 764 / excited 736
- 数据清洗后回答保留率：92.39%

说明：音频文件体积较大，仓库默认不提交 `dataset_wavs` 音频目录，仅保留发布清单与统计信息。

详细说明：

- 报告草稿：`doc.txt`
- 数据集说明：`dataset/dataset_publish/README.md`
- 数据集卡片：`dataset/dataset_publish/DATASET_CARD.md`

## 仓库结构

```text
EmoTTS-LM/
|- src/
|  |- data_generation/         # LLM 数据增强与标注相关脚本
|  |- models/                  # 模型结构原型
|  `- utils/
|- dataset/
|  `- dataset_publish/         # 发布说明、清单、统计
|- data/                       # 中间数据目录与约定
|- checkpoints/                # 权重目录（当前未随仓库发布）
|- assets/
|- doc/                        # 文档目录（索引见 doc/README.md）
|- doc.txt                     # 论文草稿（持续修订）
|- test_model.py               # 模型结构冒烟测试
`- requirements.txt
```

> 注：如需完整音频，请在本地额外准备 `dataset/dataset_wavs/`，并与 `dataset/dataset_publish/dataset_manifest.txt` 配套使用。

## 快速开始

### 1. 环境安装

```bash
git clone <your-repo-url>
cd EmoTTS-LM
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 校验发布数据

```bash
python -c "import pandas as pd; df = pd.read_csv('dataset/dataset_publish/dataset_manifest.txt', sep='\t'); print('samples:', len(df)); print(df['emotion'].value_counts().to_string())"
```

### 3. 运行模型结构冒烟测试

```bash
python test_model.py
```

### 4. 运行 LLM 增强脚本

```bash
# 需先在 .env 中配置 LLM_API_KEY / LLM_API_BASE_URL / LLM_MODEL_NAME
python src/data_generation/llm_generator.py
```

## 复现边界说明

当前仓库中的 `src/train.py` 与 `src/inference.py` 仍是原型流程脚手架，不是最终版可复现实验脚本。

可直接复用的部分：

- 发布数据集与清单
- 数据增强调用示例
- 基础模型结构原型

暂未完整开源的部分：

- 最终训练流水线（包含完整 LoRA 训练配置）
- 可直接推理的最终适配器权重
- 完整演示程序入口

如果用于论文复现，建议以 `dataset/dataset_publish/` 与 `doc.txt` 结果描述为基准，并按你的本地实验环境补全训练与推理脚本。

## 后续计划

- 补齐可复现实验版训练脚本与推理脚本。
- 发布 LoRA 适配器与加载说明。
- 增加 demo 音频与评测脚本（主观/客观指标）。

## 许可证

本项目使用 [MIT License](LICENSE)。

## 联系方式

- Email: fanqt2024@lzu.edu.cn
- GitHub: https://github.com/chocal2240/EmoTTS-LM