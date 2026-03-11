# 数据集说明 (Dataset Information)

由于数据集体积较大，未直接上传至 GitHub。请使用以下方式获取数据：

## 1. 公开数据集
- **Dataset Name**: [例如：ESD / IEMOCAP]
- **Download Link**: [填写百度网盘链接或官方网址]
- **Placement**: 下载后解压至 `data/raw/` 目录。

## 2. 数据格式
- 音频格式：`.wav` (16kHz, mono)
- 标注格式：`.json` / `.txt`

## 3. 预处理
运行 `python src/utils/preprocess.py` 即可生成处理后的数据至 `data/processed/`。

## 数据生成说明

由于版权和体积限制，完整数据集未上传。您可以使用以下脚本自行生成：

1. 配置 API Key: 复制 `.env.example` 为 `.env` 并填入 Key。
2. 运行生成脚本:
   ```bash
   python src/data_generation/llm_generator.py
   ```