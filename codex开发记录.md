# Codex 开发记录：Infinity Agents 架构概览

## 项目目录速览
- `app/app.py`：Flask + SocketIO 服务入口，负责 HTTP 路由、长连接事件以及可执行文件打包接口。
- `app/agents.py`：使用 `agno` 定义的两类 AI Agent（`paperai_agent`、`chater_agent`），封装了 DeepSeek 模型及 PubMed/Arxiv 工具链。
- `app/templates/main.html`：前端单页界面骨架，注入静态资源并初始化 Socket.IO 客户端。
- `app/static/js/script.js`：浏览器端逻辑，管理消息流、Markdown 渲染、生成中断控制等。
- `app/traitRecognizePackager.py`：原始的图像性状识别批量分类脚本，支持本地运行并可被后端改写用于打包。
- `tests/`：PyTest 测试集合（当前未深入查看）。

## 后端通信流程
1. `/chat` GET 路由渲染 `main.html`，会话信息保存在 Flask session 中。
2. 前端通过 Socket.IO 与后端建立连接；当用户发送消息时触发 `send_message` 事件。
3. `app/app.py:183` 使用 `DialogueManager` 根据请求的 Agent 类型（`paperai` 或 `chater`）启动后台线程。
4. `DialogueManager.process_user_input` 调用 agno Agent 的 `run(..., stream=True)`，逐块推送响应；服务端监听 `stop_generation` 事件，通过共享字典 `active_tasks` 切断流式输出。
5. 完整回复通过 `ai_message_end` 收尾事件通知前端；若出现异常，会返回错误片段给前端并在日志中输出堆栈。

## agent 管理与外部依赖
- `app/agents.py` 基于 `agno.agent.Agent` 封装 DeepSeek 模型，`paperai_agent` 还引入 `PubmedTools`、`ArxivTools` 实现自动检索与归纳。
- 运行前需在环境中提供 `DEEPSEEK_API_KEY`，否则会回退至占位的默认值。
- Agent 定义均启用 Markdown 输出，前端在 `script.js` 中使用 `marked` 将内容转为 HTML。

## 自动打包服务
- `POST /generate_exe` 接口负责将 trait 示例图与用户上传的对比图列表封装进独立的打包脚本。
- 核心步骤：
  1. 校验 `trait_image_base64`、拓展名，拼接为 data URL。
  2. 在临时目录复制 `_write_packager_script` 生成的无交互版 `traitRecognizePackager.py`，内嵌 trait 图 data URL。
  3. 以当前 Python 解释器调用 `PyInstaller --onefile` 打包，并通过 `send_file` 返回生成的可执行文件。
  4. 利用 `@after_this_request` 清理临时目录；若 PyInstaller 缺失或打包失败，会返回详细错误信息。
- `GET /download/<program_name>` 提供预置 EXE 占位符下载（目前为占位的批处理脚本）。

## traitRecognizePackager.py 逻辑概览
- 交互式脚本：提示用户输入 `DASHSCOPE_API_KEY` 以及图像目录，默认读取环境变量。
- 主要流程：
  1. 遍历目录中支持的图像类型，将每张图编码为 base64 data URL。
  2. 与预设的性状图 `trait_image_url` 组合，调用 DashScope 兼容接口下的 OpenAI 客户端（模型 `qwen3-vl-plus`）进行分类。
  3. 将返回的类别与理由写入 `image_classification_results.csv`，同时在终端打印结果。
- Flask 服务端在生成 EXE 时会动态覆写脚本中的 `trait_image_url`，并去除交互式输入以支持批量打包。

## 前端交互要点
- `script.js` 监听服务端推送事件，逐块拼接 Markdown 文本并渲染；提供“停止生成”按钮，可通过 Socket.IO 触发后端的停止标记。
- 界面使用 `templates/main.html` + `static/css/styles.css` 构成单页聊天体验，初始展示欢迎提示与代理说明。

## 部署与运行
- 本地运行：`python app/app.py`，默认监听 `127.0.0.1:8080`。
- Docker：`Dockerfile` 支持构建镜像并通过环境变量注入 `DEEPSEEK_API_KEY`。
- 打包功能依赖 `PyInstaller` 与 `dashscope` 兼容接口，需要在运行环境中提前安装并设置 `DASHSCOPE_API_KEY`（或在交互脚本中输入）。

