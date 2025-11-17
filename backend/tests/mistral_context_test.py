#!/usr/bin/env python3
"""
Mistral 24B Context Window Testing Suite
Tests needle-in-haystack retrieval at various context sizes and positions
"""

import json
import time
import random
import requests
import statistics
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import hashlib
import re
import tiktoken  # For accurate token counting

# Configuration
LLM_URL = "http://localhost:8080/completion"
MODEL_NAME = "mistral-small-24b-Q6_K"
MAX_CONTEXT_SIZE = 32768
OUTPUT_DIR = Path("./test_results")
OUTPUT_DIR.mkdir(exist_ok=True)

@dataclass
class TestResult:
    """Single test result data"""
    test_id: str
    timestamp: str
    context_size: int
    needle_position: str  # 'start', 'middle', 'end'
    needle_index: int
    total_items: int
    char_count: int
    token_count: int
    prompt_tokens: int
    completion_tokens: int
    response_time_ms: float
    correct: bool
    response: str
    expected: str
    confidence_score: float
    gpu_memory_mb: Optional[float] = None
    error: Optional[str] = None

class MistralContextTester:
    def __init__(self, base_url: str = LLM_URL):
        self.base_url = base_url
        self.session = requests.Session()
        # Initialize tokenizer (using cl100k_base as approximation for Mistral)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.results: List[TestResult] = []

    def generate_haystack(self, num_items: int, seed: int = 42) -> List[Tuple[int, str]]:
        """Generate diverse haystack items with consistent randomization"""
        random.seed(seed)
        templates = [
            "The {object} is {color}",
            "My {relation}'s {object} named {name} is {attribute}",
            "In {location}, the {object} appears {description}",
            "{name} found a {color} {object} near the {landmark}",
            "The {adjective} {object} belongs to {owner}",
            "During {time}, the {object} becomes {state}",
            "{quantity} {color} {object}s were seen at {place}",
            "The {object} has a {pattern} pattern with {color} highlights"
        ]

        objects = ["apple", "book", "car", "door", "elephant", "flower", "guitar",
                  "house", "island", "jacket", "kite", "lamp", "mountain", "notebook",
                  "ocean", "piano", "quilt", "robot", "star", "table", "umbrella",
                  "violin", "window", "xylophone", "yacht", "zebra"]

        colors = ["red", "blue", "green", "yellow", "purple", "orange", "brown",
                 "black", "white", "pink", "gray", "silver", "gold", "turquoise"]

        names = ["Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace",
                "Henry", "Iris", "Jack", "Kate", "Leo", "Mary", "Nathan", "Olivia"]

        items = []
        for i in range(1, num_items + 1):
            template = random.choice(templates)
            content = template.format(
                object=random.choice(objects),
                color=random.choice(colors),
                relation=random.choice(["brother", "sister", "friend", "neighbor"]),
                name=random.choice(names),
                attribute=random.choice(["soft", "hard", "shiny", "rough", "smooth"]),
                location=random.choice(["the garden", "downtown", "the forest", "the beach"]),
                description=random.choice(["bright", "dim", "vibrant", "pale", "glowing"]),
                landmark=random.choice(["bridge", "tower", "fountain", "statue", "gate"]),
                adjective=random.choice(["ancient", "modern", "mystical", "ordinary", "special"]),
                owner=random.choice(names),
                time=random.choice(["dawn", "noon", "dusk", "midnight", "morning"]),
                state=random.choice(["visible", "hidden", "active", "dormant", "transformed"]),
                quantity=random.choice(["two", "three", "several", "many", "few"]),
                place=random.choice(["the park", "the mall", "the museum", "the theater"]),
                pattern=random.choice(["striped", "dotted", "checkered", "solid", "wavy"])
            )
            items.append((i, content))

        return items

    def create_prompt(self, items: List[Tuple[int, str]],
                     query_index: int,
                     position: str = 'end') -> str:
        """Create prompt with needle at specified position"""
        # Format items with zero-padding for consistent formatting
        max_digits = len(str(len(items)))
        formatted_items = [f"index {idx:0{max_digits}d}: {content}"
                          for idx, content in items]

        # Determine query position in the list
        if position == 'end':
            query = f"\n\nQuestion: What is the exact content of index {query_index:0{max_digits}d}? Respond with ONLY the content text, nothing else."
            prompt = "\n".join(formatted_items) + query
        elif position == 'start':
            query = f"Question: What is the exact content of index {query_index:0{max_digits}d}? Respond with ONLY the content text, nothing else.\n\n"
            prompt = query + "\n".join(formatted_items)
        elif position == 'middle':
            mid_point = len(formatted_items) // 2
            query = f"\n\nQuestion: What is the exact content of index {query_index:0{max_digits}d}? Respond with ONLY the content text, nothing else.\n\n"
            prompt = "\n".join(formatted_items[:mid_point]) + query + "\n".join(formatted_items[mid_point:])
        else:  # random position
            insert_point = random.randint(0, len(formatted_items))
            query = f"\n\nQuestion: What is the exact content of index {query_index:0{max_digits}d}? Respond with ONLY the content text, nothing else.\n\n"
            prompt = "\n".join(formatted_items[:insert_point]) + query + "\n".join(formatted_items[insert_point:])

        return prompt

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        return len(self.tokenizer.encode(text))

    def query_llm(self, prompt: str, max_retries: int = 3) -> Dict:
        """Query the LLM with retry logic"""
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = self.session.post(
                    self.base_url,
                    json={
                        "prompt": prompt,
                        "temperature": 0.0,  # Deterministic
                        "top_p": 1.0,
                        "max_tokens": 100,
                        "stop": ["\n", ".", "index"],  # Stop at natural boundaries
                        "stream": False
                    },
                    timeout=60
                )

                response_time = (time.time() - start_time) * 1000  # ms

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "content": result.get("content", ""),
                        "response_time_ms": response_time,
                        "prompt_tokens": result.get("prompt_tokens", 0),
                        "completion_tokens": result.get("completion_tokens", 0),
                        "error": None
                    }
                else:
                    if attempt == max_retries - 1:
                        return {
                            "content": "",
                            "response_time_ms": response_time,
                            "error": f"HTTP {response.status_code}: {response.text}"
                        }
                    time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        "content": "",
                        "response_time_ms": 0,
                        "error": str(e)
                    }
                time.sleep(2 ** attempt)

    def evaluate_response(self, response: str, expected: str) -> Tuple[bool, float]:
        """Evaluate if response matches expected answer"""
        # Clean up response
        response = response.strip().lower()
        expected = expected.strip().lower()

        # Remove common artifacts
        response = re.sub(r'^(the content of index \d+ is:?\s*)', '', response)
        response = re.sub(r'^(content:?\s*)', '', response)
        response = response.strip('"\'')

        # Exact match
        if response == expected:
            return True, 1.0

        # Fuzzy match (contains expected)
        if expected in response:
            return True, 0.8

        # Calculate similarity score
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, response, expected).ratio()

        return similarity > 0.9, similarity

    def run_single_test(self, num_items: int, position: str,
                       query_indices: List[int] = None) -> List[TestResult]:
        """Run a single test configuration"""
        items = self.generate_haystack(num_items)

        if query_indices is None:
            # Test start, middle, and end items
            query_indices = [1, num_items // 2, num_items]

        test_results = []

        for query_idx in query_indices:
            if query_idx > num_items:
                continue

            test_id = hashlib.md5(
                f"{num_items}_{position}_{query_idx}_{datetime.now()}".encode()
            ).hexdigest()[:8]

            prompt = self.create_prompt(items, query_idx, position)
            expected = items[query_idx - 1][1]  # -1 for 0-based indexing

            # Token counting
            token_count = self.count_tokens(prompt)

            # Query LLM
            llm_response = self.query_llm(prompt)

            # Evaluate
            correct, confidence = self.evaluate_response(
                llm_response["content"],
                expected
            )

            result = TestResult(
                test_id=test_id,
                timestamp=datetime.now().isoformat(),
                context_size=num_items,
                needle_position=position,
                needle_index=query_idx,
                total_items=num_items,
                char_count=len(prompt),
                token_count=token_count,
                prompt_tokens=llm_response.get("prompt_tokens", token_count),
                completion_tokens=llm_response.get("completion_tokens", 0),
                response_time_ms=llm_response.get("response_time_ms", 0),
                correct=correct,
                response=llm_response["content"],
                expected=expected,
                confidence_score=confidence,
                error=llm_response.get("error")
            )

            test_results.append(result)
            self.results.append(result)

            # Wait between queries to avoid caching
            time.sleep(2)

        return test_results

    def run_comprehensive_test(self,
                               context_sizes: List[int] = None,
                               positions: List[str] = None,
                               runs_per_config: int = 3) -> pd.DataFrame:
        """Run comprehensive test suite"""
        if context_sizes is None:
            # Progressive sizes from 1k to 15k items
            context_sizes = [1000, 2000, 3000, 5000, 7500, 10000, 12500, 15000]

        if positions is None:
            positions = ['start', 'middle', 'end']

        print(f"Starting comprehensive test: {len(context_sizes)} sizes × "
              f"{len(positions)} positions × {runs_per_config} runs")
        print("="*60)

        for size in context_sizes:
            for position in positions:
                for run in range(runs_per_config):
                    print(f"\nTesting: size={size}, position={position}, run={run+1}/{runs_per_config}")

                    try:
                        # Test multiple needle positions within each configuration
                        if size <= 10:
                            query_indices = list(range(1, size + 1))
                        else:
                            # Sample indices: start, quartiles, middle, end
                            query_indices = [
                                1,
                                size // 4,
                                size // 2,
                                3 * size // 4,
                                size
                            ]

                        results = self.run_single_test(size, position, query_indices)

                        # Print immediate feedback
                        accuracy = sum(r.correct for r in results) / len(results)
                        avg_time = statistics.mean(r.response_time_ms for r in results)
                        print(f"  ✓ Accuracy: {accuracy:.1%}, Avg time: {avg_time:.0f}ms")

                    except Exception as e:
                        print(f"  ✗ Error: {e}")

                    # Longer wait between different configurations
                    if run < runs_per_config - 1:
                        print("  Waiting 5s before next run...")
                        time.sleep(5)

        # Convert to DataFrame for analysis
        return pd.DataFrame([asdict(r) for r in self.results])

    def analyze_results(self, df: pd.DataFrame) -> Dict:
        """Analyze test results and generate insights"""
        analysis = {
            "summary": {},
            "by_size": {},
            "by_position": {},
            "degradation": {},
            "performance": {}
        }

        # Overall summary
        analysis["summary"] = {
            "total_tests": len(df),
            "overall_accuracy": df['correct'].mean(),
            "avg_response_time_ms": df['response_time_ms'].mean(),
            "max_successful_context": df[df['correct']]['context_size'].max(),
            "failure_rate": 1 - df['correct'].mean()
        }

        # Analysis by context size
        by_size = df.groupby('context_size').agg({
            'correct': ['mean', 'std'],
            'response_time_ms': ['mean', 'std'],
            'token_count': 'mean',
            'confidence_score': 'mean'
        }).round(3)
        analysis["by_size"] = by_size.to_dict()

        # Analysis by position
        by_position = df.groupby('needle_position').agg({
            'correct': 'mean',
            'response_time_ms': 'mean',
            'confidence_score': 'mean'
        }).round(3)
        analysis["by_position"] = by_position.to_dict()

        # Find degradation point (where accuracy drops below 95%)
        size_accuracy = df.groupby('context_size')['correct'].mean().sort_index()
        for size, acc in size_accuracy.items():
            if acc < 0.95:
                analysis["degradation"]["threshold_95"] = size
                analysis["degradation"]["accuracy_at_threshold"] = acc
                break

        # Performance metrics
        analysis["performance"] = {
            "tokens_per_second": (df['token_count'] / (df['response_time_ms'] / 1000)).mean(),
            "max_tokens_processed": df['token_count'].max(),
            "response_time_correlation": df['token_count'].corr(df['response_time_ms'])
        }

        return analysis

    def visualize_results(self, df: pd.DataFrame, output_path: Path):
        """Generate visualization plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Accuracy vs Context Size
        accuracy_by_size = df.groupby('context_size')['correct'].agg(['mean', 'std'])
        axes[0, 0].errorbar(accuracy_by_size.index, accuracy_by_size['mean'],
                           yerr=accuracy_by_size['std'], marker='o', capsize=5)
        axes[0, 0].set_xlabel('Context Size (items)')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].set_title('Retrieval Accuracy vs Context Size')
        axes[0, 0].axhline(y=0.95, color='r', linestyle='--', alpha=0.5, label='95% threshold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Response Time vs Context Size
        time_by_size = df.groupby('context_size')['response_time_ms'].agg(['mean', 'std'])
        axes[0, 1].errorbar(time_by_size.index, time_by_size['mean'],
                           yerr=time_by_size['std'], marker='s', capsize=5, color='orange')
        axes[0, 1].set_xlabel('Context Size (items)')
        axes[0, 1].set_ylabel('Response Time (ms)')
        axes[0, 1].set_title('Response Time vs Context Size')
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Position Analysis
        position_data = df.groupby(['needle_position', 'context_size'])['correct'].mean().unstack()
        position_data.T.plot(marker='o', ax=axes[1, 0])
        axes[1, 0].set_xlabel('Context Size (items)')
        axes[1, 0].set_ylabel('Accuracy')
        axes[1, 0].set_title('Accuracy by Needle Position')
        axes[1, 0].legend(title='Position')
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 4: Heatmap of accuracy
        pivot_table = df.pivot_table(values='correct',
                                     index='needle_position',
                                     columns='context_size',
                                     aggfunc='mean')
        sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='RdYlGn',
                   vmin=0, vmax=1, ax=axes[1, 1])
        axes[1, 1].set_title('Accuracy Heatmap')

        plt.suptitle(f'Mistral 24B Context Window Analysis - {datetime.now().strftime("%Y-%m-%d")}',
                    fontsize=16)
        plt.tight_layout()
        plt.savefig(output_path / 'context_analysis.png', dpi=150)
        plt.show()

        return fig

    def generate_report(self, df: pd.DataFrame, analysis: Dict, output_path: Path):
        """Generate comprehensive markdown report"""
        report = f"""# Mistral 24B Context Window Test Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model**: {MODEL_NAME}
**Max Context**: {MAX_CONTEXT_SIZE} tokens

## Executive Summary

- **Total Tests Run**: {analysis['summary']['total_tests']}
- **Overall Accuracy**: {analysis['summary']['overall_accuracy']:.1%}
- **Average Response Time**: {analysis['summary']['avg_response_time_ms']:.0f}ms
- **Maximum Successful Context**: {analysis['summary']['max_successful_context']:,} items
- **Failure Rate**: {analysis['summary']['failure_rate']:.1%}

## Key Findings

### 1. Context Size Impact
"""
        # Add table for size analysis
        size_df = df.groupby('context_size').agg({
            'correct': ['mean', 'std', 'count'],
            'response_time_ms': 'mean',
            'token_count': 'mean'
        }).round(2)

        report += "\n| Context Size | Accuracy | Std Dev | Response Time | Avg Tokens | Samples |\n"
        report += "|--------------|----------|---------|---------------|------------|----------|\n"

        for size in size_df.index:
            acc_mean = size_df.loc[size, ('correct', 'mean')]
            acc_std = size_df.loc[size, ('correct', 'std')]
            resp_time = size_df.loc[size, ('response_time_ms', 'mean')]
            tokens = size_df.loc[size, ('token_count', 'mean')]
            count = size_df.loc[size, ('correct', 'count')]

            report += f"| {size:,} | {acc_mean:.1%} | ±{acc_std:.2f} | {resp_time:.0f}ms | {tokens:.0f} | {count:.0f} |\n"

        report += f"""

### 2. Position Sensitivity

The model's performance varies based on where the query appears in the context:

"""
        # Add position analysis
        position_df = df.groupby('needle_position')['correct'].agg(['mean', 'count'])
        for pos in position_df.index:
            acc = position_df.loc[pos, 'mean']
            count = position_df.loc[pos, 'count']
            report += f"- **{pos.capitalize()}**: {acc:.1%} accuracy (n={count:.0f})\n"

        # Add degradation analysis
        if 'threshold_95' in analysis['degradation']:
            report += f"""

### 3. Performance Degradation

⚠️ **Critical Finding**: Accuracy drops below 95% at **{analysis['degradation']['threshold_95']:,} items**
(accuracy: {analysis['degradation']['accuracy_at_threshold']:.1%})

This represents approximately **{analysis['degradation']['threshold_95'] / 15000:.0%}** of the tested range.
"""

        # Add performance metrics
        report += f"""

### 4. Performance Metrics

- **Processing Speed**: {analysis['performance']['tokens_per_second']:.0f} tokens/second
- **Maximum Tokens Processed**: {analysis['performance']['max_tokens_processed']:,}
- **Token-Time Correlation**: {analysis['performance']['response_time_correlation']:.3f}

## Detailed Results

### Failed Retrievals

"""
        # Add failure analysis
        failures = df[~df['correct']].head(10)
        if not failures.empty:
            report += "| Test ID | Context Size | Position | Query Index | Response | Expected |\n"
            report += "|---------|--------------|----------|-------------|----------|----------|\n"
            for _, row in failures.iterrows():
                report += f"| {row['test_id'][:6]} | {row['context_size']} | {row['needle_position']} | "
                report += f"{row['needle_index']} | {row['response'][:30]}... | {row['expected'][:30]}... |\n"
        else:
            report += "No failures detected! 🎉\n"

        # Add recommendations
        report += """

## Recommendations

Based on the test results:

"""
        if analysis['summary']['overall_accuracy'] > 0.95:
            report += "✅ **Model is suitable for production use** with careful context management.\n\n"
        else:
            report += "⚠️ **Model shows concerning accuracy issues** that need investigation.\n\n"

        if 'threshold_95' in analysis['degradation']:
            safe_limit = int(analysis['degradation']['threshold_95'] * 0.8)
            report += f"1. **Recommended maximum context**: {safe_limit:,} items (80% of degradation point)\n"
        else:
            report += "1. **Context handling**: Model maintains high accuracy across all tested sizes\n"

        report += """2. **Query positioning**: Consider placing important queries at the beginning or end of context
3. **Monitoring**: Implement response time monitoring with alert threshold at 10 seconds
4. **Fallback strategy**: Prepare chunking strategy for contexts exceeding safe limits

## Test Configuration

```python
# Test Parameters
context_sizes = [1000, 2000, 3000, 5000, 7500, 10000, 12500, 15000]
positions = ['start', 'middle', 'end']
runs_per_config = 3
temperature = 0.0  # Deterministic
model = "mistral-small-24b-Q6_K"
```

## Appendix: Raw Data

Full results saved to: `test_results/full_results.csv`
"""

        # Save report
        report_path = output_path / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\n✅ Report saved to: {report_path}")

        return report

def main():
    """Main execution function"""
    print("="*60)
    print("Mistral 24B Context Window Testing Suite")
    print("="*60)

    # Initialize tester
    tester = MistralContextTester()

    # Run quick sanity check
    print("\n1. Running sanity check...")
    sanity_results = tester.run_single_test(num_items=10, position='end', query_indices=[1, 5, 10])
    sanity_accuracy = sum(r.correct for r in sanity_results) / len(sanity_results)
    print(f"   Sanity check accuracy: {sanity_accuracy:.0%}")

    if sanity_accuracy < 0.5:
        print("❌ Sanity check failed! Please verify LLM is running and accessible.")
        return

    print("   ✅ Sanity check passed!")

    # Run comprehensive test
    print("\n2. Running comprehensive test suite...")
    print("   This will take approximately 2-3 hours.")
    response = input("   Continue? (y/n): ")

    if response.lower() != 'y':
        print("   Test cancelled.")
        return

    # Run tests
    df = tester.run_comprehensive_test(
        context_sizes=[1000, 2000, 3000, 5000, 7500, 10000, 12500, 15000],
        positions=['start', 'middle', 'end'],
        runs_per_config=3
    )

    # Save raw results
    csv_path = OUTPUT_DIR / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n3. Raw results saved to: {csv_path}")

    # Analyze results
    print("\n4. Analyzing results...")
    analysis = tester.analyze_results(df)

    # Save analysis
    analysis_path = OUTPUT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"   Analysis saved to: {analysis_path}")

    # Generate visualizations
    print("\n5. Generating visualizations...")
    tester.visualize_results(df, OUTPUT_DIR)

    # Generate report
    print("\n6. Generating final report...")
    report = tester.generate_report(df, analysis, OUTPUT_DIR)

    print("\n" + "="*60)
    print("✅ Testing complete!")
    print(f"   Results directory: {OUTPUT_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()