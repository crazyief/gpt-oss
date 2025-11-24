# Magistral-Small-2506_Q8_0 Context Limit Test

**Date**: 2025-11-18 19:51:02
**Model**: Magistral-Small-2506_Q8_0
**Configured Context**: 32,768 tokens

## Results

| Items | Accuracy | Time | Tokens | Status |
|-------|----------|------|---------|--------|
| 100 | 100% | 0.3s | 1,905 | OK |
| 250 | 100% | 0.5s | 5,205 | OK |
| 500 | 100% | 0.7s | 10,705 | OK |
| 750 | 67% | 0.8s | 16,205 | OK |
| 1,000 | 100% | 0.9s | 21,710 | OK |
| 1,250 | 67% | 1.1s | 27,960 | OK |
| 1,400 | 67% | 0.8s | 31,710 | OK |
| 1,500 | - | - | 34,200 | EXCEEDED |

## Key Findings

- **Maximum Reliable Context**: 1,000 items (21,710 tokens)
- **Context Utilization**: 66.3% of 32k
- **Average Response Time**: 0.9s
- **Token Efficiency**: 21.7 tokens per item
- **Degradation Point**: 750 items
- **Context Limit Hit**: At 1,500 items (needs 34,200 tokens)

## Test Methodology

- **Test Type**: Needle-in-haystack (indexed items)
- **Positions Tested**: First, Middle, Last
- **Temperature**: 0 (deterministic)
- **Success Criteria**: 95%+ accuracy
