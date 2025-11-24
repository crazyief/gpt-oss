# Gemma 27B Context Limit Analysis

**Date**: 2025-11-19 10:30:24
**Purpose**: Find exact context limit between 250 (works) and 750 (fails)

## Results

| Items | Tokens | Status |
|-------|--------|--------|
| 300 | 6,307 | ✅ Works |
| 350 | 7,407 | ✅ Works |
| 400 | 8,507 | ✅ Works |
| 450 | 9,607 | ✅ Works |
| 500 | 10,707 | ✅ Works |
| 550 | 11,807 | ✅ Works |
| 600 | N/A | ❌ Failed |
| 650 | N/A | ❌ Failed |
| 700 | N/A | ❌ Failed |

## Conclusion

- **Last working size**: 550 items (11807 tokens)
- **First failing size**: 600 items
- **Estimated hard limit**: ~575 items

This is a hard configuration limit (HTTP 400), not an accuracy degradation.
