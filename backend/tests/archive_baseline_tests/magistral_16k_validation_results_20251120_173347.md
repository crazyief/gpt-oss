# phi-4-reasoning 16k Context Validation Report

**Model**: Magistral-Small-2506-Q6_K_L (16k context)
**Context Window**: 16,000 tokens (~800 items)
**Test Date**: 2025-11-20 17:33:47
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 216
- **Phase 1 Queries**: 171 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-900 items)

| Item Count | Overall | First | Middle | Last | Status |
|------------|---------|-------|--------|------|--------|
|  50 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 100 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 150 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 200 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 250 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 300 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 350 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 400 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 450 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 500 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 550 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 600 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 650 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 700 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 750 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 800 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 850 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 900 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 950 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 | 100.0% | [PASS] |
| 400 | 15 | 100.0% | [PASS] |
| 800 | 15 | 100.0% | [PASS] |

## Verdict

**[SUCCESS]** All tests passed!

- Safe zone confirmed: 50-900 items
- 100% accuracy across all positions
- Production-ready with 16k context configuration
