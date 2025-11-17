# Sliding Window Technique for Context Extension

## Executive Summary

The **Sliding Window Technique** is an application-level solution to process documents that exceed your LLM's context limit. Instead of failing when a document is too large, we break it into overlapping chunks that fit within the model's limits, process each chunk separately, and merge the results.

**Key Benefit**: Process unlimited document size with any LLM, regardless of context limitations.

## Table of Contents

1. [The Problem](#the-problem)
2. [The Solution](#the-solution)
3. [How It Works](#how-it-works)
4. [Implementation](#implementation)
5. [Advanced Techniques](#advanced-techniques)
6. [Practical Applications](#practical-applications)
7. [Performance Considerations](#performance-considerations)
8. [Code Examples](#code-examples)

---

## The Problem

Your Mistral-Small-24B model has a **32,768 token context limit**, but real-world documents often exceed this:

- **IEC 62443 Complete**: ~300 pages ≈ 150,000 tokens
- **ETSI EN 303 645**: ~180 pages ≈ 90,000 tokens
- **Multiple Standards Combined**: 500,000+ tokens

### Without Sliding Window:
```
Document: [================================================] 150k tokens
Model:    [========]                                         32k limit
          ↑
          Only processes first 20% of document!
```

**Result**: 80% of your document is ignored! ❌

---

## The Solution

Break the document into **overlapping windows** that fit within the context limit:

```
Document: [================================================] 150k tokens

Window 1: [==========]....................................... 0-25k
Window 2: ........[==========]................................ 20k-45k
Window 3: ..................[==========]........................ 40k-65k
Window 4: ............................[==========]............. 60k-85k
Window 5: ......................................[==========]... 80k-105k
Window 6: ..............................................[=====] 100k-125k
Window 7: ......................................................[=] 120k-150k

         ↑ 5k overlap ensures no information is lost at boundaries
```

**Result**: 100% of document processed! ✅

---

## How It Works

### Step-by-Step Process

```python
# 1. SPLIT: Break document into chunks
chunks = split_with_overlap(document, window_size=20000, overlap=5000)

# 2. PROCESS: Query each chunk
for chunk in chunks:
    response = llm.query(chunk + question)
    results.append(response)

# 3. MERGE: Combine all responses
final_answer = merge_responses(results)
```

### Visual Flow Diagram

```
┌─────────────┐
│   Large     │
│  Document   │
│  (150k)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Split     │──► Window 1 (0-25k)
│    Into     │──► Window 2 (20-45k)
│   Windows   │──► Window 3 (40-65k)
└──────┬──────┘    ...
       │
       ▼
┌─────────────┐
│   Process   │◄── API Call 1
│    Each     │◄── API Call 2
│   Window    │◄── API Call 3
└──────┬──────┘    ...
       │
       ▼
┌─────────────┐
│   Merge     │
│   Results   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Final     │
│   Answer    │
└─────────────┘
```

---

## Implementation

### Basic Implementation (Python)

```python
class SlidingWindowProcessor:
    def __init__(self, max_context=28000, window_size=20000, overlap=5000):
        self.max_context = max_context
        self.window_size = window_size
        self.overlap = overlap
        self.stride = window_size - overlap

    def process_document(self, document, question):
        # Step 1: Create windows
        windows = self.create_windows(document)

        # Step 2: Process each window
        responses = []
        for i, window in enumerate(windows):
            prompt = f"Context:\n{window}\n\nQuestion: {question}"
            response = self.query_llm(prompt)

            if self.contains_answer(response):
                responses.append({
                    'window': i,
                    'content': response
                })

        # Step 3: Merge responses
        return self.merge_responses(responses, question)

    def create_windows(self, text):
        windows = []
        position = 0
        text_length = len(text)

        while position < text_length:
            end = min(position + self.window_size, text_length)
            windows.append(text[position:end])

            if end >= text_length:
                break

            position += self.stride

        return windows
```

### Configuration Examples

#### Conservative (High Accuracy)
```python
config = {
    'window_size': 15000,   # Smaller windows
    'overlap': 5000,        # Large overlap
    'temperature': 0.1      # Low creativity
}
```

#### Balanced (Recommended)
```python
config = {
    'window_size': 20000,   # Medium windows
    'overlap': 5000,        # Standard overlap
    'temperature': 0.3      # Balanced
}
```

#### Aggressive (Speed Priority)
```python
config = {
    'window_size': 25000,   # Large windows
    'overlap': 2000,        # Small overlap
    'temperature': 0.5      # More creative
}
```

---

## Advanced Techniques

### 1. Global Context + Local Windows (Gemma-Style)

Mimics how models with architectural sliding window attention work:

```python
def process_with_global_context(document, question):
    # Extract global summary (important facts)
    global_summary = extract_key_facts(document[:10000])

    # Process each window with global awareness
    for window in windows:
        prompt = f"""
        Global Context: {global_summary}
        Local Context: {window}
        Question: {question}
        """
        response = query_llm(prompt)
```

**Benefits**:
- Better coherence across windows
- Maintains document-level understanding
- Reduces context confusion

### 2. Smart Chunking (Semantic Boundaries)

Instead of fixed-size windows, break at semantic boundaries:

```python
def smart_chunk(document):
    chunks = []

    # Split by sections/chapters
    sections = document.split("Section")

    current_chunk = ""
    for section in sections:
        if len(current_chunk) + len(section) < window_size:
            current_chunk += section
        else:
            chunks.append(current_chunk)
            current_chunk = section

    return chunks
```

### 3. Hierarchical Processing

Process at multiple granularities:

```
Level 1: Full document summary (5k tokens)
    ↓
Level 2: Chapter summaries (10k tokens each)
    ↓
Level 3: Detailed sections (20k tokens each)
```

### 4. Answer Confidence Scoring

Track where answers come from:

```python
def process_with_confidence(windows, question):
    answers = []

    for window in windows:
        response = query_llm(window, question)
        confidence = calculate_confidence(response)

        answers.append({
            'response': response,
            'confidence': confidence,
            'window_id': window.id
        })

    # Use high-confidence answers
    best_answers = [a for a in answers if a['confidence'] > 0.8]
    return merge_answers(best_answers)
```

---

## Practical Applications

### For IEC 62443 Processing

```python
class IEC62443Processor:
    def __init__(self):
        self.processor = SlidingWindowProcessor(
            window_size=20000,  # ~40 pages per window
            overlap=5000        # ~10 pages overlap
        )

    def find_requirement(self, standard_text, requirement_id):
        """Find specific requirement like CR 2.11"""

        # Optimize: Start from likely location
        if "CR 2" in requirement_id:
            # CR 2.x usually in middle sections
            start_window = 2
        else:
            start_window = 0

        return self.processor.process_document(
            standard_text,
            f"Find and explain requirement {requirement_id}"
        )

    def compare_requirements(self, standards_dict):
        """Compare across multiple standards"""

        results = {}
        for standard_name, text in standards_dict.items():
            # Process each standard
            results[standard_name] = self.processor.process_document(
                text,
                "List all authentication requirements"
            )

        # Synthesize comparison
        return self.create_comparison_table(results)
```

### For Multi-Document RAG

```python
def multi_doc_rag(documents, question):
    """Process multiple large documents"""

    all_relevant_chunks = []

    # Step 1: Find relevant chunks from each document
    for doc in documents:
        windows = create_windows(doc)
        for window in windows:
            if is_relevant(window, question):
                all_relevant_chunks.append(window)

    # Step 2: Rerank by relevance
    ranked_chunks = rerank_chunks(all_relevant_chunks, question)

    # Step 3: Process top chunks
    top_chunks = ranked_chunks[:5]  # Top 5 most relevant

    # Step 4: Generate answer
    context = "\n---\n".join(top_chunks)
    return query_llm(context, question)
```

---

## Performance Considerations

### Time Complexity

| Document Size | Windows | API Calls | Time @ 2s/call |
|--------------|---------|-----------|----------------|
| 50k tokens   | 3       | 3         | 6 seconds      |
| 100k tokens  | 5       | 5         | 10 seconds     |
| 150k tokens  | 8       | 8         | 16 seconds     |
| 300k tokens  | 15      | 15        | 30 seconds     |

### Cost Analysis

```
Traditional: 1 call × 32k max = Limited capability
Sliding:     N calls × 20k each = Full capability

Example (150k document):
- Without sliding: Cannot process (too large)
- With sliding: 8 calls × $0.002 = $0.016 total
```

### Optimization Strategies

1. **Parallel Processing**:
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_process(windows):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(query_llm, w) for w in windows]
        return [f.result() for f in futures]
```

2. **Caching**:
```python
@lru_cache(maxsize=100)
def cached_query(window_hash, question):
    return query_llm(window, question)
```

3. **Early Stopping**:
```python
for window in windows:
    response = query_llm(window, question)
    if confidence(response) > 0.95:
        return response  # Stop if highly confident
```

---

## Code Examples

### Complete Working Example

```python
import requests
import hashlib
from typing import List, Dict

class ProductionSlidingWindow:
    """Production-ready sliding window implementation"""

    def __init__(self, api_url="http://localhost:8080/v1/chat/completions"):
        self.api_url = api_url
        self.cache = {}

    def process_large_document(self,
                              document: str,
                              question: str,
                              window_size: int = 20000,
                              overlap: int = 5000) -> Dict:
        """
        Process a document larger than context limit

        Args:
            document: The full document text
            question: Question to answer
            window_size: Size of each window in chars (≈ tokens/4)
            overlap: Overlap between windows

        Returns:
            Dict with answer, confidence, and metadata
        """

        # Create windows
        windows = self._create_windows(document, window_size, overlap)
        print(f"Document split into {len(windows)} windows")

        # Process each window
        responses = []
        for i, window in enumerate(windows):
            print(f"Processing window {i+1}/{len(windows)}...")

            # Check cache
            cache_key = self._get_cache_key(window, question)
            if cache_key in self.cache:
                response = self.cache[cache_key]
            else:
                response = self._query_window(window, question, i)
                self.cache[cache_key] = response

            if response['has_answer']:
                responses.append(response)

        # Merge responses
        if not responses:
            return {
                'answer': 'No relevant information found',
                'confidence': 0,
                'windows_checked': len(windows)
            }

        return self._merge_responses(responses, question)

    def _create_windows(self, text: str, window_size: int, overlap: int) -> List[str]:
        """Create overlapping windows from text"""
        windows = []
        stride = window_size - overlap

        for i in range(0, len(text), stride):
            window = text[i:i + window_size]
            windows.append(window)
            if i + window_size >= len(text):
                break

        return windows

    def _query_window(self, window: str, question: str, window_id: int) -> Dict:
        """Query a single window"""
        prompt = f"""
        Document section (Part {window_id + 1}):
        {window}

        Question: {question}

        If the answer is in this section, provide it with quotes.
        If not, respond with "NOT_IN_THIS_SECTION"
        """

        try:
            response = requests.post(self.api_url, json={
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.1,
                'max_tokens': 500
            }, timeout=30)

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']

                return {
                    'window_id': window_id,
                    'content': content,
                    'has_answer': 'NOT_IN_THIS_SECTION' not in content
                }
        except Exception as e:
            print(f"Error in window {window_id}: {e}")

        return {'window_id': window_id, 'content': '', 'has_answer': False}

    def _merge_responses(self, responses: List[Dict], question: str) -> Dict:
        """Merge multiple responses into final answer"""

        if len(responses) == 1:
            return {
                'answer': responses[0]['content'],
                'confidence': 0.9,
                'source_windows': [responses[0]['window_id']]
            }

        # Synthesize multiple responses
        all_content = '\n\n'.join([
            f"[From section {r['window_id']+1}]: {r['content']}"
            for r in responses
        ])

        synthesis_prompt = f"""
        Multiple sections contain relevant information:

        {all_content}

        Question: {question}

        Provide a comprehensive answer combining all relevant information.
        """

        try:
            response = requests.post(self.api_url, json={
                'messages': [{'role': 'user', 'content': synthesis_prompt}],
                'temperature': 0.2,
                'max_tokens': 1000
            }, timeout=30)

            if response.status_code == 200:
                final_answer = response.json()['choices'][0]['message']['content']

                return {
                    'answer': final_answer,
                    'confidence': 0.95,
                    'source_windows': [r['window_id'] for r in responses]
                }
        except Exception as e:
            print(f"Error in synthesis: {e}")

        # Fallback
        return {
            'answer': responses[0]['content'],
            'confidence': 0.7,
            'source_windows': [r['window_id'] for r in responses]
        }

    def _get_cache_key(self, window: str, question: str) -> str:
        """Generate cache key for window+question pair"""
        content = f"{window[:100]}...{question}"
        return hashlib.md5(content.encode()).hexdigest()


# Usage example
if __name__ == "__main__":
    processor = ProductionSlidingWindow()

    # Load your large document
    with open("iec_62443_complete.txt", "r") as f:
        document = f.read()  # 150k tokens

    # Process with sliding window
    result = processor.process_large_document(
        document,
        "What are all the requirements for secure remote access?",
        window_size=20000,
        overlap=5000
    )

    print(f"\nAnswer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Source windows: {result['source_windows']}")
```

---

## Integration with LightRAG

### Recommended Architecture

```python
class LightRAGWithSlidingWindow:
    """Integrate sliding window with LightRAG pipeline"""

    def __init__(self):
        self.sliding = ProductionSlidingWindow()
        self.lightrag = LightRAG()

    def process_query(self, query: str) -> str:
        # Step 1: Retrieve relevant documents
        documents = self.lightrag.retrieve(query, top_k=3)

        # Step 2: Check total size
        total_tokens = sum(doc.token_count for doc in documents)

        if total_tokens <= 28000:
            # Fits in context - process normally
            return self.lightrag.generate(documents, query)
        else:
            # Too large - use sliding window
            combined = "\n---\n".join([doc.content for doc in documents])
            result = self.sliding.process_large_document(
                combined,
                query,
                window_size=20000
            )
            return result['answer']
```

---

## Summary

### When to Use Sliding Window

✅ **Use when**:
- Documents exceed context limit (>32k tokens)
- Processing complete standards/regulations
- Comparing across multiple large documents
- Need 100% document coverage

❌ **Don't use when**:
- Document fits in context (<28k tokens)
- Speed is critical (adds latency)
- Only need specific sections (use targeted retrieval instead)

### Key Benefits

1. **Unlimited document size** - Process 100k, 500k, even 1M+ tokens
2. **100% coverage** - Never miss information due to context limits
3. **Works with any model** - No special architecture required
4. **Flexible configuration** - Adjust window/overlap for your needs

### Trade-offs

| Aspect | Direct Query | Sliding Window |
|--------|-------------|----------------|
| Max Size | 32k tokens | Unlimited |
| API Calls | 1 | Multiple (N) |
| Latency | 2-3 seconds | N × 2-3 seconds |
| Cost | Low | N × cost |
| Coverage | Partial | Complete |
| Complexity | Simple | Moderate |

---

## Next Steps

1. **Test with your documents**: Try the implementation with actual IEC 62443 text
2. **Optimize parameters**: Find best window_size/overlap for your use case
3. **Implement caching**: Reduce redundant API calls
4. **Add parallelization**: Speed up processing with concurrent requests
5. **Integrate with LightRAG**: Combine with your existing RAG pipeline

## Resources

- Implementation: `backend/tests/sliding_window_rag.py`
- Test results: `backend/tests/FINAL_TEST_SUMMARY.md`
- Context limits: `backend/tests/context_limit_results.md`

---

*Last Updated: 2025-11-16*
*For: GPT-OSS LightRAG Project*