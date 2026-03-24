# data 目录说明

本目录用于存放训练与数据处理阶段的中间文件，不作为对外发布数据集的主入口。

## 目录约定

- raw/: 原始文本或原始语音数据（不建议直接提交大文件）
- generated/: 生成后的中间数据（如增强文本、伪标签结果）

## 当前推荐的数据入口

如果你要直接使用本项目已整理的数据，请优先查看：

- dataset/dataset_publish/

其中 dataset/dataset_publish/dataset_manifest.txt 提供了音频与文本映射关系。

## 数据处理脚本现状

当前仓库中与数据生成相关的可用入口：

- src/data_generation/llm_generator.py

运行前请准备环境变量（.env）：

- LLM_API_KEY
- LLM_API_BASE_URL
- LLM_MODEL_NAME

示例：

```bash
python src/data_generation/llm_generator.py
```

## 说明

- data 目录的内容可根据实验迭代频繁变化，建议在本地维护。
- 音频目录 dataset/dataset_wavs/ 默认不随仓库提交，建议单独存储或通过发布包分发。
- 对外共享或论文复现请优先引用 dataset 目录中的发布版文件。