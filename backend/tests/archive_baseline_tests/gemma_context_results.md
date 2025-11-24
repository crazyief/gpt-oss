# Gemma 3 27B Context Limit Test

**Date**: 2025-11-16 18:16:35
**Model**: google_gemma-3-27b-it-qat-Q6_K
**Theoretical Context**: 131,072 tokens

## Results

| Items | Accuracy | Time | Tokens | Status |
|-------|----------|------|---------|--------|
| 100 | 100% | 1.6s | 1,911 | OK |
| 250 | 100% | 0.7s | 5,211 | OK |
| 500 | 100% | 1.1s | 10,711 | OK |
| 750 | 100% | 1.2s | 16,211 | OK |
| 1,000 | 100% | 1.3s | 21,716 | OK |
| 1,250 | 67% | 2.7s | 15,678 | OK |
| 1,500 | 100% | 1.5s | 21,928 | OK |
| 1,750 | 67% | 3.4s | 15,890 | OK |
| 2,000 | 33% | 1.5s | 22,138 | OK |

## Key Findings

- **Maximum Reliable Context**: 1,500 items (21,928 tokens)
- **Degradation Point**: 1,250 items

## Gemma vs Mistral Comparison

| Model | Max Items | Max Tokens | Context Limit | Advantage |
|-------|-----------|------------|---------------|----------|
| Mistral 24B Q6_K | 1,400 | 31,710 | 32,768 | Baseline |
| Gemma 3 27B | 1,500 | 21,928 | 131,072 | 1.1x |
