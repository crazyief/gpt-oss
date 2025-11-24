# Mistral 24B Q6_K Context Limit Test

**Date**: 2025-11-16 17:37:45
**Model**: mistral-small-24b-Q6_K
**Configured Context**: 32,768 tokens

## Results

| Items | Accuracy | Time | Tokens | Status |
|-------|----------|------|---------|--------|
| 100 | 100% | 1.2s | 1,905 | OK |
| 250 | 100% | 0.5s | 5,205 | OK |
| 500 | 67% | 0.7s | 10,705 | OK |
| 750 | 67% | 0.9s | 16,205 | OK |
| 1,000 | 100% | 0.9s | 21,710 | OK |
| 1,100 | 100% | 0.6s | 24,210 | OK |
| 1,200 | 67% | 0.6s | 26,710 | OK |
| 1,300 | 100% | 0.6s | 29,210 | OK |
| 1,400 | 100% | 0.6s | 31,710 | OK |
| 1,450 | - | - | 32,950 | EXCEEDED |

## Key Findings

- **Maximum Reliable Context**: 1,400 items (31,710 tokens)
- **Degradation Point**: 500 items
- **Context Limit Hit**: At 1,450 items (needs 32,950 tokens)
