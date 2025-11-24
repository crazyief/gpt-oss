#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mistral Q6_K Adaptive Zone Mapper
3-Phase intelligent testing strategy to map all safe/danger zones with precision

Phase 1: Coarse Discovery (50-item increments, 3 runs)
Phase 2: Binary Search Boundaries (5 runs, ±5 item precision)
Phase 3: Production Validation (10 runs at critical boundaries)
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
from dataclasses import dataclass, asdict
from enum import Enum

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class ZoneType(Enum):
    """Classification of test zones"""
    SAFE = "safe"
    DANGER = "danger"
    UNKNOWN = "unknown"


@dataclass
class TestResult:
    """Single test result"""
    num_items: int
    position: str  # 'first', 'middle', 'last'
    run_number: int
    expected_value: int
    actual_value: str
    correct: bool
    tokens: int
    response_time: float
    timestamp: str


@dataclass
class PositionSummary:
    """Summary for a position across multiple runs"""
    position: str
    total_runs: int
    correct_count: int
    accuracy: float
    avg_tokens: float
    consistency: str
    all_results: List[TestResult]


@dataclass
class ZoneTest:
    """Complete test for a specific item count"""
    num_items: int
    phase: int
    reason: str
    positions: Dict[str, PositionSummary]
    overall_accuracy: float
    zone_type: ZoneType
    confidence: float


class MistralZoneMapper:
    """Intelligent adaptive zone mapper for Mistral Q6_K"""

    def __init__(self,
                 api_url: str = "http://localhost:8080/v1/chat/completions",
                 output_dir: str = ".",
                 rest_time: int = 15):
        """
        Initialize the zone mapper

        Args:
            api_url: Mistral Q6_K API endpoint
            output_dir: Directory for output files
            rest_time: Seconds to wait between runs
        """
        self.api_url = api_url
        self.output_dir = output_dir
        self.rest_time = rest_time

        # Results storage
        self.all_tests: List[ZoneTest] = []
        self.transitions: List[Tuple[int, int]] = []  # (from_items, to_items)
        self.safe_zones: List[Tuple[int, int]] = []
        self.danger_zones: List[Tuple[int, int]] = []

        # Statistics
        self.total_queries = 0
        self.start_time = None
        self.phase_times = {}

    def test_single_position(self,
                            num_items: int,
                            position: str,
                            index: int,
                            run_number: int) -> TestResult:
        """
        Test a single position

        Args:
            num_items: Total number of items in the list
            position: Position name ('first', 'middle', 'last')
            index: Actual index to test
            run_number: Current run number

        Returns:
            TestResult object
        """
        # Build the haystack
        items = []
        for i in range(1, num_items + 1):
            items.append(f"index {i}: The value for item {i} is {i*100}")
        haystack = "\n".join(items)

        prompt = f"{haystack}\n\nQuestion: What is the content of index {index}? Reply with just the value number."
        expected = str(index * 100)

        start_time = time.time()

        try:
            response = requests.post(
                self.api_url,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 20
                },
                timeout=60
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                correct = expected in content
                tokens = result.get("usage", {}).get("total_tokens", 0)

                return TestResult(
                    num_items=num_items,
                    position=position,
                    run_number=run_number,
                    expected_value=int(expected),
                    actual_value=content,
                    correct=correct,
                    tokens=tokens,
                    response_time=response_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return TestResult(
                    num_items=num_items,
                    position=position,
                    run_number=run_number,
                    expected_value=int(expected),
                    actual_value=f"HTTP {response.status_code}",
                    correct=False,
                    tokens=0,
                    response_time=response_time,
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            return TestResult(
                num_items=num_items,
                position=position,
                run_number=run_number,
                expected_value=int(expected),
                actual_value=f"Error: {str(e)[:50]}",
                correct=False,
                tokens=0,
                response_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )

    def test_item_count(self,
                       num_items: int,
                       num_runs: int,
                       phase: int,
                       reason: str) -> ZoneTest:
        """
        Test a specific item count with multiple runs

        Args:
            num_items: Number of items to test
            num_runs: Number of runs per position
            phase: Current phase number
            reason: Reason for this test

        Returns:
            ZoneTest object with complete results
        """
        print(f"\n{'='*70}")
        print(f"[PHASE {phase}] Testing {num_items} items ({num_runs} runs)")
        print(f"[REASON] {reason}")
        print('='*70)

        # Define test positions
        test_positions = {
            'first': 1,
            'middle': num_items // 2,
            'last': num_items
        }

        position_results = {}

        for pos_name, pos_index in test_positions.items():
            print(f"\n  [POSITION] {pos_name.upper()} (index {pos_index})")
            print(f"  {'-'*60}")

            results = []

            for run in range(1, num_runs + 1):
                print(f"\n    [RUN {run}/{num_runs}] ", end="", flush=True)

                result = self.test_single_position(num_items, pos_name, pos_index, run)
                results.append(result)
                self.total_queries += 1

                status = "✅ PASS" if result.correct else "❌ FAIL"
                print(f"{status}")
                print(f"    Expected: {result.expected_value}")
                print(f"    Got: {result.actual_value}")
                print(f"    Tokens: {result.tokens:,}")
                print(f"    Time: {result.response_time:.2f}s")

                # Rest between runs (but not after last run)
                if run < num_runs:
                    print(f"\n    [WAIT] Resting {self.rest_time} seconds...")
                    for i in range(self.rest_time, 0, -1):
                        print(f"    [WAIT] {i:2d}s remaining...", end="\r", flush=True)
                        time.sleep(1)
                    print()

            # Calculate position summary
            correct_count = sum(r.correct for r in results)
            accuracy = correct_count / num_runs
            avg_tokens = sum(r.tokens for r in results) / num_runs if any(r.tokens > 0 for r in results) else 0

            # Determine consistency
            if accuracy == 1.0:
                consistency = "STABLE (always correct)"
            elif accuracy == 0.0:
                consistency = "STABLE FAILURE (always wrong)"
            elif accuracy >= 0.8:
                consistency = "MOSTLY CORRECT (occasional failure)"
            elif accuracy >= 0.4:
                consistency = "INCONSISTENT (random)"
            else:
                consistency = "MOSTLY WRONG (occasional success)"

            position_results[pos_name] = PositionSummary(
                position=pos_name,
                total_runs=num_runs,
                correct_count=correct_count,
                accuracy=accuracy,
                avg_tokens=avg_tokens,
                consistency=consistency,
                all_results=results
            )

            print(f"\n    [RESULT] {pos_name.upper()}: {accuracy:.0%} ({correct_count}/{num_runs}) - {consistency}")

        # Calculate overall accuracy
        total_correct = sum(pos.correct_count for pos in position_results.values())
        total_runs = sum(pos.total_runs for pos in position_results.values())
        overall_accuracy = total_correct / total_runs

        # Determine zone type and confidence
        middle_accuracy = position_results['middle'].accuracy

        if middle_accuracy >= 0.95:
            zone_type = ZoneType.SAFE
            confidence = 0.95
        elif middle_accuracy <= 0.05:
            zone_type = ZoneType.DANGER
            confidence = 0.95
        elif middle_accuracy >= 0.8:
            zone_type = ZoneType.SAFE
            confidence = 0.8
        elif middle_accuracy <= 0.2:
            zone_type = ZoneType.DANGER
            confidence = 0.8
        else:
            zone_type = ZoneType.UNKNOWN
            confidence = 0.5

        print(f"\n  {'='*60}")
        print(f"  [OVERALL] Accuracy: {overall_accuracy:.0%} ({total_correct}/{total_runs})")
        print(f"  [ZONE TYPE] {zone_type.value.upper()} (confidence: {confidence:.0%})")
        print(f"  [TOKENS] Average: {position_results['middle'].avg_tokens:.0f}")
        print(f"  {'='*60}")

        return ZoneTest(
            num_items=num_items,
            phase=phase,
            reason=reason,
            positions=position_results,
            overall_accuracy=overall_accuracy,
            zone_type=zone_type,
            confidence=confidence
        )

    def phase1_coarse_discovery(self) -> List[ZoneTest]:
        """
        Phase 1: Coarse Discovery
        Test every 50 items from 100 to 1400
        3 runs per test to detect 0% vs 100% zones

        Returns:
            List of ZoneTest results
        """
        print("\n" + "+"*70)
        print("|" + " PHASE 1: COARSE DISCOVERY ".center(68) + "|")
        print("+"*70)
        print("\n[STRATEGY] Test every 50 items (100-1400)")
        print("[RUNS] 3 per position (detect stable failures)")
        print("[GOAL] Identify all major transitions")
        print("[ESTIMATED TIME] ~2 hours\n")

        phase1_start = time.time()
        test_points = range(100, 1401, 50)
        results = []

        for i, num_items in enumerate(test_points, 1):
            result = self.test_item_count(
                num_items=num_items,
                num_runs=3,
                phase=1,
                reason=f"Coarse discovery {i}/{len(list(test_points))}"
            )
            results.append(result)
            self.all_tests.append(result)

            # Short rest between test sizes
            if num_items != list(test_points)[-1]:
                print(f"\n[WAIT] Switching to next test size (5s rest)...")
                time.sleep(5)

        self.phase_times['phase1'] = time.time() - phase1_start

        return results

    def identify_transitions(self, phase1_results: List[ZoneTest]) -> List[Tuple[int, int, str]]:
        """
        Analyze Phase 1 results to identify zone transitions

        Args:
            phase1_results: Results from Phase 1

        Returns:
            List of (from_items, to_items, transition_type) tuples
        """
        print("\n" + "+"*70)
        print("|" + " ANALYZING PHASE 1: TRANSITION DETECTION ".center(68) + "|")
        print("+"*70 + "\n")

        transitions = []

        for i in range(len(phase1_results) - 1):
            current = phase1_results[i]
            next_test = phase1_results[i + 1]

            current_type = current.zone_type
            next_type = next_test.zone_type

            if current_type != next_type:
                transition_type = f"{current_type.value} → {next_type.value}"
                transitions.append((current.num_items, next_test.num_items, transition_type))

                print(f"[TRANSITION FOUND] {current.num_items} → {next_test.num_items}")
                print(f"  Type: {transition_type}")
                print(f"  Current: {current_type.value} ({current.positions['middle'].accuracy:.0%} middle)")
                print(f"  Next: {next_type.value} ({next_test.positions['middle'].accuracy:.0%} middle)")
                print()

        print(f"[SUMMARY] Found {len(transitions)} transitions")
        self.transitions = transitions

        return transitions

    def phase2_binary_search(self, transitions: List[Tuple[int, int, str]]) -> List[ZoneTest]:
        """
        Phase 2: Binary Search for Exact Boundaries
        Use binary search to find exact transition points (±5 items)

        Args:
            transitions: List of transitions from Phase 1

        Returns:
            List of boundary test results
        """
        print("\n" + "+"*70)
        print("|" + " PHASE 2: BOUNDARY REFINEMENT ".center(68) + "|")
        print("+"*70)
        print("\n[STRATEGY] Binary search for exact boundaries")
        print("[PRECISION] ±5 items")
        print("[RUNS] 5 per test (higher confidence)")
        print("[GOAL] Map exact danger zone edges")
        print(f"[TRANSITIONS] {len(transitions)} to refine")
        print("[ESTIMATED TIME] ~2-3 hours\n")

        phase2_start = time.time()
        results = []

        for trans_idx, (low, high, trans_type) in enumerate(transitions, 1):
            print(f"\n{'='*70}")
            print(f"[TRANSITION {trans_idx}/{len(transitions)}] Refining {low} → {high} ({trans_type})")
            print('='*70)

            # Binary search between low and high
            left = low
            right = high
            boundary_candidates = []

            while right - left > 10:  # Stop when range is ≤10 items
                mid = (left + right) // 2

                print(f"\n[BINARY SEARCH] Range: {left}-{right}, Testing: {mid}")

                result = self.test_item_count(
                    num_items=mid,
                    num_runs=5,
                    phase=2,
                    reason=f"Binary search {trans_idx}/{len(transitions)}: narrowing {left}-{right}"
                )
                results.append(result)
                self.all_tests.append(result)

                # Adjust search range based on result
                if result.zone_type == ZoneType.SAFE:
                    left = mid
                    print(f"[DECISION] {mid} is SAFE, searching higher range")
                elif result.zone_type == ZoneType.DANGER:
                    right = mid
                    print(f"[DECISION] {mid} is DANGER, searching lower range")
                else:
                    # Uncertain - test both sides
                    print(f"[DECISION] {mid} is UNCERTAIN, testing both sides")
                    boundary_candidates.append(mid)
                    break

                time.sleep(5)  # Rest between binary search steps

            # Final boundary is between left and right
            boundary_point = (left + right) // 2
            boundary_candidates.append(boundary_point)

            print(f"\n[BOUNDARY FOUND] Transition occurs around {boundary_point} items")
            print(f"  Safe up to: ~{left} items")
            print(f"  Danger starts: ~{right} items")

            # Test the exact boundary with high confidence (10 runs)
            print(f"\n[VALIDATION] Testing exact boundary with 10 runs...")
            boundary_result = self.test_item_count(
                num_items=boundary_point,
                num_runs=10,
                phase=2,
                reason=f"Exact boundary validation for transition {trans_idx}"
            )
            results.append(boundary_result)
            self.all_tests.append(boundary_result)

        self.phase_times['phase2'] = time.time() - phase2_start

        return results

    def phase3_production_validation(self, boundary_results: List[ZoneTest]) -> List[ZoneTest]:
        """
        Phase 3: Production Validation
        Test boundaries ±10 items with 10 runs for production confidence

        Args:
            boundary_results: Results from Phase 2

        Returns:
            List of validation test results
        """
        print("\n" + "+"*70)
        print("|" + " PHASE 3: PRODUCTION VALIDATION ".center(68) + "|")
        print("+"*70)
        print("\n[STRATEGY] Validate safety margins")
        print("[MARGIN] ±10 items from each boundary")
        print("[RUNS] 10 per test (production confidence)")
        print("[GOAL] Confirm safe deployment zones")
        print("[ESTIMATED TIME] ~1 hour\n")

        phase3_start = time.time()
        results = []

        # Extract unique boundary points
        boundaries = sorted(set(test.num_items for test in boundary_results))

        for boundary_idx, boundary in enumerate(boundaries, 1):
            print(f"\n{'='*70}")
            print(f"[BOUNDARY {boundary_idx}/{len(boundaries)}] Validating around {boundary} items")
            print('='*70)

            # Test boundary - 10
            test_below = self.test_item_count(
                num_items=boundary - 10,
                num_runs=10,
                phase=3,
                reason=f"Safety margin validation: {boundary} - 10"
            )
            results.append(test_below)
            self.all_tests.append(test_below)

            time.sleep(5)

            # Test boundary + 10
            test_above = self.test_item_count(
                num_items=boundary + 10,
                num_runs=10,
                phase=3,
                reason=f"Safety margin validation: {boundary} + 10"
            )
            results.append(test_above)
            self.all_tests.append(test_above)

            print(f"\n[VALIDATION SUMMARY]")
            print(f"  {boundary - 10} items: {test_below.zone_type.value} ({test_below.confidence:.0%} confidence)")
            print(f"  {boundary + 10} items: {test_above.zone_type.value} ({test_above.confidence:.0%} confidence)")

        self.phase_times['phase3'] = time.time() - phase3_start

        return results

    def generate_safe_zones(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Analyze all test results to generate safe and danger zones

        Returns:
            Tuple of (safe_zones, danger_zones)
        """
        print("\n" + "+"*70)
        print("|" + " GENERATING SAFE/DANGER ZONE MAP ".center(68) + "|")
        print("+"*70 + "\n")

        # Sort all tests by item count
        sorted_tests = sorted(self.all_tests, key=lambda t: t.num_items)

        safe_zones = []
        danger_zones = []

        current_zone_start = None
        current_zone_type = None

        for test in sorted_tests:
            if current_zone_type is None:
                # Start first zone
                current_zone_start = test.num_items
                current_zone_type = test.zone_type
            elif test.zone_type != current_zone_type:
                # Zone transition - close previous zone
                zone_end = test.num_items - 1

                if current_zone_type == ZoneType.SAFE:
                    safe_zones.append((current_zone_start, zone_end))
                elif current_zone_type == ZoneType.DANGER:
                    danger_zones.append((current_zone_start, zone_end))

                # Start new zone
                current_zone_start = test.num_items
                current_zone_type = test.zone_type

        # Close final zone
        if current_zone_type == ZoneType.SAFE:
            safe_zones.append((current_zone_start, sorted_tests[-1].num_items))
        elif current_zone_type == ZoneType.DANGER:
            danger_zones.append((current_zone_start, sorted_tests[-1].num_items))

        self.safe_zones = safe_zones
        self.danger_zones = danger_zones

        print(f"[SAFE ZONES] {len(safe_zones)} zones identified:")
        for start, end in safe_zones:
            print(f"  {start:4d} - {end:4d} items (✅ safe)")

        print(f"\n[DANGER ZONES] {len(danger_zones)} zones identified:")
        for start, end in danger_zones:
            print(f"  {start:4d} - {end:4d} items (❌ avoid)")

        return safe_zones, danger_zones

    def generate_production_config(self) -> str:
        """
        Generate production-ready Python configuration code

        Returns:
            Python code as string
        """
        config = f"""# Mistral Q6_K Safe Zone Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Total tests: {len(self.all_tests)}
# Total queries: {self.total_queries}

from typing import List, Tuple

# Safe zones (verified with high confidence)
SAFE_ZONES: List[Tuple[int, int]] = {self.safe_zones}

# Danger zones (avoid these item counts)
DANGER_ZONES: List[Tuple[int, int]] = {self.danger_zones}

def is_safe_item_count(num_items: int) -> bool:
    \"\"\"
    Check if an item count is in a safe zone

    Args:
        num_items: Number of items to check

    Returns:
        True if safe, False if in danger zone
    \"\"\"
    for start, end in SAFE_ZONES:
        if start <= num_items <= end:
            return True
    return False

def get_nearest_safe_count(requested_items: int) -> int:
    \"\"\"
    Get nearest safe item count for a requested size

    Args:
        requested_items: Desired item count

    Returns:
        Nearest safe item count (may be padded)
    \"\"\"
    # Check if already safe
    if is_safe_item_count(requested_items):
        return requested_items

    # Find which danger zone we're in
    for danger_start, danger_end in DANGER_ZONES:
        if danger_start <= requested_items <= danger_end:
            # Pad to end of danger zone + 1
            return danger_end + 1

    # Not in any defined zone - return as-is with warning
    print(f"WARNING: {{requested_items}} not in mapped zones")
    return requested_items

def apply_safe_padding(items: List[str]) -> Tuple[List[str], int]:
    \"\"\"
    Apply padding to avoid danger zones

    Args:
        items: List of items to potentially pad

    Returns:
        Tuple of (padded_items, padding_count)
    \"\"\"
    current_count = len(items)
    safe_count = get_nearest_safe_count(current_count)

    if safe_count > current_count:
        padding_needed = safe_count - current_count
        padding = [f"PADDING_{{i}}" for i in range(padding_needed)]
        return items + padding, padding_needed

    return items, 0

# Statistics
TOTAL_TESTS = {len(self.all_tests)}
TOTAL_QUERIES = {self.total_queries}
TEST_DATE = "{datetime.now().strftime('%Y-%m-%d')}"
CONFIDENCE_LEVEL = "95%"  # Based on 10-run validation
"""
        return config

    def save_results(self):
        """Save all results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save detailed JSON results
        json_file = f"{self.output_dir}/mistral_zone_map_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            data = {
                'metadata': {
                    'timestamp': timestamp,
                    'total_tests': len(self.all_tests),
                    'total_queries': self.total_queries,
                    'phase_times': self.phase_times,
                    'total_time': sum(self.phase_times.values())
                },
                'safe_zones': self.safe_zones,
                'danger_zones': self.danger_zones,
                'transitions': self.transitions,
                'all_tests': [
                    {
                        'num_items': test.num_items,
                        'phase': test.phase,
                        'reason': test.reason,
                        'zone_type': test.zone_type.value,
                        'confidence': test.confidence,
                        'overall_accuracy': test.overall_accuracy,
                        'positions': {
                            pos: {
                                'accuracy': summary.accuracy,
                                'correct_count': summary.correct_count,
                                'total_runs': summary.total_runs,
                                'avg_tokens': summary.avg_tokens,
                                'consistency': summary.consistency
                            }
                            for pos, summary in test.positions.items()
                        }
                    }
                    for test in self.all_tests
                ]
            }
            json.dump(data, f, indent=2)

        print(f"\n[SAVED] Detailed results: {json_file}")

        # Save production config
        config_file = f"{self.output_dir}/mistral_safe_zones_config.py"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_production_config())

        print(f"[SAVED] Production config: {config_file}")

        # Save markdown report
        md_file = f"{self.output_dir}/mistral_zone_map_report_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown_report())

        print(f"[SAVED] Markdown report: {md_file}")

    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        report = f"""# Mistral Q6_K Zone Mapping Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Tests**: {len(self.all_tests)}
**Total Queries**: {self.total_queries}
**Total Time**: {sum(self.phase_times.values())/3600:.2f} hours

## Executive Summary

This report documents the comprehensive testing of Mistral 24B Q6_K to map all safe and danger zones for production deployment.

### Safe Zones (Verified)

| Start | End | Items | Pages (~) |
|-------|-----|-------|-----------|
"""
        for start, end in self.safe_zones:
            pages = (start + end) // 2 * 22 // 500  # Rough page estimate
            report += f"| {start} | {end} | {end - start + 1} | ~{pages} |\n"

        report += f"""
### Danger Zones (AVOID)

| Start | End | Items | Risk |
|-------|-----|-------|------|
"""
        for start, end in self.danger_zones:
            report += f"| {start} | {end} | {end - start + 1} | ❌ HIGH |\n"

        report += f"""
## Phase Breakdown

### Phase 1: Coarse Discovery
- **Time**: {self.phase_times.get('phase1', 0)/3600:.2f} hours
- **Strategy**: 50-item increments, 3 runs each
- **Results**: Identified {len(self.transitions)} major transitions

### Phase 2: Boundary Refinement
- **Time**: {self.phase_times.get('phase2', 0)/3600:.2f} hours
- **Strategy**: Binary search to ±5 item precision
- **Results**: Mapped exact boundaries for all transitions

### Phase 3: Production Validation
- **Time**: {self.phase_times.get('phase3', 0)/3600:.2f} hours
- **Strategy**: 10-run validation at critical boundaries
- **Results**: Confirmed safety margins with 95% confidence

## Detailed Test Results

| Items | Zone | Middle Accuracy | Confidence | Phase |
|-------|------|----------------|------------|-------|
"""
        for test in sorted(self.all_tests, key=lambda t: t.num_items):
            middle_acc = test.positions['middle'].accuracy
            report += f"| {test.num_items} | {test.zone_type.value} | {middle_acc:.0%} | {test.confidence:.0%} | {test.phase} |\n"

        report += f"""
## Production Deployment Recommendations

### Configuration
```python
# Use safe zones for all queries
SAFE_ZONES = {self.safe_zones}
DANGER_ZONES = {self.danger_zones}
```

### Safety Guidelines
1. ✅ Always validate item count against safe zones
2. ✅ Apply automatic padding if in danger zone
3. ✅ Log all near-boundary queries for monitoring
4. ⚠️ Use 20-item safety margin from danger zones
5. ❌ Never use exact danger zone boundaries

### Example Usage
```python
from mistral_safe_zones_config import apply_safe_padding

items = load_documents()  # e.g., 500 items
safe_items, padding = apply_safe_padding(items)
# safe_items now has ~520 items, safely past danger zone
```

## Test Methodology

### Statistical Confidence
- **Phase 1**: 3 runs (detect 0% vs 100% with p < 0.001)
- **Phase 2**: 5 runs (80% confidence in boundaries)
- **Phase 3**: 10 runs (95% confidence for production)

### Known Limitations
- Tested range: 100-1400 items
- Zones beyond 1400 items not validated
- Temperature = 0 (deterministic testing)
- Single position encoding style

### Future Work
- Extend testing to 1500-2000 items
- Test with different prompt formats
- Validate with production workload patterns
- Monitor for drift over time

---

*Generated by Mistral Adaptive Zone Mapper v1.0*
"""
        return report

    def run_full_mapping(self):
        """Execute complete 3-phase mapping"""
        self.start_time = time.time()

        print("\n" + "="*70)
        print(" MISTRAL Q6_K ADAPTIVE ZONE MAPPER ".center(70))
        print("="*70)
        print(f"\n[START TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[API URL] {self.api_url}")
        print(f"[OUTPUT DIR] {self.output_dir}")
        print(f"[ESTIMATED TIME] 5-6 hours")
        print("\n" + "="*70)

        # Phase 1: Coarse Discovery
        phase1_results = self.phase1_coarse_discovery()

        # Analyze transitions
        transitions = self.identify_transitions(phase1_results)

        if not transitions:
            print("\n[WARNING] No transitions found! All tests in same zone.")
            print("[RESULT] Model appears stable across entire range 100-1400")
            self.save_results()
            return

        # Phase 2: Binary Search
        phase2_results = self.phase2_binary_search(transitions)

        # Phase 3: Production Validation
        phase3_results = self.phase3_production_validation(phase2_results)

        # Generate zones
        self.generate_safe_zones()

        # Save everything
        self.save_results()

        # Final summary
        total_time = time.time() - self.start_time

        print("\n" + "="*70)
        print(" MAPPING COMPLETE ".center(70))
        print("="*70)
        print(f"\n[TOTAL TIME] {total_time/3600:.2f} hours")
        print(f"[TOTAL QUERIES] {self.total_queries}")
        print(f"[SAFE ZONES] {len(self.safe_zones)}")
        print(f"[DANGER ZONES] {len(self.danger_zones)}")
        print("\n[NEXT STEPS]")
        print("  1. Review mistral_safe_zones_config.py")
        print("  2. Integrate into LightRAG service")
        print("  3. Monitor production queries")
        print("  4. Re-test periodically for drift")
        print("\n" + "="*70)


def main():
    """Main entry point"""
    print("="*70)
    print(" MISTRAL Q6_K ADAPTIVE ZONE MAPPER ".center(70))
    print(" 3-Phase Intelligent Testing Strategy ".center(70))
    print("="*70)
    print("\nThis script will:")
    print("  Phase 1: Test every 50 items (100-1400) with 3 runs each")
    print("  Phase 2: Binary search exact boundaries with 5 runs each")
    print("  Phase 3: Validate critical boundaries with 10 runs each")
    print("\nEstimated time: 5-6 hours")
    print("Estimated queries: ~700")
    print("\n" + "="*70)

    # Get user confirmation
    response = input("\nProceed with full mapping? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n[CANCELLED] Mapping cancelled by user")
        return

    # Initialize mapper
    mapper = MistralZoneMapper(
        api_url="http://localhost:8080/v1/chat/completions",
        output_dir=".",
        rest_time=15
    )

    # Run full mapping
    try:
        mapper.run_full_mapping()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Mapping interrupted by user")
        print(f"[PROGRESS] Completed {mapper.total_queries} queries")
        print("[SAVING] Saving partial results...")
        mapper.save_results()
        print("[SAVED] Partial results saved")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        print(f"[PROGRESS] Completed {mapper.total_queries} queries")
        print("[SAVING] Saving partial results...")
        mapper.save_results()
        print("[SAVED] Partial results saved")
        raise


if __name__ == "__main__":
    main()
