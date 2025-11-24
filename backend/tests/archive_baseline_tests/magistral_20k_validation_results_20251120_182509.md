# phi-4-reasoning 20k Context Validation Report

**Model**: Magistral-Small-2506-Q6_K_L (20k context)
**Context Window**: 20,000 tokens (~1200 items)
**Test Date**: 2025-11-20 18:25:09
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 279
- **Phase 1 Queries**: 234 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-1250 items)

| Item Count | Overall | First | Middle | Last | Status |
|------------|---------|-------|--------|------|--------|
|  50 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 100 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 150 |  88.9% |  66.7% | 100.0% | 100.0% | [SUSPECT] |
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
| 1100 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1150 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1200 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 1250 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |
| 1300 |   0.0% |   0.0% |   0.0% |   0.0% | [DANGER] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 | 100.0% | [PASS] |
| 600 | 15 | 100.0% | [PASS] |
| 1200 | 15 |   0.0% | [FAIL] |

## Verdict

**[WARNING]** Some tests failed.

- Review individual test results
- Consider reducing safe zone limit
