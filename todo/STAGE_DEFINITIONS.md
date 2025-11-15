# Stage Definitions & Naming Convention

## 📊 Project Stages Overview

Each **Stage** represents a major milestone where the system gains significant new capabilities. Stages are completed sequentially, with each building on the previous.

## Stage Definitions

### Stage 1: Foundation 🏗️
**Goal**: Basic document handling infrastructure
- Document upload functionality
- PDF/Word/Excel parsing
- Text extraction and cleaning
- SQLite database setup
- ChromaDB initialization
- Basic file management

**Key Deliverables**:
- Upload API endpoint
- Document parser module
- Database schema
- Basic error handling

---

### Stage 2: RAG Core 🔍
**Goal**: Retrieval-Augmented Generation implementation
- Document chunking strategies
- Embedding generation
- Vector storage and indexing
- Retrieval algorithms
- LLM integration (llama.cpp)
- Basic Q&A functionality
- Citation tracking

**Key Deliverables**:
- Chunking service
- Embedding pipeline
- Query API endpoint
- Citation system

---

### Stage 3: Standards Support 📋
**Goal**: Specialized handling for compliance standards
- IEC 62443 parser and analyzer
- ETSI EN 303 645 support
- EN 18031 integration
- Section/clause extraction
- Cross-reference detection
- Compliance checking

**Key Deliverables**:
- Standards-specific parsers
- Compliance analyzer
- Gap analysis tools

---

### Stage 4: Intelligence Layer 🧠
**Goal**: Advanced analysis capabilities
- Knowledge graph construction (Neo4j)
- Cross-document analysis
- Entity relationship mapping
- Multi-hop reasoning
- Query optimization
- Confidence scoring

**Key Deliverables**:
- Knowledge graph builder
- Relationship analyzer
- Advanced query engine

---

### Stage 5: Production Ready 🚀
**Goal**: User interface and operational features
- Web UI (Gradio → Svelte)
- Complete audit trail system
- User feedback collection
- Performance optimization
- Error recovery
- Monitoring and logging

**Key Deliverables**:
- Production UI
- Audit system
- Performance metrics
- User manual

---

### Stage 6: Advanced Features ⚡
**Goal**: Enterprise and advanced capabilities
- Multi-user support
- Fine-tuning pipeline
- Advanced analytics
- Export/import capabilities
- API for external integration
- Scalability improvements

**Key Deliverables**:
- User management system
- Fine-tuning tools
- Analytics dashboard
- REST API

---

## 📁 Stage-Based Naming Convention

### File Naming Pattern
```
Stage{N}-{type}-{number}.{extension}
```

### Examples by File Type

#### Requirements
```
Stage1-req-001.json     # First requirement for Stage 1
Stage2-req-003.json     # Third requirement for Stage 2
```

#### Tasks
```
Stage1-task-001.json    # Upload functionality
Stage1-task-002.json    # PDF parsing
Stage2-task-001.json    # Chunking implementation
```

#### API Contracts
```
Stage1-api-001.json     # Upload API contract
Stage2-api-001.json     # Query API contract
Stage1-contract-001.json # Alternative naming
```

#### Dependencies
```
Stage1-dep-001.json     # Stage 1 dependencies
Stage2-dep-001.json     # Stage 2 dependencies
```

#### Reviews & Tests
```
Stage1-review-001.json  # Code review results
Stage1-test-001.json    # Test results
```

#### Code Files
```
Stage1-backend-upload.py    # Backend code
Stage1-frontend-upload.html # Frontend code
Stage2-rag-chunker.py       # RAG component
```

### Directory Structure Example
```
.claude-bus/
├── planning/
│   ├── Stage1-req-001.json
│   ├── Stage1-req-002.json
│   └── Stage2-req-001.json
├── tasks/
│   ├── Stage1-task-001.json  # Upload
│   ├── Stage1-task-002.json  # Parse
│   ├── Stage1-task-003.json  # Store
│   └── Stage2-task-001.json  # Chunk
├── code/
│   ├── Stage1-backend/
│   ├── Stage1-frontend/
│   └── Stage2-rag/
└── reviews/
    ├── Stage1-review-001.json
    └── Stage1-review-002.json
```

## 🎯 Benefits of Stage-Based Organization

1. **Clear Progress Tracking**: Instantly see what stage the project is in
2. **Easy Filtering**: `ls Stage1-*.json` shows all Stage 1 work
3. **No Confusion**: Tasks from different stages never mix
4. **Historical Record**: Keep all stages for reference
5. **Parallel Numbering**: Each stage can have task-001 without conflict
6. **Clear Dependencies**: Stage 2 work clearly depends on Stage 1 completion

## 🔄 Stage Transitions

### Completing a Stage
A stage is complete when:
- All tasks marked "completed"
- All tests passing
- QA approval received
- Git tag created (e.g., `v1.0.0-stage1`)
- User documentation updated

### Starting Next Stage
To begin a new stage:
1. Create `Stage{N}-req-001.json` with requirements
2. PM-Architect-Agent decomposes into tasks
3. Update current stage in `notes.md`
4. Continue workflow phases

## 📋 Quick Commands

```bash
# View all Stage 1 files
ls .claude-bus/**/Stage1-*

# Count Stage 1 tasks
ls .claude-bus/tasks/Stage1-*.json | wc -l

# Find incomplete Stage 1 tasks
grep -l "pending\|in_progress" .claude-bus/tasks/Stage1-*.json

# Archive completed stage
mkdir .claude-bus/archive/Stage1
mv .claude-bus/tasks/Stage1-*.json .claude-bus/archive/Stage1/
```

## 🏷️ Current Stage Tracking

The current active stage should be noted in:
- `D:\gpt-oss\notes.md` - Under "Active Stage"
- Git branch name: `stage-1-foundation`
- Git tags: `v0.1.0-stage1-start`, `v1.0.0-stage1-complete`

---

*This naming convention ensures clear organization and progress tracking throughout the multi-stage development process.*