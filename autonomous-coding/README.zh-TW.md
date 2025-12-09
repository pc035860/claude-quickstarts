**Language / 語言:** [English](README.md) | [繁體中文](README.zh-TW.md)

# Autonomous Coding Agent Demo

一個展示如何使用 Claude Agent SDK 進行長時間自主編碼的最小化框架。此示範實作了一個雙代理模式（初始化代理 + 編碼代理），可以在多個 session 中建立完整的應用程式。

## 前置需求

**必要：** 安裝最新版本的 Claude Code 和 Claude Agent SDK：

### 安裝 Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### 安裝 Python 依賴

此專案使用 [uv](https://github.com/astral-sh/uv) 進行快速的 Python 套件管理。您可以使用 `uv` 或傳統的 `pip`：

**選項 1 - 使用 uv（推薦）：**

```bash
# 如果還沒安裝 uv，先安裝
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝 Python 依賴
uv pip install -r requirements.txt
```

**選項 2 - 使用 pip：**

```bash
pip install -r requirements.txt
```

### 驗證安裝

```bash
claude --version  # 應該是最新版本

# 如果使用 uv：
uv pip show claude-agent-sdk  # 檢查 SDK 是否已安裝

# 如果使用 pip：
pip show claude-agent-sdk  # 檢查 SDK 是否已安裝
```

**認證：** 設定以下其中一項：

選項 1 - 從 [console.anthropic.com](https://console.anthropic.com/) 取得的標準 API key：
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

選項 2 - Claude Code OAuth token（來自 `claude setup-token`）：
```bash
export CLAUDE_CODE_OAUTH_TOKEN='your-claude-code-auth-token'
```

## 快速開始

**使用 uv（推薦）：**

```bash
uv run python autonomous_agent_demo.py --project-dir ./my_project
```

**使用傳統 Python：**

```bash
python autonomous_agent_demo.py --project-dir ./my_project
```

測試時限制迭代次數：
```bash
# 使用 uv：
uv run python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3

# 使用傳統 Python：
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

使用自訂 app 規格檔案開始專案：
```bash
# 使用 uv：
uv run python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_app_spec.txt

# 使用傳統 Python：
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_app_spec.txt
```

自訂要產生的功能數量（用於更快的示範）：
```bash
# 使用 uv：
uv run python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50

# 使用傳統 Python：
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50
```

## 重要時間預期

> **警告：此示範需要很長時間才能執行！**

- **第一個 session（初始化）：** Agent 會產生包含測試案例的 `feature_list.json`（預設：200 個）。這需要幾分鐘時間，可能會看起來像是當機 - 這是正常的。Agent 正在寫出所有功能。

- **後續 sessions：** 每次編碼迭代可能需要 **5-15 分鐘**，取決於複雜度。

- **完整應用程式：** 建立所有功能通常需要 **數小時**的總執行時間，跨越多個 sessions。

**提示：** 預設的 200 個功能參數是為了全面覆蓋而設計的。如果您想要更快的示範，可以使用 `--feature-count` 命令列選項（例如，`--feature-count 50` 以獲得更快的示範）。

## 運作方式

### 雙代理模式

1. **初始化代理（Session 1）：** 
   - 讀取 `app_spec.txt`（從專案目錄或透過 `--app-spec` 指定）
   - 建立包含測試案例的 `feature_list.json`（預設：200 個，可透過 `--feature-count` 自訂）
   - 設定專案結構
   - 初始化 git
   - 將 app spec 檔案複製到專案目錄以供未來參考

2. **編碼代理（Session 2+）：** 
   - 從專案目錄讀取 `app_spec.txt` 以了解整體規格
   - 從上次 session 停止的地方繼續
   - 逐一實作功能
   - 在 `feature_list.json` 中標記為通過

### Session 管理

- 每個 session 使用全新的 context window 執行
- 進度透過 `feature_list.json` 和 git commits 持久化
- Agent 會在 sessions 之間自動繼續（3 秒延遲）
- 按 `Ctrl+C` 暫停；執行相同命令以恢復

## 安全模型

此示範使用深度防禦安全方法（參見 `security.py` 和 `client.py`）：

1. **OS 層級沙箱：** Bash 命令在隔離環境中執行
2. **檔案系統限制：** 檔案操作僅限於專案目錄
3. **Bash 白名單：** 僅允許特定命令：
   - 檔案檢查：`ls`, `cat`, `head`, `tail`, `wc`, `grep`, `find`, `echo`, `jq`
   - 檔案操作：`cp`, `mv`, `mkdir`, `chmod`, `tee`, `xargs`
   - 目錄：`pwd`, `cd`
   - Node.js：`npm`, `node`, `npx`, `pnpm`
   - Supabase & Deno：`supabase`, `deno`
   - 網路工具：`curl`
   - 版本控制：`git`
   - 程序管理：`ps`, `lsof`, `sleep`, `pkill`, `kill`（僅限開發程序）
   - 腳本執行：`init.sh`
   - Shell 內建命令：`set`

不在白名單中的命令會被安全 hook 阻擋。

## 專案結構

```
autonomous-coding/
├── autonomous_agent_demo.py  # 主要進入點
├── agent.py                  # Agent session 邏輯
├── client.py                 # Claude SDK client 配置
├── security.py               # Bash 命令白名單和驗證
├── progress.py               # 進度追蹤工具
├── prompts.py                # Prompt 載入工具
├── prompts/
│   ├── app_spec.txt          # 應用程式規格
│   ├── initializer_prompt.md # 第一個 session prompt
│   └── coding_prompt.md      # 後續 session prompt
└── requirements.txt          # Python 依賴
```

## 產生的專案結構

執行後，您的專案目錄將包含：

```
my_project/
├── feature_list.json         # 測試案例（單一真實來源）
├── app_spec.txt              # 複製的規格
├── init.sh                   # 環境設定腳本
├── claude-progress.txt       # Session 進度筆記
├── .claude_settings.json     # 安全設定
└── [application files]       # 產生的應用程式程式碼
```

## 執行產生的應用程式

Agent 完成（或暫停）後，您可以執行產生的應用程式：

```bash
cd generations/my_project

# 執行 Agent 建立的設定腳本
./init.sh

# 或手動執行（典型的 Node.js 應用程式）：
npm install
npm run dev
```

應用程式通常會在 `http://localhost:3000` 或類似位置可用（檢查 agent 的輸出或 `init.sh` 以取得確切的 URL）。

## 命令列選項

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `--project-dir` | 專案目錄 | `./autonomous_demo_project` |
| `--max-iterations` | 最大 agent 迭代次數 | 無限制 |
| `--model` | 使用的 Claude 模型 | `claude-sonnet-4-5-20250929` |
| `--app-spec` | App spec 檔案路徑（僅在初始化時使用） | `prompts/app_spec.txt` |
| `--feature-count` | 在 feature_list.json 中產生的功能數量 | `200` |

## 自訂化

### 變更應用程式

**選項 1：編輯預設 spec 檔案**
編輯 `prompts/app_spec.txt` 以指定要建立的不同應用程式。除非您指定不同的檔案，否則這將用於所有新專案。

**選項 2：每個專案使用自訂 spec 檔案**
使用 `--app-spec` 參數在初始化新專案時指定不同的 app 規格檔案：

```bash
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_custom_spec.txt
```

這在以下情況特別有用：
- 處理具有不同規格的多個專案
- 將自主編碼整合到現有專案中
- 測試不同的應用程式設計

**注意：** 一旦專案初始化，app spec 檔案會被複製到專案目錄（`app_spec.txt`）。後續執行會自動使用專案自己的 `app_spec.txt` 檔案，因此您不需要再次指定 `--app-spec`。

### App Spec 檔案管理

- **初始化：** App spec 檔案在第一個 session 期間被複製到專案目錄
- **後續 sessions：** Agent 自動從專案目錄讀取 `app_spec.txt`
- **保護：** 如果專案已經有 `app_spec.txt`，除非您明確指定不同的 `--app-spec` 檔案，否則不會被覆蓋

### 調整功能數量

您可以使用 `--feature-count` 命令列選項來自訂要產生的功能數量：

```bash
# 產生 50 個功能以獲得更快的示範
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50

# 產生 100 個功能以獲得中等大小的示範
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 100
```

或者，您可以編輯 `prompts/initializer_prompt.md` 並變更 XML tag `<feature_count>200</feature_count>` 中的預設值。

### 修改允許的命令

編輯 `security.py` 以從 `ALLOWED_COMMANDS` 新增或移除命令。

## 與現有專案協作

可以使用兩個有用的命令將自主編碼整合到現有專案中。這些命令可幫助您接入新專案並逐步新增功能。

### 接入新專案

使用 `/onboard-project` 命令來分析現有專案並產生 `app_spec.txt` 檔案：

1. **準備您的專案**
   - 確保您的專案可存取（可以是 `generations/` 目錄中的 symbolic link）
   - 準備好任何 PRD、spec 或文件檔案

2. **執行命令**
   ```
   /onboard-project
   ```

3. **在提示時提供資訊**
   - 專案路徑（絕對或相對路徑）
   - `app_spec.txt` 的輸出位置（預設為專案根目錄）
   - API keys、secrets 或 credentials 設定說明（如果需要）

4. **檢視產生的 spec**
   - 命令會分析您的專案結構、程式碼庫和文件
   - 它會產生符合 `prompts/app_spec.example.txt` 格式的完整 `app_spec.txt`
   - 如果有任何資訊不確定，命令會詢問澄清

**命令會做什麼：**
- 並行探索專案結構、程式碼庫和文件
- 識別技術棧（前端、後端、資料庫、整合）
- 從 PRD/spec 檔案和程式碼分析中提取功能
- 收集認證和配置需求
- 產生包含所有必要章節的完整 `app_spec.txt`

**接入後：**
- `app_spec.txt` 檔案已準備好用於自主編碼初始化
- 您可以開始自主 agent：`python autonomous_agent_demo.py --project-dir ./your_project`

### 為現有專案新增功能

使用 `/add-feature` 命令為已經有 `app_spec.txt` 的專案新增新功能：

1. **準備功能資訊**
   - 清楚描述新功能
   - 如果有的話，提供任何 PRD 或 spec 文件

2. **執行命令**
   ```
   /add-feature
   ```

3. **在提示時提供資訊**
   - 專案路徑（必須已經有 `app_spec.txt`）
   - 新功能描述或需求
   - PRD/spec 檔案路徑（選填）

4. **檢視更新的功能清單**
   - 命令會分析新功能需求
   - 它會探索現有程式碼庫以了解整合點
   - 它會將功能拆解成適當大小的 `feature_list.json` 項目
   - 每個項目的大小設定為在單一 session 中至少完成 1 個

**命令會做什麼：**
- 讀取現有的 `app_spec.txt` 和 `feature_list.json`
- 探索程式碼庫以了解現有模式和架構
- 分析新功能需求和整合點
- 將複雜功能拆解成可管理的項目：
  - 後端 API 開發（1-2 個項目）
  - 前端 UI 組件（1-2 個項目）
  - 整合測試（1 個項目）
  - 樣式和 UX 優化（1 個項目）
- 更新 `feature_list.json` 而不修改現有項目

**新增功能後：**
- 新功能項目會以 `"passes": false` 加入到 `feature_list.json`
- 您可以繼續自主編碼：`python autonomous_agent_demo.py --project-dir ./your_project`
- Agent 會按優先順序處理新功能項目

**最佳實踐：**
- 保持功能描述清楚且具體
- 提供 PRD/spec 文件以獲得更好的分析
- 檢視產生的功能項目以確保它們的大小適當
- 如果有任何不確定之處，命令會詢問澄清

## 疑難排解

**"第一次執行時看起來像是當機"**
這是正常的。初始化代理正在產生詳細的測試案例（預設：200 個），這需要大量時間。觀察 `[Tool: ...]` 輸出以確認 agent 正在運作。要減少產生時間，可以使用 `--feature-count` 並指定較小的數字（例如，`--feature-count 50`）。

**"找不到 App spec 檔案"**
如果您使用自訂路徑指定 `--app-spec`，請確保檔案存在。路徑可以是相對於當前目錄或絕對路徑。範例：
```bash
# 相對路徑
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_spec.txt

# 絕對路徑
python autonomous_agent_demo.py --project-dir ./my_project --app-spec /path/to/my_spec.txt
```

**"命令被安全 hook 阻擋"**
Agent 嘗試執行不在白名單中的命令。這是安全系統按預期運作。如果需要，可以將命令新增到 `security.py` 中的 `ALLOWED_COMMANDS`。

**"未設定 Claude 認證"**
在您的 shell 環境中設定以下其中一項：
- 標準 API key：`export ANTHROPIC_API_KEY='your-api-key-here'`
- Claude Code OAuth token：`export CLAUDE_CODE_OAUTH_TOKEN='your-claude-code-auth-token'`

## 授權

Anthropic 內部使用。

