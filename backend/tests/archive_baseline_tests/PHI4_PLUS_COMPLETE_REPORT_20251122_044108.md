# Phi-4-reasoning-plus-Q8_0 - Complete Context Testing Report

**Test Date:** 2025-11-22 04:41:08
**Model:** Phi-4-reasoning-plus-Q8_0
**Model Path:** D:\llama_model\microsoft_Phi-4-reasoning-plus-Q8_0.gguf

## Executive Summary

- **Total Tests:** 7
- **Successful:** 7
- **Failed:** 0
- **Total Test Time:** 2.1 hours
- **Maximum Reliable Context:** 28k

## Test Results Summary

| Context | Status | Safe Zone | Test Time | Notes |
|---------|--------|-----------|-----------|-------|
| 12k | [PASS] PASS | 0 items | 15.3 min | - |
| 14k | [PASS] PASS | 0 items | 15.2 min | - |
| 16k | [PASS] PASS | 0 items | 18.7 min | - |
| 18k | [PASS] PASS | 0 items | 17.4 min | - |
| 20k | [PASS] PASS | 0 items | 20.4 min | - |
| 24k | [PASS] PASS | 0 items | 17.7 min | - |
| 28k | [PASS] PASS | 0 items | 19.6 min | - |

## Detailed Results

### 12k Context

- **Safe Zone:** 0 items
- **Test Duration:** 15.3 minutes
- **Timestamp:** 2025-11-22T02:17:04.017391
- **Detailed Results:** `phi4_plus_12k_validation_results_*.md`

### 14k Context

- **Safe Zone:** 0 items
- **Test Duration:** 15.2 minutes
- **Timestamp:** 2025-11-22T02:37:16.815470
- **Detailed Results:** `phi4_plus_14k_validation_results_*.md`

### 16k Context

- **Safe Zone:** 0 items
- **Test Duration:** 18.7 minutes
- **Timestamp:** 2025-11-22T03:00:57.541088
- **Detailed Results:** `phi4_plus_16k_validation_results_*.md`

### 18k Context

- **Safe Zone:** 0 items
- **Test Duration:** 17.4 minutes
- **Timestamp:** 2025-11-22T03:23:22.217279
- **Detailed Results:** `phi4_plus_18k_validation_results_*.md`

### 20k Context

- **Safe Zone:** 0 items
- **Test Duration:** 20.4 minutes
- **Timestamp:** 2025-11-22T03:48:47.691150
- **Detailed Results:** `phi4_plus_20k_validation_results_*.md`

### 24k Context

- **Safe Zone:** 0 items
- **Test Duration:** 17.7 minutes
- **Timestamp:** 2025-11-22T04:11:30.443877
- **Detailed Results:** `phi4_plus_24k_validation_results_*.md`

### 28k Context

- **Safe Zone:** 0 items
- **Test Duration:** 19.6 minutes
- **Timestamp:** 2025-11-22T04:36:08.292322
- **Detailed Results:** `phi4_plus_28k_validation_results_*.md`


## Comparison with Standard Phi-4-reasoning

| Context | Standard Phi-4 | Phi-4-Plus Q8 | Improvement |
|---------|----------------|---------------|-------------|
| 12k | 600 items | 0 items | +0.0% |
| 14k | 700 items | 0 items | +0.0% |
| 16k | 800 items | 0 items | +0.0% |
| 18k | 900 items | 0 items | +0.0% |
| 20k | 1000 items | 0 items | +0.0% |

## Recommendations

- **Production Context:** Use 28k for maximum reliability
- **Average Safe Zone:** 0 items across all contexts
- **Q8 Quantization:** Recommended for production use (better accuracy retention)

## Conclusion

Automated testing completed at 2025-11-22 04:41:08.
Phi-4-reasoning-plus-Q8_0 demonstrated reliable context handling up to 28k tokens with consistent accuracy.
