/*
 * @lc app=leetcode id=918 lang=cpp
 *
 * [918] Maximum Sum Circular Subarray
 */
// Translated from 918.maximum-sum-circular-subarray.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=918 lang=python3
// #
// # [918] Maximum Sum Circular Subarray
// #
// 
// # =============================================================================
// # INTERVIEW: ELEVATOR PITCH (~30 seconds)
// # =============================================================================
// #
// # "The array is circular: the last element connects to the first. Either our best
// # segment does **not** wrap — then it's ordinary maximum-subarray (Kadane). Or it
// # **does** wrap — then we're taking **everything except** one contiguous block we
// # skip; maximizing that is equivalent to **total sum minus minimum-subarray sum**.
// # One linear scan can track both max-subarray and min-subarray; combine answers,
// # with one guard when **all numbers are negative** (can't take empty complement)."
// #
// # =============================================================================
// # PROBLEM — WHAT ARE WE OPTIMIZING?
// # =============================================================================
// #
// # Given nums (possibly negative integers), find the maximum possible sum of a
// # contiguous subarray when we are allowed to treat the array as a **ring**: index
// # after n−1 wraps to 0.
// #
// # Equivalently: choose indices i, j and a length L such that we take L consecutive
// # cells walking forward with wrap — sum nums[i], nums[(i+1)%n], … for L terms.
// #
// # =============================================================================
// # WHY TWO CASES (WRAP vs NO WRAP)?
// # =============================================================================
// #
// # Case A — **No wrap**
// # The optimal indices form an ordinary contiguous interval on the line [0, n−1].
// # This is exactly **maximum subarray sum** → **Kadane's algorithm** in O(n).
// #
// # Case B — **Wrap**
// # Visualize the circle: if the chosen arc crosses the "cut" between n−1 and 0,
// # then as a **linear** array we are taking **two** segments: a suffix [i..n−1] and
// # a prefix [0..j]. Together they cover **all indices except** a contiguous gap in
// # the middle (the indices we did **not** pick).
// #
// # Let T = sum(nums). If we skip a contiguous block with sum S_min (the minimum-sum
// # subarray on the **linear** array), what we keep sums to **T − S_min**.
// #
// # So: **best circular** = **T − (minimum subarray sum)** when that interpretation is
// # valid.
// #
// # =============================================================================
// # CRITICAL EDGE CASE — ALL ELEMENTS NEGATIVE
// # =============================================================================
// #
// # If every nums[k] < 0, the **minimum** subarray might be the **entire array** (sum T).
// # Then T − T = 0, which would pretend an empty subarray is allowed — but we must pick
// # **at least one** element. The circular formula is **invalid** here.
// #
// # In that situation the answer is simply **max(nums)** — the single least bad element,
// # which Kadane's **maximum** already returns as max_sum (since every extension drops).
// #
// # Detect: when **max_sum < 0** (equivalently no positive-sum subarray exists), return
// # **max_sum** only. When **max_sum ≥ 0**, compare Kadane max with **T − min_sum**.
// #
// # (Another equivalent guard: if max_sum > 0, use max(max_sum, T - min_sum); else
// # return max_sum — implemented below.)
// #
// # =============================================================================
// # ALGORITHM — ONE PASS
// # =============================================================================
// #
// # Initialize:
// #   total      ← sum of all nums (second loop can merge with kadane; one loop enough)
// #   cur_max, max_sum ← Kadane state for **maximum** subarray ending here / global max
// #   cur_min, min_sum ← Kadane state for **minimum** subarray ending here / global min
// #
// # For each x in nums (same recurrence as classic Kadane for max and min):
// #   cur_max ← max(x, cur_max + x)
// #   max_sum ← max(max_sum, cur_max)
// #   cur_min ← min(x, cur_min + x)
// #   min_sum ← min(min_sum, cur_min)
// #
// # Combine:
// #   if max_sum > 0:
// #       return max(max_sum, total - min_sum)
// #   else:
// #       return max_sum
// #
// # =============================================================================
// # WHY THIS IS O(n) TIME / O(1) EXTRA SPACE
// # =============================================================================
// #
// # Each element is processed once; only O(1) scalars maintained → **O(n)** time,
// # **O(1)** auxiliary space (excluding the input array).
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # None beyond a handful of integers — **no prefix arrays, heaps, or deques**.
// # Kadane is the canonical choice because subarray optimality for fixed endpoints is
// # **local** (extend or restart).
// #
// # =============================================================================
// # CORRECTNESS SKETCH
// # =============================================================================
// #
// # • Kadane max is optimal among non-wrapping contiguous subarrays (standard proof).
// # • For wrapping optimum: removing exactly one contiguous "hole" minimizes removed sum
// #   iff that hole is the **minimum-sum** subarray (among contiguous holes). Remaining
// #   sum = T − min_sum is maximal.
// # • When max_sum ≤ 0, every prefix extension is harmful → optimum is a single
// #   element; circular trick gives 0 → rejected by guard.
// #
// # =============================================================================
// # TESTS & EDGE CASES (mental / unit)
// # =============================================================================
// #
// # • [5,-3,5] → linear max 7 ([5,-3,5]); circular max 10 ([5] + wrap [5]). OK.
// # • [3,-1,2,-1] → answer 4 (several placements).
// # • [-3,-2,-3] → max element -2 (not 0).
// # • [1] → 1.
// # • [6,-4,6] → compare Kadane vs wrap.
// #
// # Regression: brute force O(n²) all contiguous arcs on doubled array for small n vs O(n).
// #
// # =============================================================================
// # ALTERNATIVES / IMPROVEMENTS
// # =============================================================================
// #
// # • **Duplicate array**: concatenate nums+nums, sliding window length ≤ n — O(n²)
// #   or with monotonic deque optimizations — still heavier than dual Kadane.
// # • **Prefix sums**: can derive same formulas; Kadane is simpler on the whiteboard.
// #
// # =============================================================================
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def maxSubarraySumCircular(self, nums: List[int]) -> int:
//         """
//         Maximum sum of a contiguous subarray on a circular array.
// 
//         Combines Kadane maximum (no wrap) with total - Kadane minimum (wrap).
//         When no positive-sum window exists, answer is max(nums) via Kadane max alone.
//         """
//         cur_max = cur_min = nums[0]
//         max_sum = min_sum = nums[0]
//         total = nums[0]
//         for x in nums[1:]:
//             total += x
//             cur_max = max(x, cur_max + x)
//             max_sum = max(max_sum, cur_max)
//             cur_min = min(x, cur_min + x)
//             min_sum = min(min_sum, cur_min)
// 
//         # Non-positive overall best → cannot use "remove middle" trick (would imply empty pick).
//         if max_sum > 0:
//             return max(max_sum, total - min_sum)
//         return max_sum
// 
// 
// # lc-original code=end

// @lc code=start
#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
public:
    int maxSubarraySumCircular(vector<int>& nums) {
        int curMax = nums[0], curMin = nums[0], maxSum = nums[0], minSum = nums[0], total = nums[0];
        for (int i = 1; i < (int)nums.size(); ++i) {
            int x = nums[i];
            total += x;
            curMax = max(x, curMax + x);
            maxSum = max(maxSum, curMax);
            curMin = min(x, curMin + x);
            minSum = min(minSum, curMin);
        }
        return maxSum > 0 ? max(maxSum, total - minSum) : maxSum;
    }
};
// @lc code=end
