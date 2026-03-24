# EmoTTS-LM

本项目核心路线是基于 Qwen3-TTS 基座模型，通过 LoRA 参数高效微调，解决“基于文本驱动的心理咨询语音数据合成”任务。

> **⚠️ 重要提示**：  
> 本项目仅提供 **模型训练代码** 与 **应用客户端**，**不提供公共 API 服务**。  
> 
> 要使用本软件，**您必须自行部署服务端**（可以是远程服务器或本地高性能电脑），随后并在客户端中配置连接地址。

本项目通过 GitHub Release 分发可部署资产，最新发行版已包含 1500 条语音数据集，可用于部署后功能验证与效果试听。

## 目录结构

```text
EmoTTS-LM/
|- .env.example
|- .gitignore
|- LICENSE
|- requirements.txt
`- README.md
```

## 部署模式说明

本项目采用 **Client-Server (客户端-服务端)** 架构，支持两种部署模式：

1. **远程部署（推荐）**：服务端部署在 Linux GPU 服务器上，客户端运行在个人 Windows 电脑上。
2. **本地部署**：服务端与客户端均运行在同一台带有 NVIDIA 显卡的 Windows 电脑上。

---

## 模式一：远程部署（Linux 服务端 + Windows 客户端）

### 1. 服务端部署 (Linux)
*适用场景：拥有云服务器或局域网 GPU服务器。*

请将 `lora_tts/server` 目录上传至服务器。

**环境要求：**
- 操作系统：Ubuntu 20.04+ / Debian 11+
- Python：3.10+
- GPU：NVIDIA 显卡（显存建议 12GB+）
- CUDA：11.8 或 12.1

**启动步骤：**
```bash
cd lora_tts/server
pip install -r requirements-server.txt

# 设置环境变量（建议写入启动脚本）
export BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base  # 基座模型路径或 HuggingFace ID
export ADAPTER_PATH=/your/path/to/lora_tts/model # 指向发行版中的 model 目录
export REF_AUDIO_DEFAULT=/your/path/to/ref.wav   # 发行版 data 目录下的任意 wav 文件
export API_KEY=sk-test                           # 自定义您的 API 密钥

bash start_server.sh
```

### 2. 客户端连接 (Windows)
*适用场景：普通办公/家用电脑。*

**启动步骤：**
1. 下载发行版并解压。
2. 进入 `lora_tts\app` 目录。
3. 双击运行 `run_app.bat`（首次运行会自动配置环境）。

**配置连接：**
在客户端界面中填写：
- **API URL**: `http://<服务器公网或局域网IP>:8000/v1/tts`
- **API Key**: `sk-test` (与服务端设置一致)

---

## 模式二：本地一体化部署 (Windows Only)

*适用场景：拥有一台带 NVIDIA 显卡的高性能 Windows 电脑，希望单机运行。*

### 1. 启动服务端 (Windows)
打开 PowerShell 或 CMD，进入 `lora_tts\server` 目录：

```powershell
pip install -r requirements-server.txt

# 设置环境变量 (PowerShell 示例)
$env:BASE_MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-Base"
$env:ADAPTER_PATH="D:\path\to\lora_tts\model"
$env:REF_AUDIO_DEFAULT="D:\path\to\lora_tts\data\sample.wav"
$env:API_KEY="sk-local"

# 启动服务
python main.py
```
*(注：请保持该窗口开启，不要关闭)*

### 2. 启动客户端 (Windows)
双击 `lora_tts\app\run_app.bat`。

### 3. 配置连接
- **API URL**: `http://127.0.0.1:8000/v1/tts`
- **API Key**: `sk-local`

---

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