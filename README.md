# EmoTTS-LM

本项目通过 GitHub Release 分发可部署资产，包含客户端应用、服务端 API、LoRA 适配器和部署文档。

## 仓库结构

```text
EmoTTS-LM/
|- lora_tts/
|  |- README_RELEASE.md
|  |- app/
|  |  |- main.py
|  |  |- requirements-app.txt
|  |  |- run_app.bat
|  |  `- tts_config.example.json
|  |- server/
|  |  |- api_server.py
|  |  |- requirements-server.txt
|  |  |- start_server.sh
|  |  `- tts_text_enhancer.py
|  |- model/
|  |  |- adapter_config.json
|  |  |- adapter_model.safetensors
|  |  `- README.md
|  `- docs/
|     |- GITHUB_RELEASE_ASSETS.md
|     `- INSTALL_AND_CONNECT.md
|- .env.example
|- .gitignore
|- LICENSE
|- requirements.txt
`- README.md
```

## 发布版部署（推荐）

### 1. 下载发行版

从 GitHub Release 下载并解压发布包（建议保留目录结构不变）。

### 2. 环境要求

- Python 3.10+
- 服务端建议 Linux + CUDA GPU
- 客户端建议 Windows（可直接使用 `run_app.bat`）

### 3. 启动服务端（Linux）

```bash
cd lora_tts/server
pip install -r requirements-server.txt

# 按实际路径配置
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

### 4. 启动客户端（Windows）

```bat
cd lora_tts\app
run_app.bat
```

首次运行会自动创建虚拟环境并安装 `requirements-app.txt`。

### 5. 客户端连接服务端

在 GUI 模型设置中填写：

- API URL：`http://<服务器IP>:8000/v1/tts`
- API Key：与服务端 `API_KEY` 一致
- Adapter Path：可选；默认由服务端 `ADAPTER_PATH` 控制

## 依赖说明（仓库公开）

- 根目录 `requirements.txt`：聚合依赖，适合快速安装完整运行环境。
- `lora_tts/app/requirements-app.txt`：仅客户端 GUI 依赖。
- `lora_tts/server/requirements-server.txt`：仅服务端 API 依赖。

## 快速开始

```bash
git clone https://github.com/chocal2240/EmoTTS-LM.git
cd EmoTTS-LM
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

如需分别安装：

```bash
pip install -r lora_tts/app/requirements-app.txt
pip install -r lora_tts/server/requirements-server.txt
```

## 说明

- 模型目录提供 LoRA 适配器，不包含完整基座模型。
- `REF_AUDIO_DEFAULT` 必须指向一个可访问的参考音频文件（wav）。
- 仓库中的 `requirements.txt` 建议公开维护，不应在 `.gitignore` 中忽略。

## 许可证

本项目使用 [MIT License](LICENSE)。

## 联系方式

- Email: fanqt2024@lzu.edu.cn
- GitHub: https://github.com/chocal2240/EmoTTS-LM