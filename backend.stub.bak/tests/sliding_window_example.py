#!/usr/bin/env python3
"""
Simple English demo showing how sliding window works
"""

def demonstrate_sliding_window():
    """Show how sliding window breaks down large documents"""

    print("=" * 70)
    print("SLIDING WINDOW TECHNIQUE EXPLAINED")
    print("=" * 70)

    # Simulate a large document
    print("\n[SCENARIO]")
    print("You have a 100,000 token document (IEC 62443 complete)")
    print("But Mistral can only handle 32,000 tokens at once")

    print("\n[PROBLEM]")
    print("100,000 tokens > 32,000 token limit = ERROR!")

    print("\n[SOLUTION: Sliding Window]")
    print("Break document into overlapping chunks:")
    print("")
    print("Original: [============================================] 100k tokens")
    print("")
    print("Window 1: [===========].................................. 0-20k")
    print("Window 2: ........[===========]........................... 15k-35k")
    print("Window 3: ..................[===========]................. 30k-50k")
    print("Window 4: ............................[===========]...... 45k-65k")
    print("Window 5: .......................................[======] 60k-80k")
    print("Window 6: ...........................................[==] 75k-100k")
    print("")
    print("          ^ Notice 5k overlap between windows")

    print("\n[HOW IT WORKS]")
    print("1. Split document into 20k token windows")
    print("2. Each window overlaps by 5k tokens")
    print("3. Send each window to API separately")
    print("4. Collect all responses")
    print("5. Merge results into final answer")

    return True


def show_api_calls_example():
    """Show actual API calls needed"""

    print("\n" + "=" * 70)
    print("API CALLS EXAMPLE")
    print("=" * 70)

    print("\nQuestion: 'What is requirement CR 2.11 in IEC 62443?'")
    print("\nProcessing each window:")
    print("")

    windows = [
        ("Window 1 (0-20k)", "Pages 1-40", False, "Not found"),
        ("Window 2 (15k-35k)", "Pages 30-70", False, "Not found"),
        ("Window 3 (30k-50k)", "Pages 60-100", True, "CR 2.11: Secure remote access..."),
        ("Window 4 (45k-65k)", "Pages 90-130", True, "CR 2.11 continued: Authentication..."),
        ("Window 5 (60k-80k)", "Pages 120-160", False, "Not found"),
        ("Window 6 (75k-100k)", "Pages 150-200", False, "Not found"),
    ]

    api_count = 0
    found_answers = []

    for window, pages, has_answer, response in windows:
        api_count += 1
        print(f"API Call #{api_count}:")
        print(f"  Sending: {window} ({pages})")
        print(f"  Response: {response}")

        if has_answer:
            print(f"  Status: [FOUND]")
            found_answers.append((window, response))
        else:
            print(f"  Status: [NOT FOUND]")
        print("")

    print("-" * 70)
    print(f"Total API calls made: {api_count}")
    print(f"Windows with answers: {len(found_answers)}")

    if found_answers:
        print("\nFinal merged answer:")
        print("CR 2.11 Requirements (from Windows 3 & 4):")
        print("- Secure remote access control")
        print("- Multi-factor authentication required")
        print("- Session timeout mechanisms")

    return api_count


def compare_approaches():
    """Compare different approaches"""

    print("\n" + "=" * 70)
    print("COMPARISON: Direct vs Sliding Window")
    print("=" * 70)

    print("\n[Approach 1: Direct Query]")
    print("  Input: 100,000 tokens in one request")
    print("  Result: ERROR - Exceeds 32k limit!")
    print("  Status: FAILED")

    print("\n[Approach 2: Sliding Window]")
    print("  Input: 6 windows x 20,000 tokens each")
    print("  Result: All windows processed successfully")
    print("  Status: SUCCESS")

    print("\n[Cost Analysis]")
    print("  Direct: Cannot execute (too large)")
    print("  Sliding: 6 API calls = 6x cost but WORKS")

    print("\n[Time Analysis]")
    print("  Direct: N/A (fails immediately)")
    print("  Sliding: 6 calls x 2 sec = ~12 seconds total")

    print("\n[Accuracy]")
    print("  Direct: 0% (cannot run)")
    print("  Sliding: 100% (finds all information)")


def practical_example():
    """Show practical use case"""

    print("\n" + "=" * 70)
    print("PRACTICAL EXAMPLE FOR YOUR PROJECT")
    print("=" * 70)

    print("\n[Your Scenario]")
    print("- IEC 62443 complete standard: ~300 pages")
    print("- Approximately 150,000 tokens")
    print("- Mistral limit: 32,000 tokens")

    print("\n[Without Sliding Window]")
    print("- Can only process first 60-70 pages")
    print("- Missing 70% of the document!")

    print("\n[With Sliding Window]")
    print("- Process entire 300 pages in 8 windows")
    print("- Each window: ~20k tokens (40 pages)")
    print("- Overlap ensures nothing missed")

    print("\n[Example Query]")
    print("User: 'Compare all authentication requirements in IEC 62443'")
    print("")
    print("Window 1: Found CR 1.1, CR 1.2")
    print("Window 2: Found CR 2.11")
    print("Window 3: Found CR 3.5")
    print("...")
    print("Window 8: Found CR 7.3")
    print("")
    print("Final Answer: Complete list of all authentication requirements!")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_sliding_window()
    api_count = show_api_calls_example()
    compare_approaches()
    practical_example()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAY")
    print("=" * 70)
    print("\nSliding Window allows you to:")
    print("1. Process documents of ANY size (100k, 500k, 1M tokens)")
    print("2. Work within model's context limit")
    print("3. Never lose information (overlapping ensures coverage)")
    print("4. Trade time/cost for capability")
    print("\nDownside: Multiple API calls = more time & cost")
    print("Upside: Can handle unlimited document size!")