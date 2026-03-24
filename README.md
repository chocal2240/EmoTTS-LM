# EmoTTS-LM

本项目核心路线是基于 Qwen3-TTS 基座模型，通过 LoRA 参数高效微调，解决“基于文本驱动的心理咨询语音数据合成”任务。

本项目通过 GitHub Release 分发可部署资产，目标是让第三方下载后可直接完成服务端部署与客户端联调。

最新发行版已包含 1500 条语音数据集，可用于部署后功能验证与效果试听。

## 目录结构

```text
EmoTTS-LM/
|- .env.example
|- .gitignore
|- LICENSE
|- requirements.txt
`- README.md
```

## 发布版部署

### 第 1 步：下载发行版

从 Releases 下载并解压，建议保持 `lora_tts/` 目录结构不变。

发行版资产包括应用端、服务端、LoRA 适配器，以及 1500 条语音数据集。

### 第 2 步：服务端部署（Linux + GPU）

```bash
cd lora_tts/server
pip install -r requirements-server.txt

export BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base
export ADAPTER_PATH=/abs/path/to/lora_tts/model
export REF_AUDIO_DEFAULT=/abs/path/to/ref.wav
export API_KEY=sk-test

bash start_server.sh
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

### 第 3 步：客户端启动（Windows）

```bat
cd lora_tts\app
run_app.bat
```

首次运行会自动创建虚拟环境并安装依赖。

### 第 4 步：连接参数

在 GUI 中填写：

- API URL: `http://<SERVER_IP>:8000/v1/tts`
- API Key: 与服务端 `API_KEY` 保持一致
- Adapter Path: 可选（默认由服务端 `ADAPTER_PATH` 控制）

## 本地一体化部署

如果你希望在同一台机器直接跑通模型与应用，可按下面步骤执行。

### 方案 A：同机启动服务端 + 客户端

终端 A（启动服务端）：

```bash
cd lora_tts/server
pip install -r requirements-server.txt

export BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base
export ADAPTER_PATH=/abs/path/to/lora_tts/model
export REF_AUDIO_DEFAULT=/abs/path/to/ref.wav
export API_KEY=sk-local

bash start_server.sh
```

终端 B（启动客户端）：

```bat
cd lora_tts\app
run_app.bat
```

GUI 连接参数（同机）：

- API URL: `http://127.0.0.1:8000/v1/tts`
- API Key: `sk-local`

### 方案 B：仅本地验证服务端

```bash
curl http://127.0.0.1:8000/health
```

返回 `status: ok` 后，再启动 app 进行语音生成测试。

## 模型与数据说明

- 任务目标：将心理咨询场景文本转换为更具安抚性与共情感的语音输出。
- 方法主线：Qwen3-TTS 基座模型 + LoRA 微调（仅训练增量适配器，降低训练与部署成本）。
- `lora_tts/model/` 仅包含 LoRA 适配器（`adapter_model.safetensors` + `adapter_config.json`）。
- 发行版提供 1500 条语音数据集，便于部署后进行批量回放、主观听测和流程验证。
- 不包含 Qwen3-TTS 基座模型；需在服务端单独准备。
- `REF_AUDIO_DEFAULT` 必须是可访问的 wav 文件路径，否则推理请求会失败。

## 依赖说明

- 根目录 `requirements.txt` 是公开维护的聚合依赖（推荐保留在仓库中）。
- 客户端单独依赖：`lora_tts/app/requirements-app.txt`
- 服务端单独依赖：`lora_tts/server/requirements-server.txt`

快速安装（聚合）：

```bash
git clone https://github.com/chocal2240/EmoTTS-LM.git
cd EmoTTS-LM
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

按端安装：

```bash
pip install -r lora_tts/app/requirements-app.txt
pip install -r lora_tts/server/requirements-server.txt
```

## 常见问题

1. 客户端能打开但不能生成语音
原因：服务端未启动或 URL/API Key 配置错误。  
处理：先访问 `/health`，再检查 GUI 中 API URL 与 API Key。

2. 服务端报 `ref_audio not found`
原因：`REF_AUDIO_DEFAULT` 路径无效。  
处理：改成真实 wav 路径并重启服务端。

3. 生成失败或显存错误
原因：基座模型未正确安装或 GPU 资源不足。  
处理：确认 `BASE_MODEL` 可加载，并在有足够显存的设备运行。

## 许可证

本项目使用 [MIT License](LICENSE)。

## 联系方式

- Email: fanqt2024@lzu.edu.cn
- GitHub: https://github.com/chocal2240/EmoTTS-LM