---
description: 接入新專案並產生 app_spec.txt 檔案
---

這個 command 會分析指定路徑的專案，理解其架構、技術棧和功能，然後產生符合 autonomous coding 格式的 `app_spec.txt` 檔案。

<steps>
1. **詢問使用者輸入**
   - 要接入的專案路徑（可以是絕對路徑或相對路徑）
   - 要產出 app_spec.txt 的位置（預設為專案根目錄，或可指定其他位置）
   - 如果專案需要 API keys、secrets、credentials 等，詢問使用者如何取得或應用這些資訊

2. **廣泛探索專案結構**
   - 使用 @agent-Explore (haiku, run in foreground) 進行多個並行的探索任務：
     - 探索專案根目錄結構（package.json, requirements.txt, Cargo.toml 等）
     - 探索 README.md、docs/、specs/、PRD 等文件
     - 探索主要程式碼目錄結構
     - 探索配置檔案（.env.example, config/, settings/ 等）
     - 探索測試檔案結構
   - **IMPORTANT: Run subagents in parallel** - 同時啟動多個探索任務以高效收集資訊

3. **分析技術棧**
   - 識別前端框架（React, Vue, Next.js 等）
   - 識別後端技術（Node.js, Python, Rust 等）
   - 識別資料庫和儲存方案
   - 識別第三方服務整合（API providers, auth services 等）
   - 識別開發工具和建置流程

4. **理解專案功能**
   - 從 PRD、spec 文件提取功能需求
   - 從程式碼結構推斷已實作功能
   - 識別核心業務邏輯
   - 識別待完成或需要改進的功能
   - 分析 API 端點和資料模型

5. **收集認證資訊**
   - 檢查 .env.example、README.md、docs/ 中的認證說明
   - 識別需要的 API keys、secrets、credentials
   - 詢問使用者：
     - 如何取得這些認證資訊
     - 是否需要在開發/測試環境中設定
     - 是否有測試用的認證資訊可以使用

6. **產生 app_spec.txt**
   - 參考 `prompts/app_spec.example.txt` 的完整格式和結構
   - **重要：如果遇到不確定的資訊，必須主動詢問使用者**
     - 技術棧版本號不確定時（例如：Next.js 版本、React 版本）
     - 功能實作狀態不明確時（已實作 vs 待實作）
     - API 端點或資料庫結構無法從程式碼推斷時
     - 設計系統細節無法從現有程式碼判斷時
     - 環境設定或依賴關係不清楚時
     - 任何會影響後續開發的重要資訊缺失時
   - 必須包含以下所有章節（根據專案類型調整）：
     - `<project_name>` - 專案名稱
     - `<overview>` - 專案概述和核心場景，說明已實作和待完成的功能
     - `<technology_stack>` - 完整技術棧：
       - `<api_key>` - API key 說明（如何取得、使用方式、測試設定）
       - `<frontend>` - 前端技術（framework, styling, state_management, routing 等）
       - `<backend>` - 後端技術（runtime, database, api_integration, streaming 等）
       - `<communication>` - 通訊方式（RESTful, SSE, WebSocket 等）
     - `<prerequisites>` - 前置需求：
       - `<environment_setup>` - 環境設定說明（依賴安裝、配置檔案、環境變數等）
     - `<core_features>` - 核心功能，使用子區塊組織（如 `<chat_interface>`, `<artifacts>` 等）：
       - 每個功能區塊包含該功能的詳細功能點列表
       - 區分已實作和待實作的功能
     - `<database_schema>` - 資料庫結構（如果適用）：
       - `<tables>` - 所有資料表的結構說明
     - `<api_endpoints_summary>` - API 端點摘要（如果適用）：
       - 按功能分類組織（authentication, conversations, messages 等）
     - `<ui_layout>` - UI 佈局結構（如果適用）：
       - `<main_structure>` - 主要佈局結構
       - `<sidebar_left>`, `<main_chat_area>`, `<artifacts_panel>` 等區塊
       - `<modals_overlays>` - 模態框和覆蓋層
     - `<design_system>` - 設計系統（如果適用）：
       - `<color_palette>` - 顏色調色盤
       - `<typography>` - 字體系統
       - `<components>` - 組件樣式（buttons, inputs, cards 等）
       - `<animations>` - 動畫和過渡效果
     - `<key_interactions>` - 關鍵互動流程（如果適用）：
       - 描述主要使用者流程（message_flow, artifact_flow 等）
     - `<implementation_steps>` - 實作步驟（可選）：
       - 如果專案有明確的實作階段，可以列出步驟
     - `<success_criteria>` - 成功標準：
       - `<functionality>` - 功能性要求
       - `<user_experience>` - 使用者體驗要求
       - `<technical_quality>` - 技術品質要求
       - `<design_polish>` - 設計完善度要求（如果適用）

7. **驗證產出**
   - 檢查 app_spec.txt 的完整性和準確性
   - 確認所有重要功能都有涵蓋
   - 確認技術棧資訊正確
   - 確認認證資訊說明清楚

8. **儲存檔案**
   - 將 app_spec.txt 寫入指定位置
   - 如果位置在專案目錄外，同時詢問是否要複製一份到專案目錄
</steps>

<output>
產出的 app_spec.txt 應該遵循 `prompts/app_spec.example.txt` 的完整 XML 格式，包含所有相關章節：

```xml
<project_specification>
  <project_name>[專案名稱]</project_name>
  
  <overview>
    [專案概述，包含核心場景和主要功能]
    [說明已實作的功能和待完成的功能]
  </overview>
  
  <technology_stack>
    <api_key>
      [API key 說明，如何取得、使用方式、測試設定]
    </api_key>
    <frontend>
      <framework>[前端框架]</framework>
      <styling>[樣式方案]</styling>
      <state_management>[狀態管理]</state_management>
      <!-- 其他前端技術：routing, markdown, code_highlighting, port 等 -->
    </frontend>
    <backend>
      <runtime>[後端運行環境]</runtime>
      <database>[資料庫]</database>
      <api_integration>[API 整合]</api_integration>
      <streaming>[串流方案]</streaming>
      <!-- 其他後端技術 -->
    </backend>
    <communication>
      <api>[API 類型]</api>
      <streaming>[串流方式]</streaming>
      <!-- 其他通訊方式 -->
    </communication>
  </technology_stack>
  
  <prerequisites>
    <environment_setup>
      - [環境設定說明]
      - [依賴安裝方式]
      - [配置檔案位置]
    </environment_setup>
  </prerequisites>
  
  <core_features>
    <feature_category_1>
      - [功能點 1]
      - [功能點 2]
      <!-- 使用子區塊組織功能 -->
    </feature_category_1>
    <feature_category_2>
      - [功能點 1]
      - [功能點 2]
    </feature_category_2>
  </core_features>
  
  <database_schema>
    <tables>
      <table_name>
        - [欄位說明]
      </table_name>
    </tables>
  </database_schema>
  
  <api_endpoints_summary>
    <category>
      - [HTTP 方法] [端點路徑]
    </category>
  </api_endpoints_summary>
  
  <ui_layout>
    <main_structure>
      - [主要佈局描述]
    </main_structure>
    <!-- 其他 UI 區塊 -->
  </ui_layout>
  
  <design_system>
    <color_palette>
      - [顏色定義]
    </color_palette>
    <typography>
      - [字體設定]
    </typography>
    <components>
      <component_name>
        - [組件樣式說明]
      </component_name>
    </components>
    <animations>
      - [動畫效果]
    </animations>
  </design_system>
  
  <key_interactions>
    <interaction_flow>
      1. [步驟 1]
      2. [步驟 2]
    </interaction_flow>
  </key_interactions>
  
  <implementation_steps>
    <step number="1">
      <title>[步驟標題]</title>
      <tasks>
        - [任務 1]
        - [任務 2]
      </tasks>
    </step>
  </implementation_steps>
  
  <success_criteria>
    <functionality>
      - [功能性要求]
    </functionality>
    <user_experience>
      - [UX 要求]
    </user_experience>
    <technical_quality>
      - [技術品質要求]
    </technical_quality>
    <design_polish>
      - [設計完善度要求]
    </design_polish>
  </success_criteria>
</project_specification>
```
</output>

<example>
假設接入一個 Next.js + Supabase 的專案，參考 `prompts/app_spec.example.txt` 的完整結構：

```xml
<project_specification>
  <project_name>Task Management App</project_name>
  
  <overview>
    一個任務管理應用程式，支援使用者建立、編輯、刪除任務。
    已實作：使用者認證、任務 CRUD 基本功能
    待完成：任務分類、優先級設定、協作功能
  </overview>
  
  <technology_stack>
    <api_key>
      Supabase API keys: NEXT_PUBLIC_SUPABASE_URL 和 NEXT_PUBLIC_SUPABASE_ANON_KEY
      從 Supabase 專案設定頁面取得，或詢問專案維護者
      在 .env.local 中設定，Next.js 會自動讀取
      測試環境使用開發環境的 Supabase 專案 URL 和 anon key
    </api_key>
    <frontend>
      <framework>Next.js 14 App Router</framework>
      <styling>Tailwind CSS</styling>
      <state_management>React hooks + SWR</state_management>
      <routing>Next.js App Router</routing>
    </frontend>
    <backend>
      <runtime>Supabase Edge Functions (Deno)</runtime>
      <database>PostgreSQL via Supabase</database>
      <api_integration>Supabase Client SDK</api_integration>
      <auth>Supabase Auth</auth>
    </backend>
    <communication>
      <api>RESTful endpoints via Supabase</api>
      <realtime>Supabase Realtime subscriptions</realtime>
    </communication>
  </technology_stack>
  
  <prerequisites>
    <environment_setup>
      - 安裝 Node.js 18+
      - 執行 npm install 安裝依賴
      - 複製 .env.example 為 .env.local
      - 設定 Supabase 環境變數
      - 執行 npm run dev 啟動開發伺服器
    </environment_setup>
  </prerequisites>
  
  <core_features>
    <task_management>
      - 建立新任務
      - 編輯任務內容
      - 刪除任務
      - 標記任務為完成
      - 任務列表顯示
    </task_management>
    <user_authentication>
      - 使用者註冊
      - 使用者登入
      - 使用者登出
      - 個人資料管理
    </user_authentication>
    <!-- 其他功能區塊 -->
  </core_features>
  
  <database_schema>
    <tables>
      <tasks>
        - id, user_id, title, description, completed, created_at, updated_at
      </tasks>
      <users>
        - id, email, name, created_at
      </users>
    </tables>
  </database_schema>
  
  <api_endpoints_summary>
    <tasks>
      - GET /api/tasks
      - POST /api/tasks
      - PUT /api/tasks/:id
      - DELETE /api/tasks/:id
    </tasks>
  </api_endpoints_summary>
  
  <success_criteria>
    <functionality>
      - 所有 CRUD 操作正常運作
      - 使用者認證流程完整
    </functionality>
    <user_experience>
      - 介面直覺易用
      - 響應速度快
    </user_experience>
    <technical_quality>
      - 程式碼結構清晰
      - 錯誤處理完善
    </technical_quality>
  </success_criteria>
</project_specification>
```
</example>

<constraints>
- 必須徹底理解專案結構，不能遺漏重要技術或功能
- 所有認證資訊必須明確說明如何取得，不能直接包含實際的 keys 或 secrets
- 產出的 app_spec.txt 必須嚴格遵循 `prompts/app_spec.example.txt` 的格式和結構
- 必須包含所有相關章節（根據專案類型，某些章節可能不適用）
- `<core_features>` 必須使用子區塊組織，每個功能類別一個區塊
- 如果專案中已有 app_spec.txt，詢問是否要覆蓋或另存新檔
- 探索時必須使用並行的 subagents 以提高效率
- 對於 UI 專案，必須包含 `<ui_layout>` 和 `<design_system>` 章節
- 對於有明確實作階段的專案，可以包含 `<implementation_steps>` 章節
</constraints>

