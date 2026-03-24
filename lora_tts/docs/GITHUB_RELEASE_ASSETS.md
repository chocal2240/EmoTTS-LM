# GitHub Release 建议上传资产

建议发布以下文件：

1) app_package_*.zip
2) model_package_*.zip
3) server_package_*.zip
4) checksums_sha256.txt

可选：

- dataset 发布压缩包（若你打算同时发布数据）

## 推荐 Release 文案（可直接复制）

### 内容

- Windows GUI 应用（情感语音合成控制台）
- LoRA 模型适配器（final_1500）
- Linux API 服务端脚本
- 安装与连接文档

### 快速开始

1. 在 Linux GPU 服务器部署 server + model 并启动 API
2. 在 Windows 启动 app
3. 在 GUI 设置 API URL / API Key，开始合成

### 注意

- 应用依赖 API 服务；服务关闭时 GUI 无法合成
- 模型包为 LoRA 适配器，不含基座模型
