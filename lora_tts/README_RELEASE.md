# 模型与应用发布包（GitHub Release）

该目录已整理为可直接上传 GitHub Release 的资产源。

## 已包含内容

- app/: GUI 应用源码与 Windows 启动脚本
- model/: 最终 LoRA 适配器权重
- server/: API 服务端代码与启动脚本
- docs/: 安装、连接和发布说明

## 体积说明

- app/main.py: 42,706 bytes
- model/adapter_model.safetensors: 77,001,600 bytes（约 73.4 MiB）

## 重要说明

- 模型包仅包含 LoRA 适配器，不包含 Qwen3-TTS 基座模型
- 应用端需要连接服务端 API 才能生成语音
