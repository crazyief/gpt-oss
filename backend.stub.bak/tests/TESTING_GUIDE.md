# Mistral 24B Context Window Testing Guide

## Overview
This guide provides comprehensive instructions for testing the Mistral 24B model's context window capabilities for the GPT-OSS LightRAG project.

## Test Philosophy

The testing approach is based on several key insights:

1. **Token vs Character Counting**: Always measure in tokens, not characters, as the model processes tokens
2. **Position Sensitivity**: Transformer models exhibit primacy and recency biases
3. **Statistical Significance**: Single tests are insufficient; multiple runs reveal true performance
4. **Degradation Patterns**: Performance typically degrades non-linearly as context fills
5. **Real-world Relevance**: Tests should simulate actual RAG query patterns

## Quick Start

### Prerequisites
```bash
# Install test dependencies
pip install -r backend/tests/test_requirements.txt

# Ensure Mistral is running
curl http://localhost:8080/health
```

### Running Tests

#### Option 1: PowerShell Script (Windows)
```powershell
# Quick test (5-10 minutes)
.\run_context_test.ps1 -TestType quick

# Full test (2-3 hours)
.\run_context_test.ps1 -TestType full -InstallDeps

# Custom sizes
.\run_context_test.ps1 -TestType custom -CustomSizes 5000,10000,15000
```

#### Option 2: Direct Python Execution
```bash
cd backend/tests

# Quick test
python quick_context_test.py

# Custom sizes
python quick_context_test.py 1000 5000 10000

# Full comprehensive test
python mistral_context_test.py
```

## Test Types Explained

### 1. Quick Test (`quick_context_test.py`)
- **Duration**: 5-10 minutes
- **Purpose**: Rapid validation and sanity checking
- **Coverage**: 4 context sizes × 3 positions = 12 tests
- **Output**: Simple markdown report

Use when:
- Validating model is working
- Quick performance check after configuration changes
- Rapid iteration during development

### 2. Comprehensive Test (`mistral_context_test.py`)
- **Duration**: 2-3 hours
- **Purpose**: Statistical validation with confidence intervals
- **Coverage**: 8 sizes × 3 positions × 3 runs × 5 needles = 360 tests
- **Output**: Detailed report, visualizations, raw data CSV

Use when:
- Establishing baseline performance
- Comparing different models or configurations
- Production readiness assessment
- Academic or formal testing requirements

## Understanding the Results

### Key Metrics

1. **Accuracy**: Percentage of correct retrievals
   - >95%: Excellent, suitable for production
   - 90-95%: Good, may need context management
   - <90%: Poor, investigate issues

2. **Response Time**: Time to generate response
   - <5s: Excellent
   - 5-10s: Acceptable
   - >10s: May impact user experience

3. **Degradation Point**: Context size where accuracy drops below 95%
   - Critical for setting safe operational limits
   - Typically occurs at 50-70% of maximum context

4. **Position Effects**:
   - **Start bias**: Better recall at beginning (primacy effect)
   - **End bias**: Better recall at end (recency effect)
   - **Middle sag**: Reduced accuracy in middle positions

### Reading the Reports

#### Quick Test Report
```markdown
| Size | Position | Index | Correct | Time(s) |
|------|----------|-------|---------|----------|
| 1,000 | start | 1 | ✓ | 0.8 |
```
- Simple pass/fail for each test
- Overall accuracy percentage
- Identifies degradation point if found

#### Comprehensive Test Report
Includes:
- Statistical confidence intervals
- Performance degradation curves
- Position sensitivity analysis
- Failed retrieval examples
- Recommendations based on findings

### Visualizations

The comprehensive test generates four key plots:

1. **Accuracy vs Context Size**: Shows degradation curve
2. **Response Time vs Context Size**: Performance scaling
3. **Position Analysis**: Compares start/middle/end performance
4. **Accuracy Heatmap**: Visual representation of all results

## Advanced Testing Scenarios

### 1. Stress Testing
Test extreme conditions:
```python
# Test near maximum context
python quick_context_test.py 20000 25000 30000
```

### 2. Document-Specific Testing
Simulate your actual documents:
```python
# Modify generate_haystack() to use your document patterns
def generate_haystack(num_items):
    # Use IEC 62443 clause format
    items = []
    for i in range(1, num_items + 1):
        items.append(f"Clause {i}.{i%10}.{i%5}: Security requirement...")
    return items
```

### 3. Multi-Needle Testing
Test multiple queries in single context:
```python
# Modify test to query multiple indices
query_indices = [1, 100, 500, 1000, 5000]
```

### 4. Semantic Testing
Test understanding, not just retrieval:
```python
# Instead of "What is index 1?"
prompt = "What color is mentioned in index 1?"
```

## Troubleshooting

### Common Issues

1. **"LLM service not reachable"**
   - Ensure Docker containers are running: `docker-compose ps`
   - Check GPU is available: `nvidia-smi`
   - Verify port 8080: `netstat -an | findstr 8080`

2. **"Out of Memory" errors**
   - Reduce context size in tests
   - Adjust GPU layers in docker-compose.yml: `-ngl 50`
   - Monitor GPU memory: `nvidia-smi -l 1`

3. **Inconsistent results**
   - Ensure temperature=0 for deterministic output
   - Check for background GPU processes
   - Verify no other applications using GPU memory

4. **Very slow responses**
   - Check GPU utilization: `nvidia-smi`
   - Ensure model is using GPU, not CPU
   - Consider reducing batch size or context length

### Debug Mode

Enable detailed logging:
```python
# In test scripts, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Optimization Guidelines

### For Better Accuracy
1. Keep critical information at start or end of context
2. Use clear, unique identifiers (index formatting)
3. Avoid ambiguous or similar-looking content
4. Maintain consistent formatting throughout

### For Better Performance
1. Batch similar-length queries together
2. Pre-warm model with dummy query
3. Use connection pooling (requests.Session)
4. Implement caching for repeated queries

### For Production Use
Based on test results, implement:

1. **Context Windowing**: Limit context to 80% of degradation point
2. **Chunking Strategy**: Split large documents when exceeding limits
3. **Position Strategy**: Place important info at start/end
4. **Monitoring**: Track accuracy and response time metrics
5. **Fallback**: Have alternative when context too large

## Interpreting Results for GPT-OSS

### Recommended Settings
Based on typical results for Mistral 24B:

```python
# Recommended configuration
MAX_CONTEXT_TOKENS = 12000  # Conservative limit
CHUNK_SIZE = 2000  # Per document chunk
OVERLAP = 200  # Chunk overlap for continuity
NEEDLE_POSITION = "end"  # Where to place queries
```

### RAG Integration
Use test results to configure LightRAG:

```python
# In lightrag_service.py
class LightRAGConfig:
    def __init__(self, test_results):
        # Set limits based on test degradation point
        self.max_context = int(test_results['degradation_point'] * 0.8)

        # Configure retrieval based on position sensitivity
        if test_results['end_accuracy'] > test_results['middle_accuracy']:
            self.query_position = 'end'

        # Set timeout based on response times
        self.timeout = test_results['p95_response_time'] * 1.5
```

## Next Steps

After testing:

1. **Document findings** in PROJECT_STATUS.md
2. **Update configuration** based on results
3. **Implement safeguards** for identified limitations
4. **Create monitoring** for production metrics
5. **Schedule periodic retesting** after updates

## Sample Test Session

Here's what a typical test session looks like:

```powershell
# Day 1: Initial validation
.\run_context_test.ps1 -TestType quick -InstallDeps

# Review results, adjust configuration

# Day 2: Comprehensive baseline
.\run_context_test.ps1 -TestType full

# Analyze results, identify limits

# Day 3: Production configuration testing
.\run_context_test.ps1 -TestType custom -CustomSizes 8000,10000,12000

# Finalize configuration based on sweet spot
```

## Reporting Issues

When reporting test failures or unexpected results:

1. Include full error messages
2. Attach test report markdown file
3. Provide system specifications:
   - GPU model and VRAM
   - Docker compose configuration
   - Model quantization level
4. Share reproduction steps

## References

- [Anthropic's Context Window Research](https://www.anthropic.com/research)
- [LangChain Context Testing](https://python.langchain.com/docs/guides/evaluation)
- [HuggingFace LLM Evaluation](https://huggingface.co/docs/evaluate)
- [Mistral AI Documentation](https://docs.mistral.ai/)

---

*Last updated: 2024-11-16*
*For GPT-OSS LightRAG Project*