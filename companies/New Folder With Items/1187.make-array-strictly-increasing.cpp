/*
 * @lc app=leetcode id=1187 lang=cpp
 *
 * [1187] Make Array Strictly Increasing
 */
// Translated from 1187.make-array-strictly-increasing.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1187 lang=python3
// #
// # [1187] Make Array Strictly Increasing
// #
// 
// # --- Interview notes (DP on last value, greedy replacement, bisect, complexity, proofs sketch, edges, tests) ---
// #
// # Problem
// # Integer arrays `arr1` (target positions) and `arr2` (replacement palette). In one operation you may replace **any**
// # element of `arr1` with **any** single value from `arr2` (same value may be reused arbitrarily — unlimited supply).
// # Minimize the number of replacements so that `arr1` becomes **strictly** increasing. Return `-1` if impossible.
// #
// # Why track only the previous value (last element after fixing the prefix)
// # When deciding position `i`, every admissible completion depends only on the **last written value** `prev` after fixing
// # indices `< i`, because strict increase only constrains `next > prev`. Earlier history beyond `prev` does not affect
// # feasibility or future costs — optimal substructure.
// #
// # DP state
// # After processing the first `k` positions of `arr1`, maintain a map:
// #   `dp[v] = minimum operations used so far`, where `v` is the **last element value** of the constructed prefix (among
// #   finitely many candidates — values that appear as original `arr1` entries or elements from `arr2`).
// # Initialize `dp = { -∞ : 0 }` with a sentinel smaller than all integers so the first position accepts any value.
// #
// # Transitions for current `a = arr1[i]`
// # From each `(prev, cost)` in `dp`:
// # (1) **Keep** `a` if `prev < a` → candidate state `(last=a, cost)` with same cost.
// # (2) **Replace** `a` with some `x ∈ arr2` with `x > prev`. Among all such `x`, choosing the **smallest** `x > prev`
// #     dominates: it uses one operation like any replacement but leaves the tail **as small as possible**, maximizing room for
// #     future strict increases (exchange argument — any solution using a larger replacement can be modified without increasing
// #     cost).
// # Implementation: sort/deduplicate `arr2`, then `x = arr2[bisect_right(arr2, prev)]` if that index exists.
// #
// # Merge candidates: multiple `(prev, cost)` pairs may propose the same resulting last value — keep **minimum** cost.
// #
// # Invalidity
// # If after processing a position the map becomes empty, no `(prev, cost)` allowed this step → return `-1`.
// #
// # Answer
// # After the last index, `min(dp.values())` is the minimum replacement count.
// #
// # Data structures
// # • **Sorted unique `arr2`** — enables binary search for the smallest usable replacement in `O(log |arr2|)`.
// # • **Hash map `dict`** — sparse DP over candidate last values; typically `O(|arr2| + 1)` keys per layer in practice.
// #
// # Time complexity
// # Let `n = len(arr1)`, `m = len(arr2)` after dedup/sort. Each of `n` layers iterates all `dp` entries (≤ `O(m)` distinct
// # tails in typical paths) and does `O(log m)` bisect → **O(n · |dp| · log m)** worst case; often bounded by **O(n · m · log m)**.
// #
// # Space complexity
// # **O(|dp|)** per layer — **O(m)** typical — plus **O(m)** for sorted `arr2`.
// #
// # Edge cases
// # • `len(arr1) == 1` → **0** operations (single element is trivially strictly increasing).
// # • `arr2` empty → only “keep” transitions possible; sequence must already be strictly increasing or answer `-1`.
// # • Duplicate values in `arr2` — sorting **unique** values does not remove feasible replacements (duplicates never beat the
// #   first copy for “smallest `x > prev`”).
// #
// # Official-style tests (LeetCode)
// # • `arr1 = [1,5,3,6,7]`, `arr2 = [1,3,2,4]` → **1** (e.g. replace `5` with `2` → `[1,2,3,6,7]`).
// # • `arr1 = [1,5,3,6,7]`, `arr2 = [4,3,1]` → **2** (e.g. replace `5→3`, `3→4` → `[1,3,4,6,7]`).
// # • `arr1 = [1,5,3,6,7]`, `arr2 = [1,6,3,3]` → **-1** (impossible).
// #
// # Improvements / variants
// # • **Coordinate compress** candidate values if ranges huge — same logic.
// # • **List-of-(value,cost)** sorted by value per layer — alternate implementation for cache locality.
// # • Brute force over subsets only works for tiny `n`; DP + greedy replacement is the standard interview solution.
// #
// # --- end notes ---
// 
// # lc-original code=start
// import bisect
// from typing import List
// 
// 
// class Solution:
//     def makeArrayIncreasing(self, arr1: List[int], arr2: List[int]) -> int:
//         arr2 = sorted(set(arr2))
//         neg_inf = -(10**18)
//         dp = {neg_inf: 0}
// 
//         for a in arr1:
//             nxt = {}
//             for prev, cost in dp.items():
//                 if prev < a:
//                     ca = nxt.get(a)
//                     if ca is None or cost < ca:
//                         nxt[a] = cost
//                 j = bisect.bisect_right(arr2, prev)
//                 if j < len(arr2):
//                     x = arr2[j]
//                     nc = cost + 1
//                     cx = nxt.get(x)
//                     if cx is None or nc < cx:
//                         nxt[x] = nc
//             dp = nxt
//             if not dp:
//                 return -1
// 
//         return min(dp.values())
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
    int makeArrayIncreasing(vector<int>& arr1, vector<int>& arr2) {
        sort(arr2.begin(), arr2.end());
        arr2.erase(unique(arr2.begin(), arr2.end()), arr2.end());
        const int NEG = -1000000000;
        map<int, int> dp{{NEG, 0}};
        for (int a : arr1) {
            map<int, int> nxt;
            for (auto [prev, cost] : dp) {
                if (prev < a) {
                    if (!nxt.count(a) || cost < nxt[a]) nxt[a] = cost;
                }
                auto it = upper_bound(arr2.begin(), arr2.end(), prev);
                if (it != arr2.end()) {
                    int x = *it, nc = cost + 1;
                    if (!nxt.count(x) || nc < nxt[x]) nxt[x] = nc;
                }
            }
            dp.swap(nxt);
            if (dp.empty()) return -1;
        }
        int ans = INT_MAX;
        for (auto [_, cost] : dp) ans = min(ans, cost);
        return ans;
    }
};
// @lc code=end
