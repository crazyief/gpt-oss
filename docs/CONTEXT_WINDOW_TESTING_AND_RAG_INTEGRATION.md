# Context Window Testing & RAG Integration Strategy

**Document Version**: 2.0
**Last Updated**: 2025-11-19
**Changelog**:
- v2.0: Added Failure Mode Handling, Production Monitoring, and Validation Framework sections
- v1.0: Initial version with 3-phase methodology and RAG integration strategies
**Purpose**: Reference guide for context window validation methodology and RAG engine integration strategy for GPT-OSS

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Test Findings](#current-test-findings)
3. [3-Phase Adaptive Zone Mapping Methodology](#3-phase-adaptive-zone-mapping-methodology)
4. [RAG Integration Strategies](#rag-integration-strategies)
5. [Failure Mode Handling & Fallback Cascade](#failure-mode-handling--fallback-cascade)
6. [Production Monitoring & Observability](#production-monitoring--observability)
7. [Validation Framework](#validation-framework)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Production Configuration](#production-configuration)
10. [Appendix: Test Scripts](#appendix-test-scripts)

---

## Executive Summary

### The Problem

Local LLMs exhibit **systematic context window bugs** at specific token counts, causing:
- **Middle-position failures**: Queries return LAST item instead of MIDDLE item (0% accuracy)
- **Unpredictable danger zones**: Bug appears at specific item counts (e.g., 500, 750, 1200)
- **Silent failures**: No errors thrown - just wrong answers returned

### Impact on GPT-OSS RAG System

**Without mitigation**:
```
User: "Find IEC 62443-4-2 CR 2.11 requirements"
→ LightRAG retrieves 750 chunks (danger zone)
→ LLM returns LAST chunk instead of correct middle section
→ User gets WRONG compliance answer ❌ CRITICAL for security standards
```

**With zone-aware RAG**:
```
User: "Find IEC 62443-4-2 CR 2.11 requirements"
→ LightRAG retrieves 750 chunks
→ System detects danger zone, auto-pads to 754 items (safe zone)
→ LLM processes correctly
→ User gets CORRECT answer with proper citations ✅
```

### Solution Overview

1. **Map all safe/danger zones** using 3-phase adaptive testing (one-time, 5-6 hours)
2. **Generate production config** with validated safe zones
3. **Integrate with LightRAG** to auto-avoid danger zones
4. **Enable large document handling** via multi-query batching

---

## Current Test Findings

### Model Comparison (as of 2025-11-19)

| Model | Configured Context | Actual Usable | Utilization | Status |
|-------|-------------------|---------------|-------------|--------|
| **Magistral-small-2506** | 32k | 31,920 tokens | 99.75% | ✅ Gold Standard |
| **GPT-OSS 20B** | 32k | 31,080 tokens | 97% | ✅ Production Ready |
| **Mistral 24B Q6_K** | 32k | 27,960 tokens | 87% | ⚠️ **Systematic Bugs** |
| **Gemma 3 27B** | 24k | 11,807 tokens | 49% | ❌ Hard Limit (HTTP 400) |

### Mistral Q6_K Bug Pattern (Verified)

**Systematic Failures** (0% middle accuracy, 100% reproducible):

| Item Count | First | Middle | Last | Status | Context |
|-----------|-------|--------|------|--------|---------|
| 100 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |
| 250 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |
| **500** | ✅ 100% | ❌ **0%** | ✅ 100% | **BUG** | Middle returns LAST |
| **750** | ✅ 100% | ❌ **0%** | ✅ 100% | **BUG** | Middle returns LAST |
| 1000 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |
| 1100 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |
| **1200** | ✅ 100% | ❌ **0%** | ✅ 100% | **BUG** | Middle returns LAST |
| 1250 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |
| 1300-1400 | ✅ 100% | ✅ 100% | ✅ 100% | Safe | Validated |

**Known Safe Zones**: 100, 250, 1000, 1100, 1250-1400 items
**Known Danger Zones**: 500, 750, 1200 items
**Unknown Zones**: Everything between (needs Phase 1-3 testing)

### Gemma 27B Hard Limit

**Discovery**: HTTP 400 error at 600 items (not accuracy degradation)

| Item Count | Tokens | Status | Notes |
|-----------|--------|--------|-------|
| 250 | 5,367 | ✅ Works | 100% accuracy |
| 550 | 11,807 | ✅ **Last Working** | Hard limit |
| 600 | ~12,900 | ❌ HTTP 400 | Context limit exceeded |

**Root Cause**:
```
llama_context: n_ctx       = 24064  ✅ (Configured 24k)
llama_context: n_ctx_seq   = 12032  ❌ (Actual limit only 12k)
```

llama.cpp auto-sets `n_ctx_seq = n_ctx / 2` for Sliding Window Attention (SWA) models.

**Recommendation**: **DO NOT USE Gemma** for production RAG (only 25 pages of IEC 62443 capacity)

---

## 3-Phase Adaptive Zone Mapping Methodology

### Overview

**Goal**: Efficiently map ALL safe and danger zones with statistical confidence

**Why Not Fixed Increments?**
- Testing every 25 items = 780 queries, 6-8 hours
- Most of those queries are redundant (testing middle of safe zones)
- No statistical validation of boundaries

**Adaptive Approach**:
- Phase 1: Coarse discovery (find transitions)
- Phase 2: Binary search (pinpoint boundaries)
- Phase 3: Production validation (confirm stability)
- **Total**: ~700 queries, 5-6 hours, higher information gain

---

### Phase 1: Coarse Discovery

**Objective**: Survey the entire range to identify transitions

**Method**:
```python
test_points = range(100, 1401, 50)  # Every 50 items
runs_per_point = 3
positions_per_run = 3  # first, middle, last

Total queries: 27 points × 3 runs × 3 positions = 243 queries
Duration: ~2 hours (15s rest between runs)
```

**Sample Output**:
```
100 items  → 100% middle (3/3 runs) ✅
150 items  → 100% middle (3/3 runs) ✅
...
450 items  → 100% middle (3/3 runs) ✅
500 items  → 0% middle (0/3 runs) ❌  ⚠️ TRANSITION DETECTED
550 items  → 0% middle (0/3 runs) ❌
600 items  → 100% middle (3/3 runs) ✅  ⚠️ TRANSITION DETECTED
```

**Result**: List of transition pairs (e.g., "450→500" and "550→600")

**Confidence Level**:
- 0% or 100% → High confidence (3 runs sufficient)
- 33-67% → Low confidence (needs more runs in Phase 3)

---

### Phase 2: Binary Search Refinement

**Objective**: Find exact boundaries to ±5 item precision

**Method**:
```python
for each transition in Phase 1:
    binary_search(low, high, precision=5)
    runs_per_test = 5  # Higher confidence

Example transition: 500 (0%) ← → 600 (100%)

Test 550 → 0% (bug still present)
Test 575 → 100% (safe)
Test 562 → 100%
Test 556 → 0%
Test 559 → 100% ✅ BOUNDARY FOUND (±3 items)

Total queries: ~10-15 per transition × 5 runs × 3 positions = ~200-250 queries
Duration: ~2-3 hours
```

**Result**: Precise boundary coordinates
- Danger zone: 500-558 items
- Safe zone: 559-1199 items

**Confidence Level**: 80% (5 runs)

---

### Phase 3: Production Validation

**Objective**: Confirm boundaries are stable with 95% confidence

**Method**:
```python
for each boundary found in Phase 2:
    test_range = boundary ± 10 items
    runs_per_test = 10  # Statistical confidence

Example boundary at 559:
Test 549, 554, 559, 564, 569 (5 points × 10 runs × 3 positions)

Expected results:
549 → 0/10 middle (0%) ❌ DANGER CONFIRMED
554 → 0/10 middle (0%) ❌ DANGER CONFIRMED
559 → 10/10 middle (100%) ✅ SAFE CONFIRMED
564 → 10/10 middle (100%) ✅ SAFE CONFIRMED

Total queries: ~20 boundaries × 10 runs × 3 positions = ~200 queries
Duration: ~1 hour
```

**Result**: Production-validated configuration file

**Confidence Level**: 95% (10 runs)

---

### Automated Output Files

**1. Test Data (JSON)**
```json
// mistral_zone_map_20251119_140000.json
{
  "phase1_results": [...],
  "phase2_boundaries": [...],
  "phase3_validation": [...],
  "safe_zones": [
    {"start": 100, "end": 497, "confidence": 0.95},
    {"start": 559, "end": 753, "confidence": 0.95}
  ],
  "danger_zones": [
    {"start": 498, "end": 558, "confidence": 0.95},
    {"start": 754, "end": 1199, "confidence": 0.95}
  ]
}
```

**2. Production Config (Python)**
```python
# mistral_safe_zones_config.py
SAFE_ZONES = [
    (100, 497),
    (559, 753),
    (1201, 1400)
]

DANGER_ZONES = [
    (498, 558),
    (754, 1200)
]

def is_danger_zone(item_count: int) -> bool:
    """Check if item count falls in danger zone"""
    return any(start <= item_count <= end
               for start, end in DANGER_ZONES)

def apply_safe_padding(item_count: int) -> int:
    """Auto-pad to next safe zone if in danger"""
    if not is_danger_zone(item_count):
        return item_count

    # Find next safe zone
    for start, end in SAFE_ZONES:
        if item_count < start:
            return start

    # If beyond all safe zones, use largest safe zone
    return SAFE_ZONES[-1][1]
```

**3. Analysis Report (Markdown)**
```markdown
# Mistral Q6_K Zone Map Report
Generated: 2025-11-19 14:00:00

## Summary
- Total tests: 643 queries over 5.5 hours
- Safe zones: 3 ranges covering 62% of 100-1400 items
- Danger zones: 2 ranges covering 38%

## Phase 1 Discoveries
- Transition at ~500 items (danger starts)
- Transition at ~559 items (safe resumes)
...

## Recommended Production Settings
- Target chunk size: 400 items (middle of 100-497 safe zone)
- Fallback: 650 items (middle of 559-753 safe zone)
- Maximum: 1300 items (middle of 1201-1400 safe zone)
```

---

## RAG Integration Strategies

### Strategy 1: Dynamic Context Padding ⭐ (Recommended First Step)

**Concept**: Auto-avoid danger zones when building LLM context

**Implementation**:
```python
# backend/app/services/lightrag_service.py
from backend.tests.mistral_safe_zones_config import (
    is_danger_zone,
    apply_safe_padding,
    SAFE_ZONES
)

class LightRAGService:
    def query(self, project_id: str, question: str, mode: str = "hybrid"):
        # Step 1: LightRAG retrieves relevant chunks
        retrieved_chunks = self.lightrag.retrieve(
            question,
            top_k=self.config.default_chunk_count
        )

        # Step 2: Add conversation history
        conversation_history = self._get_conversation_history(project_id)
        total_items = len(retrieved_chunks) + len(conversation_history)

        # Step 3: Check for danger zone
        if is_danger_zone(total_items):
            logger.warning(
                f"Danger zone detected: {total_items} items. "
                f"Adjusting to safe zone..."
            )

            safe_count = apply_safe_padding(total_items)

            # Option A: Reduce chunks to stay in previous safe zone
            if safe_count < total_items:
                max_chunks = safe_count - len(conversation_history)
                retrieved_chunks = retrieved_chunks[:max_chunks]
                logger.info(
                    f"Reduced chunks: {total_items} → {safe_count} items"
                )

            # Option B: Add filler to push into next safe zone
            # (Less recommended - wastes tokens)

        # Step 4: Build final context
        context = self._build_context(retrieved_chunks, conversation_history)

        # Step 5: Query LLM with safe context
        response = self.llm_service.generate(
            prompt=question,
            context=context
        )

        return response
```

**Pros**:
- ✅ Immediate fix - deploy today with known zones (100, 250, 1000-1400)
- ✅ No model changes required
- ✅ Transparent to users
- ✅ Minimal performance impact (slight chunk reduction)

**Cons**:
- ❌ May reduce context slightly (e.g., 750 → 700 items)
- ❌ Requires zone mapping data

**Best For**: Quick deployment, immediate bug mitigation

---

### Strategy 2: Intelligent Chunk Sizing

**Concept**: Configure LightRAG's retrieval to target safe zones

**Implementation**:
```python
class LightRAGConfig:
    def __init__(self):
        # Read validated safe zones
        self.safe_zones = SAFE_ZONES

        # Pick largest safe zone as default target
        self.target_chunk_count = 1300  # Middle of 1201-1400 safe zone
        self.min_chunk_count = 250      # Middle of 100-497 safe zone
        self.max_chunk_count = 1400     # Upper bound

class LightRAGService:
    def __init__(self):
        self.config = LightRAGConfig()

        self.lightrag = LightRAG(
            working_dir=self.rag_dir,
            llm_model_func=self.llm_service.generate,
            # Configure retrieval to stay in safe zones
            default_top_k=self.config.target_chunk_count
        )

    def query(self, project_id: str, question: str):
        # LightRAG automatically retrieves safe chunk count
        # No runtime checks needed - designed for safety
        response = self.lightrag.query(question, mode="hybrid")
        return response
```

**Pros**:
- ✅ Architecture-level solution (no runtime overhead)
- ✅ Maximizes safe context usage
- ✅ Cleaner code (no per-query checks)

**Cons**:
- ❌ Requires understanding LightRAG internals
- ❌ Less flexible for dynamic adjustment

**Best For**: Long-term architecture, system redesign

---

### Strategy 3: Hybrid Multi-Query for Large Documents

**Concept**: Split large documents into safe batches, merge results

**Implementation**:
```python
class LightRAGService:
    def query_large_document(
        self,
        project_id: str,
        question: str,
        max_chunk_size: int = 1300  # Largest safe zone
    ):
        # Step 1: Retrieve ALL relevant chunks
        all_chunks = self.lightrag.retrieve(question, top_k=5000)

        # Step 2: Check if splitting needed
        if len(all_chunks) <= max_chunk_size:
            # Small document - single query
            return self.query(project_id, question)

        # Step 3: Split into safe batches
        batches = self._split_into_safe_batches(
            all_chunks,
            batch_size=max_chunk_size
        )

        logger.info(
            f"Large document query: {len(all_chunks)} chunks "
            f"split into {len(batches)} batches"
        )

        # Step 4: Query each batch
        batch_results = []
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)}...")

            result = self.lightrag.query_batch(
                question=question,
                chunks=batch,
                batch_id=i
            )

            batch_results.append(result)

        # Step 5: Merge results with citation tracking
        merged_result = self._merge_results_with_citations(
            batch_results,
            question
        )

        return merged_result

    def _split_into_safe_batches(self, chunks, batch_size):
        """Split chunks into safe-sized batches"""
        return [
            chunks[i:i + batch_size]
            for i in range(0, len(chunks), batch_size)
        ]

    def _merge_results_with_citations(self, batch_results, question):
        """Merge multiple batch results, preserving citations"""
        # Strategy A: Concatenate all answers with batch labels
        merged_answer = "\n\n".join([
            f"**Source Batch {i+1}**:\n{result['answer']}"
            for i, result in enumerate(batch_results)
        ])

        # Strategy B: Re-rank and synthesize
        # Use LLM to synthesize final answer from batch results
        synthesis_prompt = f"""
Question: {question}

I have answers from {len(batch_results)} different document sections:

{merged_answer}

Synthesize a comprehensive answer, citing specific sections.
"""

        final_answer = self.llm_service.generate(synthesis_prompt)

        # Merge all citations
        all_citations = []
        for result in batch_results:
            all_citations.extend(result.get('citations', []))

        return {
            'answer': final_answer,
            'citations': all_citations,
            'batches_processed': len(batch_results)
        }
```

**Pros**:
- ✅ Handles unlimited document sizes (300+ page IEC 62443)
- ✅ Maintains accuracy across all chunks
- ✅ Preserves source citations
- ✅ No single-query context limits

**Cons**:
- ❌ Multiple LLM calls = slower (but accurate)
- ❌ More complex citation merging
- ❌ Higher token costs

**Best For**: Large standards documents (IEC 62443, EN 18031)

**Example Use Case**:
```
User: "Find all access control requirements in IEC 62443"
→ LightRAG retrieves 2500 relevant chunks
→ Split into 2 batches: [1-1300], [1301-2500]
→ Batch 1: Query chunks 1-1300 (safe zone)
→ Batch 2: Query chunks 1301-2500 (safe zone)
→ Merge results: "Access control requirements found in:
   - Section 4.2 (Batch 1, Page 45)
   - Section 7.3 (Batch 2, Page 198)
   ..."
```

---

### Strategy 4: Attention Injection (Advanced)

**Concept**: Add prompt markers to force LLM attention to middle positions

**Implementation**:
```python
class LightRAGService:
    def query_with_attention_markers(self, chunks, question):
        # Insert attention markers at danger positions
        marked_chunks = []

        for i, chunk in enumerate(chunks):
            position = "first" if i == 0 else "last" if i == len(chunks)-1 else "middle"

            if position == "middle" and is_danger_zone(len(chunks)):
                # Add attention marker for middle chunks in danger zone
                marked_chunk = f"""
⚠️ CRITICAL: This is the MIDDLE section - PAY ATTENTION ⚠️
Position: {i}/{len(chunks)}

{chunk}

⚠️ Remember to check this MIDDLE section for the answer ⚠️
"""
            else:
                marked_chunk = chunk

            marked_chunks.append(marked_chunk)

        return self.llm_service.generate(question, marked_chunks)
```

**Pros**:
- ✅ May improve accuracy even in danger zones
- ✅ No chunk reduction needed
- ✅ Simple to implement

**Cons**:
- ❌ Not guaranteed to work (LLM still might ignore)
- ❌ Wastes tokens on markers
- ❌ Hacky solution

**Best For**: Experimental mitigation, not production

---

## Failure Mode Handling & Fallback Cascade

### Overview

**Critical Principle**: Never return wrong answers. If all strategies fail, the system MUST refuse to answer.

### Failure Detection Mechanisms

#### 1. Confidence Scoring
```python
class ConfidenceEvaluator:
    def __init__(self):
        self.min_confidence = 0.85  # 85% threshold for production

    def calculate_confidence(self, response, context):
        """Calculate confidence score for LLM response"""
        scores = {
            'citation_present': self._has_citations(response),
            'context_coherence': self._check_coherence(response, context),
            'position_alignment': self._verify_position(response, context),
            'answer_completeness': self._check_completeness(response)
        }

        # Weighted average
        weights = {
            'citation_present': 0.3,
            'context_coherence': 0.3,
            'position_alignment': 0.25,
            'answer_completeness': 0.15
        }

        confidence = sum(scores[k] * weights[k] for k in scores.keys())
        return confidence

    def _verify_position(self, response, context):
        """Check if response matches expected position in context"""
        # Extract position markers from response
        # Compare with known context positions
        # Return 1.0 if correct, 0.0 if wrong position detected
        pass
```

#### 2. Dead Zone Detection at Runtime
```python
class RuntimeZoneDetector:
    def __init__(self):
        self.suspect_zones = []
        self.failure_history = []

    def detect_failure(self, context_size, response, expected):
        """Detect potential dead zone failure"""
        # Check if in known danger zone
        if is_danger_zone(context_size):
            self.failure_history.append({
                'size': context_size,
                'timestamp': datetime.now(),
                'confidence': 0.0
            })
            return True

        # Check response quality
        confidence = self._calculate_confidence(response, expected)
        if confidence < 0.7:
            # Potential new danger zone discovered
            self._mark_suspect_zone(context_size)
            return True

        return False

    def _mark_suspect_zone(self, size):
        """Flag a new potential danger zone"""
        logger.warning(
            f"⚠️ SUSPECT ZONE DETECTED: {size} items "
            f"(not in known danger zones but low confidence)"
        )
        self.suspect_zones.append({
            'size': size,
            'detected_at': datetime.now(),
            'occurrences': 1
        })
```

### Fallback Cascade Strategy

**4-Level Cascade** (Primary → Emergency):

```python
class FallbackCascade:
    """Automatic fallback through increasingly conservative strategies"""

    def __init__(self):
        self.strategies = [
            ('intelligent_chunking', self._strategy_intelligent_chunking),
            ('multi_query', self._strategy_multi_query),
            ('dynamic_padding', self._strategy_dynamic_padding),
            ('refuse_answer', self._strategy_refuse)
        ]
        self.max_latency = 25  # seconds (P90 target)

    def query(self, project_id, question, context):
        """Execute fallback cascade until success or exhaustion"""
        start_time = time.time()

        for strategy_name, strategy_func in self.strategies:
            # Check latency budget
            elapsed = time.time() - start_time
            if elapsed > self.max_latency:
                logger.error(f"⏱️ Latency budget exceeded: {elapsed:.2f}s")
                return self._strategy_refuse(
                    reason="Timeout - unable to answer within latency budget"
                )

            logger.info(f"Attempting strategy: {strategy_name}")

            try:
                result = strategy_func(project_id, question, context)

                # Validate result
                confidence = self._evaluate_confidence(result)

                if confidence >= 0.85:
                    logger.info(
                        f"✅ Success with {strategy_name} "
                        f"(confidence: {confidence:.2%})"
                    )
                    return result
                else:
                    logger.warning(
                        f"⚠️ {strategy_name} failed "
                        f"(confidence: {confidence:.2%}), trying next strategy"
                    )

            except Exception as e:
                logger.error(f"❌ {strategy_name} error: {e}, trying next strategy")
                continue

        # All strategies failed
        return self._strategy_refuse(reason="All strategies failed validation")

    def _strategy_intelligent_chunking(self, project_id, question, context):
        """Level 1: Fast, safe zone targeting"""
        # Target largest safe zone (1300 items)
        chunks = self._retrieve_chunks(question, max_count=1300)

        if is_danger_zone(len(chunks)):
            raise ValueError(f"Danger zone detected: {len(chunks)} items")

        return self._query_llm(chunks, question)

    def _strategy_multi_query(self, project_id, question, context):
        """Level 2: Split into multiple safe queries"""
        all_chunks = self._retrieve_chunks(question, max_count=5000)

        # Split into 1300-item batches (largest safe zone)
        batches = [all_chunks[i:i+1300]
                   for i in range(0, len(all_chunks), 1300)]

        results = []
        for batch in batches:
            result = self._query_llm(batch, question)
            results.append(result)

        return self._merge_results(results)

    def _strategy_dynamic_padding(self, project_id, question, context):
        """Level 3: Aggressive padding to avoid all danger zones"""
        chunks = self._retrieve_chunks(question, max_count=5000)

        # Apply safe padding
        safe_count = apply_safe_padding(len(chunks))

        if safe_count < len(chunks):
            # Reduce to safe count
            chunks = chunks[:safe_count]
        elif safe_count > len(chunks):
            # Add neutral filler to push past danger zone
            chunks = self._add_filler(chunks, target_count=safe_count)

        return self._query_llm(chunks, question)

    def _strategy_refuse(self, reason="Insufficient data quality"):
        """Level 4: Refuse to answer (safety measure)"""
        logger.critical(f"🚨 REFUSING TO ANSWER: {reason}")

        return {
            'answer': None,
            'error': 'UNABLE_TO_ANSWER',
            'reason': reason,
            'suggestion': (
                "I cannot provide a reliable answer based on the available data. "
                "This may be due to context window limitations. "
                "Please try:\n"
                "1. Narrowing your question to a specific section\n"
                "2. Breaking your query into smaller parts\n"
                "3. Asking about a specific document or chapter"
            ),
            'citations': []
        }
```

### Failure Mode Matrix

| Failure Mode | Detection | Fallback Action | User Impact |
|--------------|-----------|-----------------|-------------|
| **Known Danger Zone Hit** | Pre-query zone check | Level 1 → Level 2 (multi-query) | Transparent (slight latency) |
| **Low Confidence Response** | Post-query confidence scoring | Retry with Level 2/3 | Transparent (<25s) |
| **Suspect New Danger Zone** | Runtime anomaly detection | Log + Level 3 (padding) | Logged for future mapping |
| **All Strategies Failed** | Exhausted cascade | Level 4 (refuse) | User notified with suggestions |
| **Latency Budget Exceeded** | Timer check | Level 4 (refuse) | User notified with timeout |
| **LLM Service Down** | Exception handling | Level 4 (refuse) | User notified with service status |

### Example Execution Flow

```
User Query: "Find IEC 62443-4-2 CR 2.11"

1. Retrieve chunks: 750 items
2. Check danger zone: TRUE (750 in known danger zone)
3. Skip Level 1 (would fail)
4. Execute Level 2 (Multi-Query):
   - Split into [1-750] → single batch (below 1300 threshold)
   - Wait, 750 is danger zone!
   - Split into [1-400], [401-750] (two safe batches)
   - Query each batch independently
   - Merge results
5. Calculate confidence: 0.92 ✅
6. Return merged result with citations

Total time: 18.5s (within 25s budget)
```

---

## Production Monitoring & Observability

### Overview

**Goal**: Real-time visibility into RAG system health, danger zone usage, and retrieval accuracy.

### Key Metrics Dashboard

#### 1. Core Performance Metrics
```python
class RAGMetrics:
    """Prometheus-compatible metrics for production monitoring"""

    def __init__(self):
        # Latency metrics
        self.query_latency = Histogram(
            'rag_query_latency_seconds',
            'RAG query latency',
            buckets=[1, 5, 10, 15, 20, 25, 30, 40, 50]
        )

        # Zone usage metrics
        self.zone_hits = Counter(
            'rag_zone_hits_total',
            'Zone hit counts',
            ['zone_type']  # safe, danger, suspect
        )

        # Confidence metrics
        self.confidence_scores = Histogram(
            'rag_confidence_score',
            'Response confidence scores',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
        )

        # Strategy usage
        self.strategy_usage = Counter(
            'rag_strategy_used_total',
            'Fallback strategy usage',
            ['strategy']  # intelligent_chunking, multi_query, padding, refuse
        )

        # Citation accuracy
        self.citation_accuracy = Gauge(
            'rag_citation_accuracy',
            'Citation validation accuracy'
        )

    def record_query(self, duration, zone_type, confidence, strategy):
        """Record query metrics"""
        self.query_latency.observe(duration)
        self.zone_hits.labels(zone_type=zone_type).inc()
        self.confidence_scores.observe(confidence)
        self.strategy_usage.labels(strategy=strategy).inc()
```

#### 2. Alert Thresholds
```yaml
# prometheus/alerts.yml
alerts:
  - name: HighDangerZoneHitRate
    expr: rate(rag_zone_hits_total{zone_type="danger"}[5m]) > 0.1
    severity: WARNING
    description: >
      Danger zone hit rate exceeds 10% (5min window).
      May indicate inadequate chunk sizing or new danger zones.

  - name: LowCitationAccuracy
    expr: rag_citation_accuracy < 0.95
    severity: CRITICAL
    description: >
      Citation accuracy below 95% threshold.
      CRITICAL: May be returning incorrect compliance information.

  - name: HighRefusalRate
    expr: rate(rag_strategy_used_total{strategy="refuse"}[10m]) > 0.01
    severity: WARNING
    description: >
      System refusing to answer >1% of queries.
      Check zone mapping and LLM service health.

  - name: LatencyBudgetExceeded
    expr: histogram_quantile(0.90, rag_query_latency_seconds) > 25
    severity: WARNING
    description: >
      P90 latency exceeds 25s target.
      Review strategy performance and consider optimization.

  - name: SuspectZoneDetected
    expr: rate(rag_zone_hits_total{zone_type="suspect"}[1h]) > 0
    severity: INFO
    description: >
      New suspect danger zones detected.
      Schedule zone remapping to validate.
```

### Real-Time Monitoring Implementation

```python
class ProductionMonitor:
    """Real-time monitoring and alerting for RAG system"""

    def __init__(self):
        self.metrics = RAGMetrics()
        self.alert_manager = AlertManager()
        self.golden_dataset = self._load_golden_dataset()

    def monitor_query(self, query_func):
        """Decorator to monitor query execution"""
        @wraps(query_func)
        def wrapper(project_id, question, *args, **kwargs):
            start_time = time.time()

            try:
                # Execute query
                result = query_func(project_id, question, *args, **kwargs)

                # Calculate metrics
                duration = time.time() - start_time
                zone_type = self._determine_zone_type(result.get('context_size'))
                confidence = result.get('confidence', 0.0)
                strategy = result.get('strategy_used', 'unknown')

                # Record metrics
                self.metrics.record_query(
                    duration=duration,
                    zone_type=zone_type,
                    confidence=confidence,
                    strategy=strategy
                )

                # Check alerts
                self._check_alerts(duration, zone_type, confidence, strategy)

                return result

            except Exception as e:
                logger.error(f"Query failed: {e}")
                self.metrics.strategy_usage.labels(strategy='error').inc()
                raise

        return wrapper

    def _check_alerts(self, duration, zone_type, confidence, strategy):
        """Real-time alert checking"""
        if zone_type == 'danger':
            self.alert_manager.notify(
                severity='WARNING',
                message=f"Danger zone hit (confidence: {confidence:.2%})"
            )

        if confidence < 0.85:
            self.alert_manager.notify(
                severity='WARNING',
                message=f"Low confidence response: {confidence:.2%}"
            )

        if duration > 25:
            self.alert_manager.notify(
                severity='WARNING',
                message=f"Latency budget exceeded: {duration:.2f}s"
            )

        if strategy == 'refuse':
            self.alert_manager.notify(
                severity='CRITICAL',
                message="System refused to answer query"
            )
```

### Logging Strategy

```python
import structlog

logger = structlog.get_logger()

# Structured logging for all RAG operations
logger.info(
    "rag_query_executed",
    project_id=project_id,
    question_length=len(question),
    retrieved_chunks=len(chunks),
    context_size_items=total_items,
    zone_type="safe",
    danger_zone_avoided=True,
    strategy_used="intelligent_chunking",
    confidence_score=0.92,
    latency_ms=1850,
    citations_count=3
)
```

### Grafana Dashboard Template

```json
{
  "dashboard": {
    "title": "GPT-OSS RAG Monitoring",
    "panels": [
      {
        "title": "Query Latency (P50, P90, P99)",
        "targets": [
          "histogram_quantile(0.50, rag_query_latency_seconds)",
          "histogram_quantile(0.90, rag_query_latency_seconds)",
          "histogram_quantile(0.99, rag_query_latency_seconds)"
        ]
      },
      {
        "title": "Zone Hit Distribution",
        "targets": [
          "rate(rag_zone_hits_total{zone_type='safe'}[5m])",
          "rate(rag_zone_hits_total{zone_type='danger'}[5m])",
          "rate(rag_zone_hits_total{zone_type='suspect'}[5m])"
        ]
      },
      {
        "title": "Confidence Score Distribution",
        "targets": ["rag_confidence_score"]
      },
      {
        "title": "Strategy Usage",
        "targets": ["rate(rag_strategy_used_total[5m])"]
      },
      {
        "title": "Citation Accuracy",
        "targets": ["rag_citation_accuracy"]
      }
    ]
  }
}
```

---

## Validation Framework

### Overview

**Goal**: Continuous validation of RAG accuracy using golden datasets and automated testing.

### Golden Dataset Structure

```python
# backend/tests/golden_dataset.json
{
  "datasets": {
    "iec_62443": {
      "name": "IEC 62443-4-2 Requirements",
      "document": "IEC_62443-4-2_2019.pdf",
      "test_cases": [
        {
          "id": "IEC-001",
          "question": "What are the requirements for CR 2.11 (wireless access management)?",
          "expected_answer_contains": [
            "wireless access point",
            "authentication",
            "encryption"
          ],
          "expected_citations": [
            {"section": "4.2.11", "page": 45}
          ],
          "context_size": "medium",  # 100-500 items
          "difficulty": "medium"
        },
        {
          "id": "IEC-002",
          "question": "Compare authentication requirements in CR 1.1 vs CR 1.2",
          "expected_answer_contains": [
            "human user authentication",
            "software process authentication"
          ],
          "expected_citations": [
            {"section": "4.1.1", "page": 32},
            {"section": "4.1.2", "page": 35}
          ],
          "context_size": "large",  # 500+ items
          "difficulty": "hard"
        }
      ]
    },
    "etsi_en_303_645": {
      "name": "ETSI EN 303 645 Cyber Security",
      "document": "ETSI_EN_303_645_V2.1.1.pdf",
      "test_cases": [
        {
          "id": "ETSI-001",
          "question": "What are the requirements for default password management?",
          "expected_answer_contains": [
            "unique per device",
            "factory default passwords"
          ],
          "expected_citations": [
            {"section": "5.1.1", "page": 12}
          ],
          "context_size": "small",  # <100 items
          "difficulty": "easy"
        }
      ]
    }
  }
}
```

### Automated Validation Testing

```python
class ValidationFramework:
    """Automated RAG accuracy validation"""

    def __init__(self):
        self.golden_dataset = self._load_golden_dataset()
        self.results_history = []

    def run_validation(self, rag_service):
        """Execute full validation suite"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'avg_confidence': 0.0,
            'citation_accuracy': 0.0,
            'test_details': []
        }

        for dataset_name, dataset in self.golden_dataset['datasets'].items():
            logger.info(f"Validating dataset: {dataset_name}")

            for test_case in dataset['test_cases']:
                test_result = self._run_test_case(
                    rag_service,
                    test_case,
                    dataset['document']
                )

                results['test_details'].append(test_result)
                results['total_tests'] += 1

                if test_result['passed']:
                    results['passed'] += 1
                else:
                    results['failed'] += 1

        # Calculate aggregate metrics
        results['pass_rate'] = results['passed'] / results['total_tests']
        results['avg_confidence'] = np.mean([
            t['confidence'] for t in results['test_details']
        ])
        results['citation_accuracy'] = np.mean([
            t['citation_accuracy'] for t in results['test_details']
        ])

        # Store results
        self.results_history.append(results)
        self._save_results(results)

        # Alert if below threshold
        if results['pass_rate'] < 0.95:
            self._alert_validation_failure(results)

        return results

    def _run_test_case(self, rag_service, test_case, document):
        """Execute single test case"""
        try:
            # Execute RAG query
            response = rag_service.query(
                project_id=test_case.get('project_id', 'validation'),
                question=test_case['question']
            )

            # Validate answer content
            content_match = self._validate_content(
                response['answer'],
                test_case['expected_answer_contains']
            )

            # Validate citations
            citation_accuracy = self._validate_citations(
                response.get('citations', []),
                test_case['expected_citations']
            )

            # Overall pass/fail
            passed = (
                content_match >= 0.8 and
                citation_accuracy >= 0.9 and
                response.get('confidence', 0) >= 0.85
            )

            return {
                'test_id': test_case['id'],
                'passed': passed,
                'content_match': content_match,
                'citation_accuracy': citation_accuracy,
                'confidence': response.get('confidence', 0),
                'strategy_used': response.get('strategy_used'),
                'latency': response.get('latency', 0)
            }

        except Exception as e:
            logger.error(f"Test case {test_case['id']} failed: {e}")
            return {
                'test_id': test_case['id'],
                'passed': False,
                'error': str(e)
            }

    def _validate_content(self, answer, expected_keywords):
        """Check if answer contains expected keywords"""
        if not answer:
            return 0.0

        answer_lower = answer.lower()
        matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
        return matches / len(expected_keywords)

    def _validate_citations(self, actual_citations, expected_citations):
        """Validate citation accuracy"""
        if not expected_citations:
            return 1.0 if not actual_citations else 0.5

        matches = 0
        for expected in expected_citations:
            for actual in actual_citations:
                if (actual.get('page') == expected['page'] and
                    expected['section'] in actual.get('section', '')):
                    matches += 1
                    break

        return matches / len(expected_citations)
```

### Continuous Validation Schedule

```python
# backend/app/tasks/validation_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Hourly validation (quick smoke test)
@scheduler.scheduled_job('cron', hour='*', minute='0')
def hourly_validation():
    """Quick validation with 10 test cases"""
    framework = ValidationFramework()
    results = framework.run_validation(
        rag_service=get_rag_service(),
        test_subset='smoke'
    )
    logger.info(f"Hourly validation: {results['pass_rate']:.2%} pass rate")

# Daily comprehensive validation
@scheduler.scheduled_job('cron', hour='2', minute='0')
def daily_validation():
    """Full validation with all test cases"""
    framework = ValidationFramework()
    results = framework.run_validation(
        rag_service=get_rag_service(),
        test_subset='full'
    )

    # Generate report
    report_path = f"validation_report_{datetime.now().strftime('%Y%m%d')}.html"
    generate_validation_report(results, report_path)

    logger.info(f"Daily validation complete: {report_path}")

# Weekly zone remapping check
@scheduler.scheduled_job('cron', day_of_week='sun', hour='3', minute='0')
def weekly_zone_check():
    """Check if zone boundaries have shifted"""
    detector = RuntimeZoneDetector()

    if detector.suspect_zones:
        logger.warning(
            f"⚠️ {len(detector.suspect_zones)} suspect zones detected this week"
        )
        # Trigger zone remapping
        schedule_zone_remapping(detector.suspect_zones)

scheduler.start()
```

### A/B Testing Framework

```python
class ABTestFramework:
    """A/B testing for strategy improvements"""

    def __init__(self):
        self.variants = {
            'control': self._control_strategy,
            'variant_a': self._variant_a_strategy,
            'variant_b': self._variant_b_strategy
        }
        self.results = defaultdict(list)

    def split_traffic(self, user_id):
        """Consistent traffic splitting"""
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        variant = ['control', 'variant_a', 'variant_b'][hash_val % 3]
        return variant

    def execute_query(self, user_id, question, context):
        """Execute query with assigned variant"""
        variant = self.split_traffic(user_id)
        strategy = self.variants[variant]

        start_time = time.time()
        result = strategy(question, context)
        latency = time.time() - start_time

        # Record metrics
        self.results[variant].append({
            'latency': latency,
            'confidence': result.get('confidence', 0),
            'success': result.get('success', False)
        })

        return result

    def analyze_results(self):
        """Statistical analysis of variants"""
        for variant, metrics in self.results.items():
            avg_latency = np.mean([m['latency'] for m in metrics])
            avg_confidence = np.mean([m['confidence'] for m in metrics])
            success_rate = np.mean([m['success'] for m in metrics])

            logger.info(f"""
Variant: {variant}
  Avg Latency: {avg_latency:.2f}s
  Avg Confidence: {avg_confidence:.2%}
  Success Rate: {success_rate:.2%}
            """)
```

---

## Implementation Roadmap

### Phase 0: Immediate Mitigation (Today) ⭐

**Goal**: Deploy quick fix using known safe zones

**Steps**:
1. Copy existing zone data to production config:
```python
# backend/app/config/mistral_safe_zones.py
KNOWN_SAFE_ZONES = [
    (100, 450),    # Estimated (100, 250 validated)
    (1000, 1400)   # Validated (1000, 1100, 1250-1400)
]

KNOWN_DANGER_ZONES = [
    (500, 750),    # Validated bugs
    (1200, 1200)   # Validated bug
]
```

2. Implement Strategy 1 (Dynamic Padding) in `lightrag_service.py`

3. Add logging to monitor zone hits:
```python
logger.info(f"Query size: {item_count} items - Zone: {'SAFE' if not is_danger_zone(item_count) else 'DANGER'}")
```

4. Deploy and monitor production logs

**Duration**: 2-3 hours
**Risk**: Low (conservative safe zones)

---

### Phase 1: Comprehensive Zone Mapping (Week 1)

**Goal**: Run full 3-phase testing to map all zones

**Steps**:
1. Run zone mapper script:
```bash
cd backend/tests
python mistral_adaptive_zone_mapper.py
```

2. Review outputs:
   - `mistral_zone_map_YYYYMMDD.json` (detailed test data)
   - `mistral_safe_zones_config.py` (production config)
   - `mistral_zone_map_report_YYYYMMDD.md` (analysis)

3. Validate results:
   - Check boundary confidence scores (should be 95%)
   - Verify no overlapping zones
   - Confirm largest safe zone identified

4. Update production config with validated zones

**Duration**: 5-6 hours test run + 1 hour review
**Risk**: None (read-only testing)

---

### Phase 2: Production Integration (Week 2)

**Goal**: Upgrade from quick fix to validated zone-aware RAG

**Steps**:
1. Replace estimated zones with validated zones from Phase 1

2. Implement Strategy 2 (Intelligent Chunk Sizing):
   - Configure LightRAG default `top_k` to target largest safe zone
   - Add fallback logic for different document sizes

3. Implement Strategy 3 (Multi-Query) for large documents:
   - Add `query_large_document()` method
   - Implement citation merging logic
   - Test with IEC 62443 (300 pages)

4. Add monitoring dashboard:
   - Zone usage statistics
   - Danger zone avoidance rate
   - Query performance metrics

**Duration**: 1 week development + testing
**Risk**: Medium (requires LightRAG integration testing)

---

### Phase 3: Advanced Features (Month 2)

**Goal**: Optimize for production workloads

**Steps**:
1. Implement adaptive chunk sizing:
   - Auto-adjust based on document size
   - Learn optimal zones for different query types

2. Add caching:
   - Cache chunk splits for frequently accessed documents
   - Pre-compute safe batch sizes

3. Implement Strategy 4 (Attention Injection) as experimental feature:
   - A/B test with/without markers
   - Measure accuracy improvement

4. Model-specific zone profiles:
   - Support multiple LLMs with different zones
   - Auto-switch zones based on active model

**Duration**: 2-3 weeks
**Risk**: Low (incremental features)

---

## Production Configuration

### Recommended Settings (Based on Current Knowledge)

```python
# backend/app/config/rag_config.py

class RAGConfig:
    """Production RAG configuration for Mistral Q6_K"""

    # Safe zone targeting
    DEFAULT_CHUNK_COUNT = 1300        # Target: 1201-1400 safe zone
    MIN_CHUNK_COUNT = 250             # Fallback: 100-497 safe zone
    MAX_CHUNK_COUNT = 1400            # Hard limit

    # Multi-query thresholds
    LARGE_DOC_THRESHOLD = 1400        # Switch to batching above this
    BATCH_SIZE = 1300                 # Use largest safe zone for batches

    # Safety margins
    DANGER_ZONE_BUFFER = 10           # Stay 10 items away from boundaries

    # Model-specific zones (from validation testing)
    MISTRAL_SAFE_ZONES = [
        (100, 450),    # Conservative (100, 250 validated)
        (1000, 1400)   # Validated (1000, 1100, 1250-1400)
    ]

    MISTRAL_DANGER_ZONES = [
        (451, 999),    # Includes 500, 750 bugs
        (1200, 1200)   # Specific bug point (will be refined)
    ]

    # Logging
    LOG_ZONE_USAGE = True             # Track zone hits for analysis
    ALERT_ON_DANGER_ZONE = True       # Log warnings for danger zone avoidance
```

### Environment-Specific Overrides

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      # Development: Use smaller chunks for faster testing
      RAG_DEFAULT_CHUNK_COUNT: 250
      RAG_ENABLE_ZONE_CHECKING: "true"

      # Production: Use largest safe zone
      # RAG_DEFAULT_CHUNK_COUNT: 1300
      # RAG_ENABLE_MULTI_QUERY: "true"
```

---

## Appendix: Test Scripts

### A.1 Zone Mapper Script

**Location**: `backend/tests/mistral_adaptive_zone_mapper.py`

**Usage**:
```bash
# Run full 3-phase testing
python mistral_adaptive_zone_mapper.py

# Custom range
python mistral_adaptive_zone_mapper.py --start 100 --end 2000 --step 50

# Quick test (fewer runs)
python mistral_adaptive_zone_mapper.py --quick
```

**Key Features**:
- Dataclass-based structured results
- Automatic transition detection
- Binary search boundary refinement
- Statistical confidence scoring
- Three output formats (JSON, Python, Markdown)
- Graceful interruption (Ctrl+C saves partial results)

### A.2 Quick Validation Script

**Location**: `backend/tests/mistral_quick_zone_check.py`

**Purpose**: Fast check if specific item count is safe

**Usage**:
```python
from mistral_quick_zone_check import check_zone

result = check_zone(item_count=750, runs=5)
if result['middle_accuracy'] == 0:
    print(f"❌ DANGER ZONE: {item_count} items")
else:
    print(f"✅ SAFE: {item_count} items ({result['middle_accuracy']}% accuracy)")
```

### A.3 Zone Visualization Script

**Location**: `backend/tests/visualize_zone_map.py`

**Purpose**: Generate visual chart of safe/danger zones

**Output**:
```
Mistral Q6_K Zone Map
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
100   |████████████████| Safe (100% acc)
...
500   |░░░░░░░░░░░░░░░░| DANGER (0% acc) ⚠️
750   |░░░░░░░░░░░░░░░░| DANGER (0% acc) ⚠️
1000  |████████████████| Safe (100% acc)
1200  |░░░░░░░░░░░░░░░░| DANGER (0% acc) ⚠️
1300  |████████████████| Safe (100% acc)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Legend: █ = Safe Zone  ░ = Danger Zone  ⚠️ = Validated Bug
```

---

## Related Documents

- **Test Results**: `backend/tests/FINAL_4_MODEL_COMPARISON.md`
- **Mistral Validation**: `backend/tests/mistral_q6_k_validation_results.md`
- **Gemma Analysis**: `backend/tests/gemma_limit_analysis.md`
- **LightRAG Integration**: `backend/app/services/lightrag_service.py`

---

## Glossary

- **Danger Zone**: Item count range where LLM exhibits systematic bugs (0% middle accuracy)
- **Safe Zone**: Item count range where LLM works correctly (100% accuracy, or >80% with degradation)
- **Systematic Bug**: Reproducible failure (0% success rate over multiple runs)
- **Transition**: Boundary between safe and danger zones
- **Context Window**: Maximum token count an LLM can process in single query
- **Needle-in-Haystack**: Testing methodology where "needle" (answer) is placed at first/middle/last position in "haystack" (context)

---

**End of Document**
