# phi-4-reasoning 12k Context Validation Report

**Model**: Magistral-Small-2506-Q8_0 (14k context)
**Context Window**: 14,000 tokens (~600 items)
**Test Date**: 2025-11-20 20:33:23
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 198
- **Phase 1 Queries**: 153 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-800 items)

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
| 700 |  66.7% |  66.7% |  66.7% |  66.7% | [DANGER] |
| 750 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 800 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 850 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 | 100.0% | [PASS] |
| 400 | 15 | 100.0% | [PASS] |
| 800 | 15 | 100.0% | [PASS] |

## Verdict

**[WARNING]** Some tests failed.

- Review individual test results
- Consider reducing safe zone limit
