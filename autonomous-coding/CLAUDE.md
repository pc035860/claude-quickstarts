# CLAUDE.md

## Project Overview

**Autonomous Coding Agent Demo** - 使用 Claude Agent SDK 實現長時間運行的自主編碼代理。

- **技術棧**: Python + claude-agent-sdk (>=0.1.13)
- **架構模式**: 雙代理模式 (Initializer Agent + Coding Agent)
- **用途**: 透過多個會話自動建構完整應用程式

## Common Commands

### 運行代理

```bash
# 使用 uv（推薦）
uv run python autonomous_agent_demo.py --project-dir ./my_project

# 使用傳統 Python
python autonomous_agent_demo.py --project-dir ./my_project
```

### 常用選項

```bash
# 限制迭代次數（測試用）
--max-iterations 3

# 自定義 app spec 文件
--app-spec ./specs/my_app_spec.txt

# 調整功能數量（預設 200，可減少以加速）
--feature-count 50

# 指定模型
--model claude-sonnet-4-5-20250929
```

### 測試

```bash
pytest                           # 運行所有測試
pytest test_security.py -v       # 運行安全模組測試
```

### 驗證安裝

```bash
claude --version                  # 確認 Claude Code CLI
uv pip show claude-agent-sdk      # 確認 SDK 安裝
```

## Architecture & Key Components

```
autonomous-coding/
├── autonomous_agent_demo.py  # 主入口點，解析命令列參數
├── agent.py                  # Agent 會話邏輯，run_agent_session()
├── client.py                 # Claude SDK 客戶端配置
├── security.py               # Bash 命令白名單驗證 (ALLOWED_COMMANDS)
├── progress.py               # 進度追蹤工具
├── prompts.py                # Prompt 載入工具
└── prompts/
    ├── initializer_prompt.md # 第一次會話 prompt
    └── coding_prompt.md      # 後續會話 prompt
```

### 關鍵流程

1. **Initializer Agent (Session 1)**:
   - 讀取 `app_spec.txt`
   - 生成 `feature_list.json`（預設 200 個功能）
   - 初始化 git

2. **Coding Agent (Sessions 2+)**:
   - 從上次中斷處繼續
   - 逐一實現功能並標記完成

### UI 驗證子代理

定義於 `client.py:142-171`，用於自動化 UI 測試：

- **名稱**: `ui-verify`
- **模型**: haiku（快速回應）
- **用途**: 透過瀏覽器自動化驗證 UI 功能
- **特性**: 只驗證和報告問題，不修改程式碼

### Chrome DevTools MCP 整合

定義於 `client.py:17-42`，提供瀏覽器自動化能力：

- **MCP 服務器**: `chrome-devtools-mcp@latest`
- **模式**: `--isolated --headless`（無頭模式）
- **工具數量**: 22 個瀏覽器操作工具
- **功能**: 頁面導航、元素點擊、表單填寫、截圖、Console 監控等

## Development Notes

### 認證設定

設定其中一個環境變數：
```bash
export ANTHROPIC_API_KEY='your-api-key'
# 或
export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token'
```

### 安全機制

- 命令白名單定義於 `security.py:ALLOWED_COMMANDS`
- 檔案操作限制在專案目錄內
- 新增命令需修改 `security.py`

### 專案命令

- `/onboard-project` - 為現有專案生成 `app_spec.txt`
- `/add-feature` - 為已有專案新增功能到 `feature_list.json`

### 注意事項

- 首次運行會生成功能列表，可能需要數分鐘
- 每次迭代可能需要 5-15 分鐘
- 使用 `Ctrl+C` 暫停，相同命令恢復
