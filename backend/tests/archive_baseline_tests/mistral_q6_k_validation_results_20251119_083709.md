# Mistral Q6_K Scientific Validation Results

**Date**: 2025-11-19 08:37:09
**Purpose**: Verify suspicious 67% accuracy points and fill missing data gaps

## Summary

| Items | Overall | First | Middle | Last | Consistency |
|-------|---------|-------|--------|------|-------------|
| 500 | 67% | 100% | 0% | 100% | Stable |
| 750 | 67% | 100% | 0% | 100% | Stable |
| 1200 | 67% | 100% | 0% | 100% | Stable |
| 1250 | 100% | 100% | 100% | 100% | Stable |

## Detailed Results

### 500 Items

**Test Reason**: Previously 67% - verify if consistent

**FIRST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 10701
- Results: [OK] [OK] [OK] [OK] [OK] 

**MIDDLE Position**:
- Accuracy: 0% (0/5)
- Avg Tokens: 10705
- Results: [X] [X] [X] [X] [X] 

**LAST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 10705
- Results: [OK] [OK] [OK] [OK] [OK] 

### 750 Items

**Test Reason**: Previously 67% - verify if consistent

**FIRST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 16201
- Results: [OK] [OK] [OK] [OK] [OK] 

**MIDDLE Position**:
- Accuracy: 0% (0/5)
- Avg Tokens: 16204
- Results: [X] [X] [X] [X] [X] 

**LAST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 16205
- Results: [OK] [OK] [OK] [OK] [OK] 

### 1200 Items

**Test Reason**: Previously 67% - verify if consistent

**FIRST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 26704
- Results: [OK] [OK] [OK] [OK] [OK] 

**MIDDLE Position**:
- Accuracy: 0% (0/5)
- Avg Tokens: 26709
- Results: [X] [X] [X] [X] [X] 

**LAST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 26710
- Results: [OK] [OK] [OK] [OK] [OK] 

### 1250 Items

**Test Reason**: Missing data point - compare with Magistral

**FIRST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 27954
- Results: [OK] [OK] [OK] [OK] [OK] 

**MIDDLE Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 27958
- Results: [OK] [OK] [OK] [OK] [OK] 

**LAST Position**:
- Accuracy: 100% (5/5)
- Avg Tokens: 27960
- Results: [OK] [OK] [OK] [OK] [OK] 


## Recommendations

- **500 items**: Update to 0% (was 67%, now consistently fails - SYSTEMATIC BUG)
- **750 items**: Update to 0% (was 67%, now consistently fails - SYSTEMATIC BUG)
- **1200 items**: Update to 0% (was 67%, now consistently fails - SYSTEMATIC BUG)
- **1250 items**: Update to 100% (was 67%, now consistently correct)
