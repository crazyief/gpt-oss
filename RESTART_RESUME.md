# 测试进度恢复指南 (2025-11-21)

## ✅ 已完成测试 (25/30 = 83.3%)

### Run 1: phi-4-reasoning-UD-Q8_K_XL
- 12k: 650 items ✅
- 14k: 800 items ✅
- 16k: 950 items ✅
- 18k: 1100 items ✅
- 20k: 1300 items ✅

### Run 2: Mistral-Small-24B-Instruct-2501-Q6_K
- 12k: 650 items ✅
- 14k: 800 items ✅
- 16k: 950 items ✅
- 18k: 1050 items ✅
- 20k: 1150 items ✅

### Run 3: Magistral-Small-2506-Q6_K_L
- 12k: 650 items ✅
- 14k: 800 items ✅
- 16k: 950 items ✅
- 18k: 1050 items ✅
- 20k: 1150 items ✅

### Run 4: Magistral-Small-2506-Q8_0
- 12k: 650 items ✅
- 14k: 800 items ✅
- 16k: 950 items ✅
- 18k: 1050 items ✅
- 20k: 1150 items ✅

### Run 5: google_gemma-3-27b-it-qat-Q6_K
- 12k: 650 items ✅
- 14k: 800 items ✅
- 16k: 500 items ⚠️ (CATASTROPHIC DEGRADATION)
- 18k: 1050 items ✅ (FULL RECOVERY)
- 20k: 1150 items ✅ (TOP TIER)

---

## ⏳ 待完成测试 (5/30 = 16.7%)

### Run 6: Falcon-H1-34B-Instruct-Q5_K_M
- 12k: ⏳ PENDING
- 14k: ⏳ PENDING
- 16k: ⏳ PENDING
- 18k: ⏳ PENDING
- 20k: ⏳ PENDING

**注**: Falcon @ 13k已在之前完成 (650 items, 100%)

---

## 📁 已保存数据文件

### 主要进度文件:
- `D:\gpt-oss\CONTEXT_TEST_PROGRESS.md` - 总进度追踪
- `D:\gpt-oss\RESTART_RESUME.md` - 本文件（恢复指南）

### 详细测试结果 (backend/tests/):
```
# phi-4 (5个测试)
phi4_12k_phase1_*.json + phase3_*.json + validation_results_*.md
phi4_14k_phase1_*.json + phase3_*.json + validation_results_*.md
phi4_16k_phase1_*.json + phase3_*.json + validation_results_*.md
phi4_18k_phase1_*.json + phase3_*.json + validation_results_*.md
phi4_20k_phase1_*.json + phase3_*.json + validation_results_*.md

# Mistral-Small (5个测试)
mistral_small_12k_phase1_*.json + phase3_*.json + validation_results_*.md
mistral_small_14k_phase1_*.json + phase3_*.json + validation_results_*.md
mistral_small_16k_phase1_*.json + phase3_*.json + validation_results_*.md
mistral_small_18k_phase1_*.json + phase3_*.json + validation_results_*.md
mistral_small_20k_phase1_*.json + phase3_*.json + validation_results_*.md

# Magistral-Q6_K_L (5个测试)
magistral_12k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_14k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_16k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_18k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_20k_phase1_*.json + phase3_*.json + validation_results_*.md

# Magistral-Q8_0 (5个测试)
magistral_q8_12k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_q8_14k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_q8_16k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_q8_18k_phase1_*.json + phase3_*.json + validation_results_*.md
magistral_q8_20k_phase1_*.json + phase3_*.json + validation_results_*.md

# Gemma-3-27b (5个测试)
gemma_12k_phase1_*.json + phase3_*.json + validation_results_*.md
gemma_14k_phase1_*.json + phase3_*.json + validation_results_*.md
gemma_16k_phase1_*.json (部分数据 - 提前终止)
gemma_18k_phase1_20251121_001422.json + phase3_20251121_001844.json + validation_results_*.md
gemma_20k_phase1_20251121_084108.json + phase3_20251121_084545.json + validation_results_*.md
```

---

## 🔄 重启后恢复步骤

### 1. 确认数据完整性
```bash
# 检查主要进度文件
ls -lh D:\gpt-oss\CONTEXT_TEST_PROGRESS.md
ls -lh D:\gpt-oss\RESTART_RESUME.md

# 检查测试结果数量
cd D:\gpt-oss\backend\tests
ls *_phase1_*.json | wc -l  # 应该有 24-25个
ls *_phase3_*.json | wc -l  # 应该有 24-25个
ls *_validation_results_*.md | wc -l  # 应该有 24-25个
```

### 2. 继续 Run 6: Falcon-H1 测试

**方法1: 自动继续（推荐）**
- 重启后直接告诉Claude: "继续Run 6: Falcon-H1测试"
- Claude会自动执行剩余5个测试

**方法2: 手动执行**
需要的文件已准备好：
- `backend/tests/falcon_12k_3phase_validation.py`
- `backend/tests/falcon_14k_3phase_validation.py`
- `backend/tests/falcon_16k_3phase_validation.py`
- `backend/tests/falcon_18k_3phase_validation.py`
- `backend/tests/falcon_20k_3phase_validation.py`
- `backend/tests/falcon_warmup.py`

### 3. 最终报告生成
完成Falcon测试后，生成：
- 综合对比表（所有模型 × 所有CTX）
- RAG部署建议
- CTX vs Safe Zone可视化

---

## 🔑 关键发现（到目前为止）

### 最佳模型（12k-20k全能）:
1. **phi-4-reasoning** - 最强扩展性（20k达到1300 items）
2. **Mistral-Small-24B** - 稳定可靠（12k-20k一致表现）
3. **Magistral-Q6_K_L** - 与Mistral相同表现

### 特殊发现:
- **Gemma @ 16k崩溃** - 从800→500 items（-37.5%）
- **Gemma @ 18k恢复** - 1050 items（超越14k）
- **Gemma @ 20k顶峰** - 1150 items（与顶级模型持平）
- **Q8 vs Q6**: 没有差异（context利用率相同）

### RAG配置建议（基于现有数据）:
- **推荐CTX**: 12k-14k（sweet spot，所有模型稳定）
- **避免CTX**: Gemma @ 16k（性能陷阱）
- **主力模型**: phi-4-reasoning（最佳扩展性）
- **备用模型**: Mistral-Small-24B（生产验证）

---

## ⏱️ 预计剩余时间

**Falcon-H1 @ 12k-20k (5 tests)**:
- 每个测试约10-12分钟
- 总计: ~50-60分钟

**最终报告生成**: ~5分钟

**总计**: ~1小时

---

## 📊 当前docker-compose.yml状态

最后配置为: **Gemma @ 20k**
```yaml
llama:
  container_name: gemma-3-27b-20k
  command: >
    --model /models/google_gemma-3-27b-it-qat-Q6_K.gguf
    --ctx-size 20000
```

**重启后需要切换到Falcon模型**

---

**最后更新**: 2025-11-21 08:45 (重启前)
**下一步**: Falcon-H1 @ 12k-20k (5 tests)
