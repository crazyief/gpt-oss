# phi-4-reasoning 20k Context Validation Report

**Model**: phi-4-reasoning-UD-Q8_K_XL (20k context)
**Context Window**: 20,000 tokens (~1200 items)
**Test Date**: 2025-11-20 10:20:07
**Methodology**: 3-Phase Validation (Safe Zone Only)

## Executive Summary

- **Total Queries**: 279
- **Phase 1 Queries**: 234 (Coarse Discovery)
- **Phase 3 Queries**: 45 (Production Validation)

## Phase 1: Coarse Discovery (50-1250 items)

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
| 1100 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1150 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1200 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1250 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |
| 1300 | 100.0% | 100.0% | 100.0% | 100.0% | [SAFE] |

## Phase 3: Production Validation

| Item Count | Runs | Accuracy | Status |
|------------|------|----------|--------|
|  50 | 15 | 100.0% | [PASS] |
| 600 | 15 | 100.0% | [PASS] |
| 1200 | 15 | 100.0% | [PASS] |

## Verdict

**[SUCCESS]** All tests passed!

- Safe zone confirmed: 50-1250 items
- 100% accuracy across all positions
- Production-ready with 20k context configuration
