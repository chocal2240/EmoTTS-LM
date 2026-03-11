# 🎙️ EmoTTS-LM: 基于文本的情感语音大模型

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-in%20development-orange)](https://github.com/yourusername/EmoTTS-LM)

> **项目简介**：本项目旨在构建一个能够根据文本内容自动生成带有特定情感色彩语音的大模型。支持多种情感控制（如高兴、悲伤、愤怒等），实现高自然度的情感语音合成。
>
> **Project Description**: This project aims to build a large model capable of automatically generating speech with specific emotional colors based on text content. It supports multiple emotion controls (e.g., happy, sad, angry) to achieve high-naturalness emotional speech synthesis.

---

## 📰 更新日志 (News)

<!-- 请随项目进展动态更新此处 -->
- **[2024-XX-XX]**: 项目初始化，仓库建立 (Project initialized).
- **[TODO]**: 完成数据预处理模块 (Complete data preprocessing).
- **[TODO]**: 完成基线模型搭建 (Complete baseline model).
- **[TODO]**: 发布第一个 Demo 音频 (Release first demo audio).

---

## ✨ 主要功能 (Features)

- 🎯 **多情感控制 (Multi-emotion Control)**：支持通过文本标签控制输出语音的情感色彩。
- 🚀 **高自然度 (High Naturalness)**：基于 Transformer 架构，生成语音流畅自然。
- 📚 **端到端训练 (End-to-End Training)**：提供完整的训练与推理 pipeline。
- 🛠️ **易于扩展 (Easy to Extend)**：模块化代码设计，方便添加新情感或调整模型结构。

---

## 📦 安装指南 (Installation)

### 1. 环境准备 (Environment Setup)
确保已安装 Python 3.8+ 和 PyTorch。

```bash
# 克隆仓库 (Clone Repository)
git clone https://github.com/yourusername/EmoTTS-LM.git
cd EmoTTS-LM

# 创建虚拟环境 (Create Virtual Environment)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# 安装依赖 (Install Dependencies)
pip install -r requirements.txt
```

### 2. 数据准备 (Data Preparation)
由于数据集较大，未包含在仓库中。请参考 [data/README.md](data/README.md) 下载数据集并放置到 `data/raw/` 目录。

### 3. 模型权重 (Model Weights)
预训练权重请参考 [Checkpoints](#checkpoints) 部分下载。

---

## 🚀 快速开始 (Quick Start)

### 推理示例 (Inference)
```bash
python src/inference.py --text "今天天气真好" --emotion "happy" --output ./output.wav
```

### 训练示例 (Training)
```bash
python src/train.py --config configs/default.yaml
```

---

## 🎧 在线演示 (Demo)

| 文本内容 (Text) | 情感 (Emotion) | 音频预览 (Audio Preview) |
| :--- | :---: | :---: |
| "恭喜你获得了第一名！" | 😄 Happy | 🔊 [播放音频](assets/demo_happy.wav) |
| "很遗憾听到这个消息..." | 😢 Sad | 🔊 [播放音频](assets/demo_sad.wav) |
| "你怎么能这样对我？" | 😡 Angry | 🔊 [播放音频](assets/demo_angry.wav) |

*(注：以上音频为占位符，项目进展后将更新真实生成效果)*

---

## 🏆 项目背景 (Project Background)

本项目受 **校级大学生创新创业训练计划** 资助。  
This work is supported by the **University-level Undergraduate Training Program for Innovation and Entrepreneurship**.

- **项目编号 (Grant No.)**: `[请填写项目编号]`
- **项目级别 (Project Level)**: 校级 (University-level)

--- 

## 📚 参考文献 (References)


---

## 📄 许可证 (License)

本项目采用 [MIT 许可证](LICENSE) 开源。  
This project is licensed under the [MIT License](LICENSE).

---

## 📬 联系方式 (Contact)

如有问题或合作意向，请通过以下方式联系：  
For any questions or collaboration inquiries, please contact:

- 📧 **Email**: `fanqt2024@lzu.edu.cn`
- 🐱 **GitHub**: [`chocalbushnell-dotcom`](https://github.com/chocalbushnell-dotcom)