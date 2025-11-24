# phi-4-reasoning 12k Context Validation Report

**Model**: google_gemma-3-27b-it-qat-Q6_K (12k context)
**Context Window**: 12,000 tokens (~600 items)
**Test Date**: 2025-11-20 21:09:57
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 162
- **Phase 1 Queries**: 117 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-600 items)

| Item Count | Overall | First | Middle | Last | Status |
|------------|---------|-------|--------|------|--------|
|  50 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 100 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 150 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 200 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 250 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 300 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 350 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 400 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 450 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 500 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 550 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 600 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 650 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 |   0.0% | [FAIL] |
| 300 | 15 |   0.0% | [FAIL] |
| 600 | 15 |   0.0% | [FAIL] |

## Verdict

**[WARNING]** Some tests failed.

- Review individual test results
- Consider reducing safe zone limit
