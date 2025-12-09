---
description: 為指定專案新增功能並更新 feature_list.json
---

這個 command 會分析新功能需求，探索現有程式碼庫，然後將新功能拆解成適當大小的 feature_list.json 項目。每個項目的大小應該剛好可以在單一 session 中完成至少 1 個。

<steps>
1. **詢問使用者輸入**
   - 專案路徑（通常專案中已經有 app_spec.txt 檔案）
   - 新功能的描述或需求
   - 如果有相關的 PRD、spec 文件，請使用者提供路徑或內容

2. **讀取專案基礎資訊**
   - 讀取專案目錄中的 `app_spec.txt` 了解專案整體規格
   - 讀取現有的 `feature_list.json` 了解已完成和進行中的功能
   - 檢查 `claude-progress.txt` 了解最近的開發進度

3. **廣泛探索現有程式碼庫**
   - 使用 @agent-Explore (haiku, run in foreground) 進行多個並行的探索任務：
     - 探索與新功能相關的現有程式碼模組
     - 探索相關的 API 端點和資料模型
     - 探索相關的 UI 組件和頁面結構
     - 探索測試檔案以了解測試模式
     - 探索相關的配置和依賴關係
   - **IMPORTANT: Run subagents in parallel** - 同時啟動多個探索任務以高效收集資訊

4. **分析新功能需求**
   - 結合使用者提供的 PRD/spec 和程式碼探索結果
   - 理解新功能與現有功能的關係
   - 識別需要新增的模組、API、UI 組件
   - 識別需要修改的現有程式碼
   - 識別可能的依賴關係和整合點
   - **重要：如果遇到不確定的資訊，必須主動詢問使用者**
     - 新功能的具體需求或邊界條件不清楚時
     - 與現有功能的整合方式不明確時
     - 技術實作方式有多種選擇時
     - UI/UX 設計細節未明確時
     - 資料模型或 API 設計需要確認時
     - 測試範圍或驗證標準不清楚時

5. **拆解功能為適當大小的項目**
   - 參考 `prompts/initializer_prompt.md` 中 feature_list.json 的格式要求
   - **重要：如果拆解過程中遇到不確定的部分，必須主動詢問使用者**
     - 功能拆解的粒度是否適當（太大或太小）
     - 實作優先順序是否需要調整
     - 某些功能點是否應該合併或分開
     - 測試步驟的詳細程度是否足夠
     - 是否有遺漏的重要功能點
   - 將新功能拆解成多個 feature_list 項目，每個項目應該：
     - 可以在單一 session 中完成至少 1 個
     - 有明確的測試步驟（2-10+ steps）
     - 包含 functional 或 style 類別
     - 優先級排序（基礎功能優先）
   - 對於複雜功能，拆解成更多項目：
     - 後端 API 開發（1-2 個項目）
     - 前端 UI 組件（1-2 個項目）
     - 整合測試（1 個項目）
     - 樣式和 UX 優化（1 個項目）
   - 確保每個項目都有：
     - 清楚的描述
     - 詳細的測試步驟
     - 預期的驗證結果

6. **更新 feature_list.json**
   - 讀取現有的 feature_list.json
   - 將新項目加入到適當位置（根據優先級）
   - 保持現有項目的完整性（不刪除、不修改已完成項目）
   - 確保所有新項目的 `"passes": false`
   - 保持 JSON 格式正確

7. **驗證更新**
   - 檢查 feature_list.json 的格式正確性
   - 確認新項目的大小適中（單一 session 可完成）
   - 確認測試步驟完整且可執行
   - 確認優先級排序合理

8. **儲存更新**
   - 將更新後的 feature_list.json 寫回專案目錄
   - 顯示新增的項目摘要
   - 建議下一步可以開始實作哪些項目
</steps>

<output>
更新後的 feature_list.json 應該包含新增的項目，格式如下：

```json
[
  {
    "category": "functional",
    "description": "[新功能項目 1 的描述]",
    "steps": [
      "Step 1: [具體步驟]",
      "Step 2: [具體步驟]",
      "Step 3: [驗證步驟]"
    ],
    "passes": false
  },
  {
    "category": "functional",
    "description": "[新功能項目 2 的描述]",
    "steps": [
      "Step 1: [具體步驟]",
      "Step 2: [具體步驟]",
      "...",
      "Step 10: [驗證步驟]"
    ],
    "passes": false
  }
  // ... 現有項目保持不變
]
```
</output>

<example>
假設要為任務管理應用新增「任務分類」功能：

**輸入：**
- 專案路徑：`./generations/task-manager`
- 新功能：任務分類功能，使用者可以為任務設定分類標籤

**產出：**
```json
[
  // ... 現有項目 ...
  {
    "category": "functional",
    "description": "後端 API: 建立任務分類資料模型和 CRUD 端點",
    "steps": [
      "Step 1: 在資料庫中建立 category 資料表",
      "Step 2: 建立 Supabase Edge Function 處理分類 CRUD",
      "Step 3: 測試建立分類 API",
      "Step 4: 測試讀取分類列表 API",
      "Step 5: 測試更新分類 API",
      "Step 6: 測試刪除分類 API"
    ],
    "passes": false
  },
  {
    "category": "functional",
    "description": "前端 UI: 分類選擇器組件",
    "steps": [
      "Step 1: 建立 CategorySelector 組件",
      "Step 2: 整合分類列表 API",
      "Step 3: 實作分類選擇 UI（下拉選單或多選）",
      "Step 4: 測試組件互動",
      "Step 5: 驗證視覺樣式"
    ],
    "passes": false
  },
  {
    "category": "functional",
    "description": "整合: 任務表單中加入分類選擇",
    "steps": [
      "Step 1: 在任務建立表單中整合 CategorySelector",
      "Step 2: 在任務編輯表單中整合 CategorySelector",
      "Step 3: 更新任務 API 呼叫以包含分類資訊",
      "Step 4: 測試建立帶分類的任務",
      "Step 5: 測試編輯任務分類",
      "Step 6: 驗證分類資料正確儲存"
    ],
    "passes": false
  },
  {
    "category": "functional",
    "description": "功能: 依分類篩選任務列表",
    "steps": [
      "Step 1: 在任務列表頁面加入分類篩選器",
      "Step 2: 實作篩選邏輯（前端或後端）",
      "Step 3: 測試篩選功能",
      "Step 4: 驗證 UI 互動流暢"
    ],
    "passes": false
  },
  {
    "category": "style",
    "description": "UI/UX: 分類標籤的視覺設計和互動",
    "steps": [
      "Step 1: 設計分類標籤的視覺樣式",
      "Step 2: 實作標籤顯示（顏色、圖示等）",
      "Step 3: 加入 hover 和選取狀態",
      "Step 4: 驗證響應式設計",
      "Step 5: 截圖驗證視覺效果"
    ],
    "passes": false
  }
]
```
</example>

<constraints>
- 必須徹底探索現有程式碼庫，理解相關模組和模式
- 功能拆解必須適當，每個項目應該可以在單一 session 完成至少 1 個
- 不能刪除或修改現有的 feature_list.json 項目（已完成或進行中）
- 新項目的測試步驟必須具體且可執行
- 必須考慮與現有功能的整合點
- 探索時必須使用並行的 subagents 以提高效率
- 如果專案中沒有 feature_list.json，應該先執行初始化流程
</constraints>

