# phi-4-reasoning 18k Context Validation Report

**Model**: Magistral-Small-2506-Q6_K_L (18k context)
**Context Window**: 18,000 tokens (~1000 items)
**Test Date**: 2025-11-20 18:02:39
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 243
- **Phase 1 Queries**: 198 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-1050 items)

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
| 1000 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1050 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1100 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 | 100.0% | [PASS] |
| 500 | 15 | 100.0% | [PASS] |
| 1000 | 15 | 100.0% | [PASS] |

## Verdict

**[WARNING]** Some tests failed.

- Review individual test results
- Consider reducing safe zone limit
