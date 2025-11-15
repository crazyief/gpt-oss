# 📋 GPT-OSS 專案 Chatroom Summary

## 專案概述
建立了一個完整的 **Local LLM + LightRAG** 系統，整合本地 LLM (gpt-oss-20b) 與知識圖譜 RAG。

## 核心架構
- **LLM**: llama.cpp 運行 gpt-oss-20b-UD-Q8_K_XL.gguf (GPU 加速)
- **向量搜尋**: ChromaDB (專門的向量資料庫)
- **知識圖譜**: Neo4j (實體關係)
- **結構化資料**: SQLite (專案、聊天、文檔metadata)
- **檔案存儲**: 檔案系統 (只存二進制檔案)
- **Backend**: FastAPI + LightRAG + SQLAlchemy
- **Frontend**: Svelte + SvelteKit + TypeScript (待開發)

## 前端技術架構 (計畫)
- **框架**: Svelte + SvelteKit
- **語言**: TypeScript
- **樣式**: TailwindCSS
- **即時通訊**: WebSocket Client
- **內容渲染**: Markdown 渲染器
- **程式碼**: Code 語法高亮 (Prism.js/Shiki)
- **圖表**: D3.js/Chart.js (知識圖譜視覺化)

## 重要檔案位置
```
D:\gpt-oss\
├── docker-compose.yml      # 唯一的 Docker 配置
├── start.bat              # Windows 啟動腳本
├── test.py                # 系統測試
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI 主程式
│   │   ├── config.py      # 配置管理
│   │   ├── models/
│   │   │   └── database.py  # SQLAlchemy 模型
│   │   ├── services/
│   │   │   ├── llm_service.py      # LLM 整合
│   │   │   ├── lightrag_service.py # RAG 服務
│   │   │   └── project_manager.py  # 專案管理 (使用 SQLite)
│   │   └── api/
│   │       ├── chat.py      # 對話 API (支援 SSE/WebSocket)
│   │       ├── documents.py # 文檔 API
│   │       └── projects.py  # 專案 API
│   └── requirements.txt
├── frontend/              # Svelte 前端 (待建立)
│   ├── src/
│   │   ├── routes/       # SvelteKit 路由
│   │   ├── lib/          # 共用元件
│   │   │   ├── components/  # UI 元件
│   │   │   ├── stores/      # Svelte stores
│   │   │   └── ws/          # WebSocket 客戶端
│   │   └── app.html      # HTML 模板
│   ├── package.json       # 需要更新為 Svelte 依賴
│   ├── svelte.config.js  # SvelteKit 配置
│   ├── tailwind.config.js # TailwindCSS 配置
│   └── vite.config.ts    # Vite 配置
└── doc/
    ├── data-architecture-v2.md # 更新的資料架構
    └── [其他文檔]
```

## Docker 服務配置
```yaml
services:
  llama:     # LLM 服務 (port 8080)
  neo4j:     # 知識圖譜 (port 7474, 7687)
  chroma:    # 向量資料庫 (port 8001)
  backend:   # FastAPI (port 8000)
  frontend:  # SvelteKit (port 3000) - 待更新
  # postgres: # 未來升級時取消註解
  # redis:    # 未來升級時取消註解
```

## 資料存儲策略 (已更正)
- **SQLite** 存所有結構化資料:
  - 專案資料 (projects 表)
  - 聊天紀錄 (chat_messages 表)
  - 文檔metadata (documents 表)
  - 用戶資料 (users 表 - 未來)
- **Neo4j** 存知識圖譜
- **ChromaDB** 存向量索引
- **檔案系統** 只存上傳的原始檔案

## API 端點
### REST API
- POST `/api/projects/create` - 創建專案
- POST `/api/documents/upload` - 上傳文檔
- POST `/api/chat/chat` - 對話 (支援 streaming)
- GET `/api/projects/{id}/stats` - 專案統計
- GET `/api/projects/{id}/knowledge-graph` - 知識圖譜資料

### WebSocket (待實作)
- `/ws/chat` - 即時對話
- `/ws/notifications` - 系統通知

## 前端功能規劃 (Svelte)
```typescript
// 主要頁面 (routes)
/                     # 首頁/專案列表
/project/[id]        # 專案詳情/聊天介面
/project/[id]/docs   # 文檔管理
/project/[id]/graph  # 知識圖譜視覺化
/settings            # 設定頁面

// 核心元件
ChatInterface.svelte    # 聊天介面 (支援 Markdown)
DocumentUploader.svelte # 文檔上傳 (drag & drop)
KnowledgeGraph.svelte  # 知識圖譜 (D3.js)
CodeBlock.svelte       # 程式碼高亮
```

## 前端 Package.json (需要更新)
```json
{
  "name": "gpt-oss-frontend",
  "type": "module",
  "dependencies": {
    "@sveltejs/adapter-node": "^2.0.0",
    "@sveltejs/kit": "^2.0.0",
    "svelte": "^4.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "marked": "^11.0.0",
    "prismjs": "^1.29.0",
    "d3": "^7.8.0"
  }
}
```

## 啟動方式
```bash
# Backend + 資料庫服務
docker-compose up -d

# Frontend 開發 (Svelte)
cd frontend
npm install
npm run dev

# 包含: LLM + Neo4j + ChromaDB + Backend
# SQLite 自動創建，不需要額外配置
```

## 升級路徑
1. **現在**: SQLite + ChromaDB + Neo4j (個人/小團隊)
2. **未來**: PostgreSQL + ChromaDB + Neo4j + Redis (多用戶/生產)

## 關鍵決策
1. **使用 SQLite 而非檔案系統** 存儲結構化資料 (更合理)
2. **分離不同類型資料** 到專門的資料庫 (效能最佳)
3. **保持升級彈性** (SQLite → PostgreSQL 很容易)
4. **簡化 Docker 配置** (移除複雜的 profiles)
5. **選擇 Svelte 而非 React** (更輕量、效能更好、適合即時應用)

## WebSocket 整合計畫
```typescript
// WebSocket 客戶端 (Svelte)
import { writable } from 'svelte/store';

class ChatWebSocket {
  private ws: WebSocket;
  public messages = writable([]);
  
  connect(projectId: string) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/chat/${projectId}`);
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messages.update(msgs => [...msgs, data]);
    };
  }
  
  send(message: string) {
    this.ws.send(JSON.stringify({ 
      type: 'chat',
      content: message 
    }));
  }
}
```

## 測試命令
```python
# 健康檢查
python health_check.py

# 簡單測試
python test.py

# 完整測試
python test_integration.py
```

## 訪問位址
- API 文檔: http://localhost:8000/docs
- Frontend: http://localhost:3000 (Svelte - 待開發)
- Neo4j: http://localhost:7474 (neo4j/password123)
- ChromaDB: http://localhost:8001
- LLM: http://localhost:8080

## 系統需求
- Docker Desktop with WSL2
- Node.js 18+ (for Svelte development)
- 16GB+ RAM (建議 32GB)
- NVIDIA GPU (可選但建議)
- 50GB 磁碟空間

## 記憶體優化
如果記憶體不足，編輯 docker-compose.yml:
```yaml
command:
  - -ngl 50      # 減少 GPU 層數
  - -c 32768     # 減少上下文長度
```

## 重要提醒
- 第一次啟動需要下載 Docker 映像 (10-20分鐘)
- ChromaDB 大幅提升搜尋效能 (強烈建議使用)
- 所有結構化資料都在 SQLite 中 (不是檔案系統)
- 可以隨時從 SQLite 升級到 PostgreSQL
- Frontend 使用 Svelte + SvelteKit (不是 React)

## 下一步開發
- [ ] 建立 Svelte + SvelteKit 前端專案
- [ ] 實作 WebSocket 即時通訊
- [ ] 整合 Markdown 渲染和程式碼高亮
- [ ] 建立知識圖譜視覺化 (D3.js)
- [ ] 添加用戶認證系統 (使用已建立的 User model)
- [ ] 實現資料遷移腳本 (SQLite → PostgreSQL)
- [ ] 添加更多 RAG 功能 (HyDE, Self-RAG)

## 前端設計理念
- **響應式設計**: Mobile-first with TailwindCSS
- **即時性**: WebSocket 優先，fallback 到 SSE
- **可視性**: Markdown 即時預覽，程式碼語法高亮
- **互動性**: 拖放上傳，知識圖譜可互動
- **效能**: Svelte 編譯時優化，無虛擬 DOM

---

**專案狀態**: 
- ✅ Backend 完整可用
- 🚧 Frontend 待開發 (Svelte + SvelteKit)

**核心價值**: 本地部署、隱私保護、知識圖譜增強的 RAG 系統

**設計原則**: KISS (Keep It Simple, Stupid) - 用對的工具做對的事

**前端選擇**: Svelte (輕量、快速、適合即時應用)
