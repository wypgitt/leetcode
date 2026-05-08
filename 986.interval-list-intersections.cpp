// Translated from 986.interval-list-intersections.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=986 lang=python3
// #
// # [986] Interval List Intersections
// #
// 
// # --- Interview notes (two sorted lists, intersection formula, advance rule, complexity, edges) ---
// #
// # Problem
// # **`firstList`** and **`secondList`** are **sorted**, pairwise **non-overlapping**, closed intervals **`[start, end]`**.
// # Return **all non-empty intersections** between some interval from **`firstList`** and some interval from **`secondList`**,
// # as a sorted list (natural merge order from the linear scan).
// #
// # Geometry of one pair
// # For **`A = [a0, a1]`** and **`B = [b0, b1]`**, the overlap is **`[max(a0, b0), min(a1, b1)]`**. It is **non-empty** iff
// # **`max(a0, b0) ≤ min(a1, b1)`** (closed intervals).
// #
// # Why two pointers (merge-intersect pattern)
// # Like merging sorted arrays, at each step only **current** **`firstList[i]`** and **`secondList[j]`** can produce a new intersection
// # involving “the next” uncovered overlap — earlier intervals are already finished because lists are sorted by start time.
// #
// # Advance rule (discard the interval that ends first)
// # After recording an overlap (if any), move **`i`** if **`firstList[i]` ends before **`secondList[j]`**, else move **`j`**.
// # The interval that finishes **earlier** cannot intersect **future** intervals from the other list beyond that cutoff — only the
// # longer-span partner might still overlap the **next** interval on the other side.
// # When **`a1 == b1`**, advancing **`j`** (or symmetrically **`i`**) is standard; both intervals are exhausted at the same
// # coordinate for overlap purposes with each other (next pair picks up fresh intervals).
// #
// # Data structures
// # Output **`res`** list only — **O(k)** for **`k`** intersection segments. No heaps or segment trees needed.
// #
// # Time complexity **O(m + n)`** — each pointer moves strictly forward, **`m = len(firstList)`**, **`n = len(secondList)`**.
// #
// # Space complexity **O(1)** auxiliary excluding the answer list (**O(k)** output).
// #
// # Edge cases
// # • Either list **empty** → **no** intersections → **`[]`**.
// # • Single-point overlap **`[5,5]`** — still valid closed interval if **`max ≤ min`** with equality.
// #
// # Tests (LeetCode Example 1)
// # • **`firstList = [[0,2],[5,10],[13,23],[24,25]]`**, **`secondList = [[1,5],[8,12],[15,24],[25,26]]`** → six overlapping segments
// #   **`[[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]`**.
// #
// # Improvements
// # • If intervals were half-open **`[l, r)`**, intersection formula adjusts endpoints accordingly — same pointer skeleton.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def intervalIntersection(
//         self, firstList: List[List[int]], secondList: List[List[int]]
//     ) -> List[List[int]]:
//         i, j = 0, 0
//         out: List[List[int]] = []
//         while i < len(firstList) and j < len(secondList):
//             a0, a1 = firstList[i]
//             b0, b1 = secondList[j]
//             lo = max(a0, b0)
//             hi = min(a1, b1)
//             if lo <= hi:
//                 out.append([lo, hi])
//             if a1 < b1:
//                 i += 1
//             else:
//                 j += 1
//         return out
// 
// 
// # @lc code=end

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
    vector<vector<int>> intervalIntersection(vector<vector<int>>& firstList, vector<vector<int>>& secondList) {
        int i = 0, j = 0;
        vector<vector<int>> out;
        while (i < (int)firstList.size() && j < (int)secondList.size()) {
            int lo = max(firstList[i][0], secondList[j][0]);
            int hi = min(firstList[i][1], secondList[j][1]);
            if (lo <= hi) out.push_back({lo, hi});
            if (firstList[i][1] < secondList[j][1]) ++i;
            else ++j;
        }
        return out;
    }
};
