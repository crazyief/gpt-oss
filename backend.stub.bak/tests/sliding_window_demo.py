#!/usr/bin/env python3
"""
Simple demo to show how sliding window works
簡單示範滑動窗口如何運作
"""

def visualize_sliding_window():
    """視覺化展示滑動窗口"""

    # 假設文檔有 100 個段落
    document = [f"Section {i}" for i in range(1, 101)]

    window_size = 30  # 每個窗口 30 個段落
    overlap = 10      # 重疊 10 個段落
    stride = window_size - overlap  # 每次移動 20 個段落

    windows = []
    position = 0

    print("原始文檔: 100 個段落 (Section 1 - Section 100)")
    print("="*60)

    window_num = 1
    while position < len(document):
        # 取出這個窗口的內容
        window_end = min(position + window_size, len(document))
        window = document[position:window_end]
        windows.append(window)

        print(f"\n窗口 {window_num}:")
        print(f"  範圍: Section {position+1} 到 Section {window_end}")
        print(f"  內容: {window[0]} ... {window[-1]}")
        print(f"  大小: {len(window)} 段落")

        if window_num > 1:
            # 計算與前一個窗口的重疊
            overlap_start = max(0, position)
            overlap_end = min(position + overlap, len(document))
            print(f"  重疊: Section {overlap_start+1} 到 Section {overlap_end} (與前一窗口)")

        position += stride  # 移動到下一個窗口
        window_num += 1

        if window_end >= len(document):
            break

    print("\n" + "="*60)
    print(f"總共切成 {len(windows)} 個窗口")
    print(f"每個窗口 {window_size} 段落，重疊 {overlap} 段落")

    return windows


def simulate_api_calls(windows, target="Section 75"):
    """模擬對每個窗口進行 API 調用"""

    print(f"\n尋找目標: {target}")
    print("="*60)

    api_calls = 0
    found_windows = []

    for i, window in enumerate(windows, 1):
        api_calls += 1

        # 模擬 API 調用
        print(f"\nAPI Call #{api_calls} - 窗口 {i}:")
        print(f"  查詢範圍: {window[0]} - {window[-1]}")

        # 檢查目標是否在這個窗口
        if target in window:
            print(f"  [FOUND] 找到 {target}！")
            found_windows.append(i)
        else:
            print(f"  [NOT FOUND] 未找到")

    print("\n" + "="*60)
    print(f"總結:")
    print(f"  - 總共進行了 {api_calls} 次 API 調用")
    print(f"  - 在窗口 {found_windows} 找到目標")

    return api_calls, found_windows


def compare_methods():
    """比較不同方法的差異"""

    print("\n" + "="*70)
    print("方法比較：處理 100k tokens 文檔")
    print("="*70)

    print("\n[X] 方法 1: 直接查詢（會失敗）")
    print("  - 嘗試一次送入 100k tokens")
    print("  - 結果: ERROR - 超過 32k 限制！")

    print("\n[O] 方法 2: 滑動窗口（可行）")
    print("  - 切成 5 個 20k 的窗口（有 5k 重疊）")
    print("  - 進行 5 次 API 調用")
    print("  - 每次調用只用 20k tokens（在 32k 限制內）")
    print("  - 結果: 成功處理整個文檔！")

    print("\n[成本分析]:")
    print("  方法 1: 1 次調用 x 100k = 無法執行")
    print("  方法 2: 5 次調用 x 20k = 100k tokens（分批）")

    print("\n[時間分析]:")
    print("  方法 1: 無法執行")
    print("  方法 2: 5 次調用 x 2秒 = 約 10 秒")

    print("\n[優缺點]:")
    print("  優點: 可處理任意大小文檔、不受 context 限制")
    print("  缺點: 需要多次 API 調用、時間較長、成本較高")


if __name__ == "__main__":
    print("滑動窗口技術演示")
    print("="*70)

    # 1. 視覺化窗口切割
    windows = visualize_sliding_window()

    # 2. 模擬 API 調用
    simulate_api_calls(windows)

    # 3. 方法比較
    compare_methods()

    print("\n" + "="*70)
    print("[關鍵理解]:")
    print("  1. 滑動窗口把大問題變成多個小問題")
    print("  2. 每個小問題都在 model 的能力範圍內")
    print("  3. 重疊確保不會遺漏邊界資訊")
    print("  4. 最後合併所有答案得到完整結果")