/*
 * @lc app=leetcode id=1007 lang=cpp
 *
 * [1007] Minimum Domino Rotations For Equal Row
 */
// Translated from 1007.minimum-domino-rotations-for-equal-row.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1007 lang=python3
// #
// # [1007] Minimum Domino Rotations For Equal Row
// #
// 
// # --- Interview notes (two candidates, counting, formula n - max(cnt), complexity, edges) ---
// #
// # Problem
// # `tops[i]` and `bottoms[i]` are the two faces of domino `i` (values in `1..6`). You may swap the two faces on any domino
// # (rotation). Minimize the number of rotations so that **either** every `tops[i]` equals the same value **or** every
// # `bottoms[i]` equals the same value. Return `-1` if impossible.
// #
// # Key observation — only two target values are possible
// # If after all moves some row is all equal to `x`, then **every** domino must display `x` on at least one face (otherwise
// # that domino can never contribute `x` to either row). In particular, domino `0` must contain `x`, so `x ∈ {tops[0],
// # bottoms[0]}`. No other value can be the uniform row value — we only need to try **`x = tops[0]`** and **`x = bottoms[0]`**
// # (when equal, both checks coincide).
// #
// # Feasibility for a fixed target `x`
// # Scan all indices: if for some `i`, `x ∉ {tops[i], bottoms[i]}`, value `x` is impossible for that row goal → reject `x`.
// #
// # Minimum rotations for a feasible `x`
// # Let `c1` = count of indices with `tops[i] == x`, `c2` = count with `bottoms[i] == x`.
// # • To make **top** row all `x`: positions already correct need `0` flips; each other position must have `x` on bottom so we
// #   rotate once → **`n - c1`** rotations.
// # • To make **bottom** row all `x`: symmetrically **`n - c2`** rotations.
// # We may achieve either goal, so **`f(x) = min(n - c1, n - c2) = n - max(c1, c2)`**.
// #
// # Algorithm
// # `answer = min(f(tops[0]), f(bottoms[0]))`, treating impossible candidate as `+∞`. If answer infinite → `-1`.
// #
// # Why no extra data structures
// # Two linear scans (or one helper invoked twice) — **O(1)** beyond input arrays.
// #
// # Time complexity **O(n)** with `n = len(tops)`.
// #
// # Space complexity **O(1)** auxiliary (only counters / `inf`).
// #
// # Edge cases
// # • All dominoes already show the same value on top — `c1 == n` → **0** rotations for top row.
// # • `tops[0] == bottoms[0]` — still run `f` twice or early dedupe; result unchanged.
// #
// # Tests (statement)
// # • `tops = [2,1,2,4,2,2]`, `bottoms = [5,2,6,2,3,2]` → **2**.
// # • `tops = [3,5,1,2,3]`, `bottoms = [3,6,3,3,4]` → **-1**.
// #
// # Improvements
// # • If `tops[0] == bottoms[0]`, evaluate **`f` once**.
// # • Values bounded by **6** — could bit-mask count, but unnecessary with **O(n)** scan.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def minDominoRotations(self, tops: List[int], bottoms: List[int]) -> int:
//         n = len(tops)
// 
//         def min_rotations_for_target(x: int) -> int:
//             c1 = c2 = 0
//             for a, b in zip(tops, bottoms):
//                 if x != a and x != b:
//                     return float("inf")
//                 c1 += a == x
//                 c2 += b == x
//             return n - max(c1, c2)
// 
//         ans = min(min_rotations_for_target(tops[0]), min_rotations_for_target(bottoms[0]))
//         return -1 if ans == float("inf") else int(ans)
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
    int minDominoRotations(vector<int>& tops, vector<int>& bottoms) {
        int n = (int)tops.size();
        const int INF = 1e9;
        auto cost = [&](int x) {
            int topMatches = 0, bottomMatches = 0;
            for (int i = 0; i < n; ++i) {
                if (tops[i] != x && bottoms[i] != x) return INF;
                topMatches += tops[i] == x;
                bottomMatches += bottoms[i] == x;
            }
            return n - max(topMatches, bottomMatches);
        };
        int ans = min(cost(tops[0]), cost(bottoms[0]));
        return ans == INF ? -1 : ans;
    }
};
// @lc code=end
