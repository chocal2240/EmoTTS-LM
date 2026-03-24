# 安装与连接说明

本发布包分为两个部分：

- 应用端（Windows 客户端 GUI）
- 模型服务端（Linux GPU API）

## 1. 目录说明

- app/: GUI 应用代码（main.py）
- model/: LoRA 适配器（adapter_model.safetensors + adapter_config.json）
- server/: API 服务代码（api_server.py + tts_text_enhancer.py）

## 2. 服务端部署（Linux）

1) 准备 Python 环境并安装依赖

cd server
pip install -r requirements-server.txt

2) 配置环境变量并启动

export BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base
export ADAPTER_PATH=/abs/path/to/model
export REF_AUDIO_DEFAULT=/abs/path/to/ref.wav
export API_KEY=sk-test

bash start_server.sh

3) 健康检查

curl http://127.0.0.1:8000/health

如果需要外网访问，请放行 8000 端口，并将客户端里的 API URL 改成 http://你的服务器IP:8000/v1/tts。

## 3. 客户端部署（Windows）

1) 安装 Python 3.10+
2) 进入 app 目录，双击 run_app.bat
3) 首次运行会自动创建虚拟环境并安装依赖

你也可以手动执行：

py -m venv venv
venv\Scripts\activate
pip install -r requirements-app.txt
python main.py

## 4. 连接模型

在 GUI 的“模型设置”中：

- API URL: http://你的服务器IP:8000/v1/tts
- API Key: 与服务端 API_KEY 一致（示例 sk-test）

说明：

- ADAPTER_PATH 需要填写“模型目录路径”，即包含 adapter_model.safetensors 和 adapter_config.json 的目录
- 本发布包中该目录名为 model

应用会通过 API 调用服务端模型；如果服务端关闭，客户端仍能打开，但无法生成语音。

## 5. 关于模型体积

- LoRA 适配器权重文件 adapter_model.safetensors 大小约 77,001,600 字节（约 73.4 MiB）
- 这只是增量适配器，不包含基座模型
- 基座模型 Qwen3-TTS-1.7B 需在服务端额外准备（通常为数 GB）
