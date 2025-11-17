#!/usr/bin/env python3
"""
Calculate comment coverage for Python files.
Formula: (comment_lines / (total_lines - blank_lines)) * 100
"""

import sys
from pathlib import Path


def count_lines(file_path: Path) -> tuple[int, int, int]:
    """
    Count lines in a Python file.

    Returns:
        (total_lines, blank_lines, comment_lines)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    blank_lines = 0
    comment_lines = 0
    in_docstring = False
    docstring_delimiter = None

    for line in lines:
        stripped = line.strip()

        # Count blank lines
        if not stripped:
            blank_lines += 1
            continue

        # Handle docstrings (multi-line comments)
        if '"""' in line or "'''" in line:
            delimiter = '"""' if '"""' in line else "'''"
            count = line.count(delimiter)

            if not in_docstring:
                # Starting a docstring
                in_docstring = True
                docstring_delimiter = delimiter
                comment_lines += 1

                # Check if docstring ends on same line
                if count >= 2:
                    in_docstring = False
                    docstring_delimiter = None
            else:
                # Ending a docstring
                if delimiter == docstring_delimiter:
                    in_docstring = False
                    docstring_delimiter = None
                    comment_lines += 1
            continue

        # If we're inside a docstring, count this line as a comment
        if in_docstring:
            comment_lines += 1
            continue

        # Handle single-line comments
        if stripped.startswith('#'):
            comment_lines += 1
            continue

    return total_lines, blank_lines, comment_lines


def calculate_coverage(file_path: Path) -> float:
    """Calculate comment coverage percentage."""
    total, blank, comment = count_lines(file_path)
    code_lines = total - blank

    if code_lines == 0:
        return 0.0

    coverage = (comment / code_lines) * 100

    print(f"\n{file_path.name}")
    print(f"  Total lines: {total}")
    print(f"  Blank lines: {blank}")
    print(f"  Code lines: {code_lines}")
    print(f"  Comment lines: {comment}")
    print(f"  Coverage: {coverage:.2f}%")

    return coverage


if __name__ == "__main__":
    files = [
        Path("app/models/database.py"),
        Path("app/db/session.py"),
        Path("app/config.py"),
    ]

    coverages = []
    for file in files:
        if file.exists():
            coverage = calculate_coverage(file)
            coverages.append((file.name, coverage))
        else:
            print(f"File not found: {file}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, coverage in coverages:
        status = "PASS" if coverage >= 40 else "FAIL"
        print(f"{name:30} {coverage:6.2f}%  {status}")

    print(f"{'='*60}")
    avg_coverage = sum(c for _, c in coverages) / len(coverages) if coverages else 0
    print(f"Average coverage: {avg_coverage:.2f}%")
    print(f"Target: 40.00%")
