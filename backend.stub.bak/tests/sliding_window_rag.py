#!/usr/bin/env python3
"""
Application-Level Sliding Window for Mistral Small 24B
Extends effective context beyond 32k limit using overlapping windows
"""

import requests
from typing import List, Dict, Tuple
import time

class SlidingWindowRAG:
    """
    Implements sliding window context management for models without native SWA.
    This allows processing documents larger than the model's context limit.
    """

    def __init__(self,
                 base_url="http://localhost:8080/v1/chat/completions",
                 max_context=28000,  # Leave buffer for safety
                 window_size=20000,  # Size of each window
                 overlap=5000):      # Overlap between windows

        self.base_url = base_url
        self.max_context = max_context
        self.window_size = window_size
        self.overlap = overlap
        self.stride = window_size - overlap

    def chunk_document(self, text: str, tokens_per_char=0.25) -> List[str]:
        """
        Split document into overlapping windows.
        Approximates tokens as 1 token ≈ 4 characters.
        """
        char_window = int(self.window_size / tokens_per_char)
        char_stride = int(self.stride / tokens_per_char)

        chunks = []
        for i in range(0, len(text), char_stride):
            chunk = text[i:i + char_window]
            chunks.append(chunk)
            if i + char_window >= len(text):
                break

        return chunks

    def process_with_sliding_window(self, document: str, question: str) -> Dict:
        """
        Process a large document using sliding windows.
        Each window gets the question, aggregates results.
        """
        chunks = self.chunk_document(document)
        print(f"Document split into {len(chunks)} windows")

        all_answers = []
        all_evidence = []

        for i, chunk in enumerate(chunks):
            print(f"\nProcessing window {i+1}/{len(chunks)}...")

            # Construct prompt for this window
            prompt = f"""Context (Part {i+1} of document):
{chunk}

Question: {question}

Instructions: Answer based ONLY on the above context. If the answer is partially in this context, provide what you can see. Include any relevant quotes."""

            # Query the model
            response = self._query_model(prompt)

            if response and "not found" not in response.lower() and "cannot answer" not in response.lower():
                all_answers.append({
                    "window": i+1,
                    "answer": response,
                    "chunk_start": i * self.stride,
                    "chunk_text_sample": chunk[:200] + "..."
                })

            # Small delay between windows
            time.sleep(1)

        # Aggregate results
        return self._aggregate_answers(all_answers, question)

    def _query_model(self, prompt: str) -> str:
        """Query the Mistral model"""
        try:
            response = requests.post(
                self.base_url,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Query error: {e}")
            return None

    def _aggregate_answers(self, answers: List[Dict], question: str) -> Dict:
        """
        Aggregate answers from multiple windows.
        Can be enhanced with reranking or synthesis.
        """
        if not answers:
            return {
                "status": "no_answer",
                "message": "No relevant information found in any window"
            }

        # Simple aggregation - in production, you'd want more sophisticated merging
        if len(answers) == 1:
            return {
                "status": "single_window",
                "answer": answers[0]["answer"],
                "window": answers[0]["window"]
            }

        # Multiple windows have answers - synthesize
        all_answers_text = "\n\n".join([
            f"[From section {a['window']}]: {a['answer']}"
            for a in answers
        ])

        # Use model to synthesize final answer
        synthesis_prompt = f"""Multiple sections of a document contain relevant information:

{all_answers_text}

Question: {question}

Synthesize a complete answer combining all the relevant information above:"""

        final_answer = self._query_model(synthesis_prompt)

        return {
            "status": "multi_window",
            "answer": final_answer,
            "windows_used": [a["window"] for a in answers],
            "raw_answers": answers
        }


class AdvancedSlidingWindow:
    """
    Advanced sliding window with attention-aware chunking.
    Mimics Gemma-style local+global attention at application level.
    """

    def __init__(self, base_url="http://localhost:8080/v1/chat/completions"):
        self.base_url = base_url

        # Configuration mimicking Gemma 2 approach
        self.local_window = 4096    # Local attention window
        self.global_tokens = 256    # Important tokens kept globally
        self.max_context = 28000    # Safe limit for Mistral

    def smart_chunking(self, document: str, question: str) -> Tuple[str, List[str]]:
        """
        Create a global summary + local chunks strategy.
        Similar to how models with local+global attention work.
        """

        # Step 1: Extract key information as "global" context
        global_prompt = f"""Document: {document[:8000]}...

Create a brief summary (max 150 words) of the KEY FACTS, important entities, and main topics in this document that would be relevant for answering questions:"""

        global_summary = self._query_model(global_prompt)

        # Step 2: Create overlapping local windows
        chunks = []
        chunk_size = 15000  # Smaller chunks since we'll prepend global context
        overlap = 3000

        for i in range(0, len(document), chunk_size - overlap):
            chunk = document[i:i + chunk_size]
            chunks.append(chunk)
            if i + chunk_size >= len(document):
                break

        return global_summary, chunks

    def query_with_global_local(self, document: str, question: str) -> Dict:
        """
        Process query using global context + local windows.
        This mimics architectural sliding window at application level.
        """

        print("Extracting global context...")
        global_context, local_chunks = self.smart_chunking(document, question)

        relevant_answers = []

        for i, chunk in enumerate(local_chunks):
            print(f"Processing chunk {i+1}/{len(local_chunks)}...")

            # Combine global + local context
            prompt = f"""Global Document Summary:
{global_context}

Current Section (Part {i+1}):
{chunk}

Question: {question}

Answer based on the current section, considering the global context. If this section doesn't contain the answer, respond with 'NOT_IN_THIS_SECTION'."""

            response = self._query_model(prompt)

            if response and "NOT_IN_THIS_SECTION" not in response:
                relevant_answers.append({
                    "chunk": i+1,
                    "answer": response
                })

            time.sleep(1)

        if not relevant_answers:
            return {"status": "no_answer", "message": "Answer not found"}

        # Final synthesis with global context
        if len(relevant_answers) > 1:
            synthesis = self._synthesize_with_global(
                global_context, relevant_answers, question
            )
            return {
                "status": "success",
                "answer": synthesis,
                "chunks_used": [a["chunk"] for a in relevant_answers]
            }
        else:
            return {
                "status": "success",
                "answer": relevant_answers[0]["answer"],
                "chunk": relevant_answers[0]["chunk"]
            }

    def _query_model(self, prompt: str) -> str:
        """Query helper"""
        try:
            response = requests.post(
                self.base_url,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30
            )
            return response.json()["choices"][0]["message"]["content"]
        except:
            return None

    def _synthesize_with_global(self, global_context: str,
                                answers: List[Dict], question: str) -> str:
        """Synthesize final answer with global awareness"""

        all_answers = "\n".join([
            f"[Section {a['chunk']}]: {a['answer']}"
            for a in answers
        ])

        prompt = f"""Global Context: {global_context}

Relevant Information Found:
{all_answers}

Question: {question}

Provide a comprehensive answer that synthesizes all the information:"""

        return self._query_model(prompt)


def demo_sliding_window():
    """Demo showing how to extend context beyond 32k limit"""

    # Create a large document that exceeds 32k tokens
    large_doc = """
    [Imagine this is a 50,000 token document about IEC 62443]
    Section 1: Introduction to IEC 62443...
    Section 2: Security Zones and Conduits...
    Section 3: Security Levels...
    ... (continues for many pages) ...
    Section 50: Compliance Requirements...
    """

    # Simulate with smaller example
    large_doc = " ".join([
        f"Section {i}: Information about topic {i}. " * 100
        for i in range(1, 20)
    ])

    # Basic sliding window
    print("="*60)
    print("BASIC SLIDING WINDOW DEMO")
    print("="*60)

    rag = SlidingWindowRAG()
    result = rag.process_with_sliding_window(
        large_doc,
        "What information is in section 15?"
    )
    print(f"\nResult: {result}")

    # Advanced global+local approach
    print("\n" + "="*60)
    print("ADVANCED GLOBAL+LOCAL WINDOW DEMO")
    print("="*60)

    advanced = AdvancedSlidingWindow()
    result = advanced.query_with_global_local(
        large_doc,
        "What information is in section 15?"
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    # Test basic functionality
    print("Testing Sliding Window Context Extension for Mistral Small 24B")
    print("-"*60)

    # Quick test
    sw = SlidingWindowRAG()

    # Create test document
    test_doc = "\n".join([
        f"Item {i}: The value is {i*100}"
        for i in range(1, 5000)  # Would exceed 32k context
    ])

    print(f"Document size: {len(test_doc)} characters")
    print(f"Estimated tokens: {len(test_doc)//4}")

    # This would fail with direct query but works with sliding window
    result = sw.process_with_sliding_window(
        test_doc,
        "What is the value of item 4500?"
    )

    print(f"\nResult: {result}")

    # Run full demo
    # demo_sliding_window()