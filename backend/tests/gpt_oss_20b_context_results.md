# GPT-OSS 20B Context Limit Test

**Date**: 2025-11-16 20:14:54
**Model**: gpt-oss-20b-F16.gguf
**Configured Context**: 131,072 tokens
**Hardware**: RTX 5090 (32GB VRAM)

## Results

| Items | Accuracy | Time | Tokens | Status |
|-------|----------|------|---------|--------|
| 100 | 33% | 1.0s | 1,535 | OK |
| 500 | 0% | 1.2s | 7,535 | OK |
| 1,000 | 0% | 1.4s | 15,038 | OK |
| 1,500 | 0% | 0.9s | 23,538 | OK |
| 2,000 | 0% | 1.0s | 32,038 | OK |
| 2,500 | 0% | 1.2s | 40,538 | OK |
| 3,000 | 0% | 1.3s | 49,038 | OK |
| 3,500 | 0% | 1.4s | 57,538 | OK |
| 4,000 | 0% | 1.5s | 66,038 | OK |
| 4,500 | 0% | 1.7s | 74,538 | OK |
| 5,000 | 0% | 1.8s | 83,038 | OK |
| 5,250 | 0% | 1.3s | 87,288 | OK |
| 5,500 | 0% | 1.4s | 91,538 | OK |
| 5,750 | 0% | 1.4s | 95,788 | OK |
| 6,000 | 0% | 1.5s | 100,038 | OK |
| 6,100 | 0% | 1.1s | 101,738 | OK |
| 6,200 | 0% | 1.1s | 103,438 | OK |
| 6,300 | 0% | 1.1s | 105,138 | OK |
| 6,400 | 0% | 1.1s | 106,838 | OK |
| 6,500 | 0% | 1.1s | 108,538 | OK |

## Key Findings

- **First Degradation**: 100 items

## 3-Model Comparison

| Model | Context Config | Actual on 5090 | Max Items | Max Tokens | Advantage |
|-------|---------------|----------------|-----------|------------|----------|
| Mistral 24B | 32k | 32k | 1,400 | 31,710 | Baseline |
| Gemma 3 27B | 131k | 24k (limited) | 1,500 | 21,928 | 1.1x items |
