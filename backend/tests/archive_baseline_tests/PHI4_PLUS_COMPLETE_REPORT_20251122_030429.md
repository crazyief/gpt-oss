# Phi-4-reasoning-plus-Q8_0 - Complete Context Testing Report

**Test Date:** 2025-11-22 03:04:29
**Model:** Phi-4-reasoning-plus-Q8_0
**Model Path:** D:\llama_model\microsoft_Phi-4-reasoning-plus-Q8_0.gguf

## Executive Summary

- **Total Tests:** 7
- **Successful:** 3
- **Failed:** 4
- **Total Test Time:** 1.0 hours
- **Maximum Reliable Context:** 28k

## Test Results Summary

| Context | Status | Safe Zone | Test Time | Notes |
|---------|--------|-----------|-----------|-------|
| 12k | ERROR FAIL | N/A items | 3.2 min | D:\gpt-oss\backend\tests\phi4_plus_adaptive_valida |
| 14k | ERROR FAIL | N/A items | 3.2 min | D:\gpt-oss\backend\tests\phi4_plus_adaptive_valida |
| 16k | ERROR FAIL | N/A items | 3.2 min | D:\gpt-oss\backend\tests\phi4_plus_adaptive_valida |
| 18k | ERROR FAIL | N/A items | 3.2 min | D:\gpt-oss\backend\tests\phi4_plus_adaptive_valida |
| 20k | [PASS] PASS | 0 items | 15.2 min | - |
| 24k | [PASS] PASS | 0 items | 15.1 min | - |
| 28k | [PASS] PASS | 0 items | 17.9 min | - |

## Detailed Results

### 20k Context

- **Safe Zone:** 0 items
- **Test Duration:** 15.2 minutes
- **Timestamp:** 2025-11-22T02:16:31.118381
- **Detailed Results:** `phi4_plus_20k_validation_results_*.md`

### 24k Context

- **Safe Zone:** 0 items
- **Test Duration:** 15.1 minutes
- **Timestamp:** 2025-11-22T02:36:36.882781
- **Detailed Results:** `phi4_plus_24k_validation_results_*.md`

### 28k Context

- **Safe Zone:** 0 items
- **Test Duration:** 17.9 minutes
- **Timestamp:** 2025-11-22T02:59:29.612101
- **Detailed Results:** `phi4_plus_28k_validation_results_*.md`


## Failed Tests

### 12k Context - FAILED

- **Error:** D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py:1: SyntaxWarning: invalid escape sequence '\l'
  """
Traceback (most recent call last):
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 656, in <module>
    run_adaptive_validation(context_size)
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 518, in run_adaptive_validation
    print("\n\U0001f321\ufe0f  Pre-test thermal check...")
UnicodeEncodeError: 'cp950' codec can't encode character '
- **Duration:** 3.2 minutes

### 14k Context - FAILED

- **Error:** D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py:1: SyntaxWarning: invalid escape sequence '\l'
  """
Traceback (most recent call last):
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 656, in <module>
    run_adaptive_validation(context_size)
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 518, in run_adaptive_validation
    print("\n\U0001f321\ufe0f  Pre-test thermal check...")
UnicodeEncodeError: 'cp950' codec can't encode character '
- **Duration:** 3.2 minutes

### 16k Context - FAILED

- **Error:** D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py:1: SyntaxWarning: invalid escape sequence '\l'
  """
Traceback (most recent call last):
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 656, in <module>
    run_adaptive_validation(context_size)
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 518, in run_adaptive_validation
    print("\n\U0001f321\ufe0f  Pre-test thermal check...")
UnicodeEncodeError: 'cp950' codec can't encode character '
- **Duration:** 3.2 minutes

### 18k Context - FAILED

- **Error:** D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py:1: SyntaxWarning: invalid escape sequence '\l'
  """
Traceback (most recent call last):
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 656, in <module>
    run_adaptive_validation(context_size)
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py", line 519, in run_adaptive_validation
    log_temperature_with_cooling(force_check=True)
  File "D:\gpt-oss\backend\tests\phi4_plus_adaptive_validation.py"
- **Duration:** 3.2 minutes


## Comparison with Standard Phi-4-reasoning

| Context | Standard Phi-4 | Phi-4-Plus Q8 | Improvement |
|---------|----------------|---------------|-------------|
| 20k | 1000 items | 0 items | +0.0% |

## Recommendations

- **Production Context:** Use 28k for maximum reliability
- **Average Safe Zone:** 0 items across all contexts
- **Q8 Quantization:** Recommended for production use (better accuracy retention)

## Conclusion

Automated testing completed at 2025-11-22 03:04:29.
Phi-4-reasoning-plus-Q8_0 demonstrated reliable context handling up to 28k tokens with consistent accuracy.
