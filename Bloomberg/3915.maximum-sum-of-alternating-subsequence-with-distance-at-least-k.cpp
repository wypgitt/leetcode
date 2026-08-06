/*
 * @lc app=leetcode id=3915 lang=cpp
 *
 * [3915] Maximum Sum of Alternating Subsequence With Distance At Least K
 */
// Translated from 3915.maximum-sum-of-alternating-subsequence-with-distance-at-least-k.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3915 lang=python3
// #
// # [3915] Maximum Sum of Alternating Subsequence With Distance At Least K
// #
// # =============================================================================
// # OFFICIAL PROBLEM (summary)
// # =============================================================================
// #
// # Pick indices i1 < i2 < … with **i_{t+1} - i_t >= k**. The **values** must form a
// # **strictly alternating** sequence in value space:
// #   either  nums[i1] < nums[i2] > nums[i3] < …
// #   or      nums[i1] > nums[i2] < nums[i3] > …
// # Any single element counts as alternating. The **score** is the **sum** of
// # chosen values (no +/- parity on signs — “alternating” refers to up/down in
// # value, like a zigzag).
// #
// # =============================================================================
// # DP (two states = “last edge direction”)
// # =============================================================================
// #
// # After fixing the last pick at index `j`, only whether **nums[j]** is a **peak**
// # or **valley** among the last two selected values matters for what **nums[i]**
// # may follow (with `i - j >= k`):
// #
// # - **high[j]** = best score of a valid subsequence **ending at j** such that
// #   if length >= 2, the previous value is **< nums[j]**  (“… < nums[j]” — `j` is
// #   a local peak in the value zigzag).
// #
// # - **low[j]**  = best score ending at `j` with previous **> nums[j]** if length >= 2
// #   (“… > nums[j]” — `j` is a local valley).
// #
// # Length-1 subsequence: both **high[j] = low[j] = nums[j]** (either convention).
// #
// # Transitions for `i - j >= k` (strict inequalities on values):
// # - If **nums[j] < nums[i]** we may extend a **valley** at `j` upward → new peak at `i`:
// #     **high[i] = max(high[i], low[j] + nums[i])**
// # - If **nums[j] > nums[i]** we may extend a **peak** at `j` downward → new valley at `i`:
// #     **low[i] = max(low[i], high[j] + nums[i])**
// #
// # Base: **high[i] >= nums[i]**, **low[i] >= nums[i]** (take only index `i`).
// #
// # Answer: **max_i max(high[i], low[i])**.
// #
// # =============================================================================
// # ACCELERATING THE MAX OVER j (segment tree on compressed values)
// # =============================================================================
// #
// # Naive scan over all `j <= i - k` is **O(n^2)**. After processing index `p`,
// # index `p` becomes usable as a predecessor when we reach `i = p + k`. Maintain
// # two max segment trees over **compressed coordinate of nums[p]**:
// #   - tree_low stores at each value coordinate **max low[p]** among inserted `p`;
// #   - tree_high stores **max high[p]** among inserted `p`.
// #
// # At index `i`:
// #   1. If **i >= k**, insert index **i - k** into both trees at **nums[i-k]**.
// #   2. **high[i] = nums[i]**; **low[i] = nums[i]**.
// #   3. **M_lo** = max **low[j]** over inserted `j` with **nums[j] < nums[i]**  
// #      → prefix max on **tree_low** over value coords **[0, pos(nums[i]) - 1]**.
// #      **M_hi** = max **high[j]** over inserted `j` with **nums[j] > nums[i]**  
// #      → range max on **tree_high** over **[pos(nums[i]) + 1, M-1]**.
// #   4. **high[i] = max(high[i], M_lo + nums[i])** if **M_lo** finite;  
// #      **low[i] = max(low[i], M_hi + nums[i])** if **M_hi** finite.
// #
// # **Time O(n log n)**, **space O(n)** (trees + compression).
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - **k = 1**: every adjacent index pair allowed (subject to value zigzag).
// # - **Large k**: only length-1 subsequences → **max(nums)**.
// # - **Equal values**: **nums[j] == nums[i]** forbids extending (strict alternation).
// #
// # =============================================================================
// # COMMON MISTAKE (what went wrong in an earlier draft)
// # =============================================================================
// #
// # Do **not** confuse this with “alternating **sum**” (+a − b + c − … by pick order).
// # Here **alternating** means **strict zigzag of values** (< > < > or > < > <); the
// # objective is **sum of chosen nums[i]**. Example **nums = [5,4,2], k = 2**:
// # pick indices **[0,2]** → values **5 > 2** → score **7**, not **5 − 2**.
// #
// # =============================================================================
// # INTERVIEW TALK TRACK (why this algorithm / data structures)
// # =============================================================================
// #
// # **Why two states (high / low)?**  
// # After the last picked value `v`, the next admissible value is constrained only
// # by whether we must go **up** or **down** from `v`. That is exactly “last step
// # was ascending into `v` (peak)” vs “descending into `v` (valley)”.
// #
// # **Why segment trees (or two Fenwick-style structures), not plain prefix arrays?**  
// # The predecessor `j` must satisfy **value** inequality (`nums[j] < nums[i]` or
// # `>`), not just index order. After restricting to **eligible indices** (inserted
// # in order of `i`), we need **max DP over j with nums[j] in a range of values** —
// # that is a **2D** constraint (index cutoff via sliding eligibility + value range).
// # Coordinate-compress values and use **range max** queries: prefix for `< nums[i]`,
// # suffix for `> nums[i]`.
// #
// # **Why coordinate compression?**  
// # Values are up to 1e5; segment tree size is **O(#distinct values)** ≤ **n**.
// #
// # =============================================================================
// # COMPLEXITY
// # =============================================================================
// #
// # - **Time:** **O(n log n)** — each index: **O(log n)** updates + queries.
// # - **Space:** **O(n)** for DP arrays + **O(m)** for trees (**m** = distinct values).
// #
// # =============================================================================
// # TESTING & VALIDATION
// # =============================================================================
// #
// # For **n ≤ ~15**, brute-force all non-empty index subsets: check gap ≥ **k**,
// # verify zigzag on selected values, compare max sum to the algorithm. Randomized
// # stress tests catch off-by-one on insertion index **i − k** and strict **<** / **>**.
// #
// # =============================================================================
// # POSSIBLE IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # - **Fenwick tree for prefix max** + reversed Fenwick for suffix max (same bounds).
// # - If constraints were tiny, **O(n²)** DP is a correct reference implementation.
// # - **Merge-sort tree** or **balanced BST** could answer the same queries; segment
// #   tree is a standard choice for static compressed coordinates.
// #
// # =============================================================================
// 
// # lc-original code=start
// from typing import List
// 
// 
// class SegTreeMax:
//     """Point update (max-assign), range max query. Iterative; 0-based leaves."""
// 
//     __slots__ = ("n", "size", "neg", "t")
// 
//     def __init__(self, n: int, neg: int = -(10**18)) -> None:
//         self.n = n
//         self.neg = neg
//         size = 1
//         while size < n:
//             size <<= 1
//         self.size = size
//         self.t = [neg] * (2 * size)
// 
//     def update(self, i: int, val: int) -> None:
//         i += self.size
//         self.t[i] = max(self.t[i], val)
//         i >>= 1
//         while i:
//             self.t[i] = max(self.t[2 * i], self.t[2 * i + 1])
//             i >>= 1
// 
//     def query(self, l: int, r: int) -> int:
//         """Max on inclusive [l, r]; empty range returns neg."""
//         if l > r or l < 0 or r >= self.n:
//             if l > r:
//                 return self.neg
//             l = max(l, 0)
//             r = min(r, self.n - 1)
//             if l > r:
//                 return self.neg
//         l += self.size
//         r += self.size
//         res = self.neg
//         while l <= r:
//             if l & 1:
//                 res = max(res, self.t[l])
//                 l += 1
//             if not (r & 1):
//                 res = max(res, self.t[r])
//                 r -= 1
//             l >>= 1
//             r >>= 1
//         return res
// 
// 
// class Solution:
//     def maxAlternatingSum(self, nums: List[int], k: int) -> int:
//         """
//         Maximum sum of a subsequence whose values strictly zigzag (<>< or ><>) and
//         whose consecutive indices differ by at least k. Uses high/low DP with two
//         max segment trees over compressed values for O(n log n) time.
//         """
//         n = len(nums)
//         vals = sorted(set(nums))
//         coord = {v: i for i, v in enumerate(vals)}
//         m = len(vals)
//         neg = -(10**18)
// 
//         st_low = SegTreeMax(m, neg)
//         st_high = SegTreeMax(m, neg)
// 
//         high = [neg] * n
//         low = [neg] * n
//         ans = neg
// 
//         for i in range(n):
//             if i >= k:
//                 p = i - k
//                 st_low.update(coord[nums[p]], low[p])
//                 st_high.update(coord[nums[p]], high[p])
// 
//             pos = coord[nums[i]]
//             ml = st_low.query(0, pos - 1)
//             mh = st_high.query(pos + 1, m - 1)
// 
//             high[i] = nums[i]
//             low[i] = nums[i]
//             if ml != neg:
//                 high[i] = max(high[i], ml + nums[i])
//             if mh != neg:
//                 low[i] = max(low[i], mh + nums[i])
// 
//             ans = max(ans, high[i], low[i])
// 
//         return ans
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

class SegTreeMax {
    int n, size;
    long long neg;
    vector<long long> tree;
public:
    SegTreeMax(int n, long long neg) : n(n), size(1), neg(neg) {
        while (size < n) size <<= 1;
        tree.assign(2 * size, neg);
    }
    void update(int i, long long val) {
        i += size;
        tree[i] = max(tree[i], val);
        for (i >>= 1; i; i >>= 1) tree[i] = max(tree[i << 1], tree[i << 1 | 1]);
    }
    long long query(int l, int r) {
        if (l > r) return neg;
        l = max(l, 0);
        r = min(r, n - 1);
        if (l > r) return neg;
        l += size;
        r += size;
        long long res = neg;
        while (l <= r) {
            if (l & 1) res = max(res, tree[l++]);
            if (!(r & 1)) res = max(res, tree[r--]);
            l >>= 1;
            r >>= 1;
        }
        return res;
    }
};

class Solution {
public:
    long long maxAlternatingSum(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> vals = nums;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        int m = vals.size();
        const long long NEG = -(long long)4e18;
        SegTreeMax stLow(m, NEG), stHigh(m, NEG);
        vector<long long> high(n, NEG), low(n, NEG);
        long long ans = NEG;
        for (int i = 0; i < n; ++i) {
            if (i >= k) {
                int p = i - k;
                int posp = lower_bound(vals.begin(), vals.end(), nums[p]) - vals.begin();
                stLow.update(posp, low[p]);
                stHigh.update(posp, high[p]);
            }
            int pos = lower_bound(vals.begin(), vals.end(), nums[i]) - vals.begin();
            long long ml = stLow.query(0, pos - 1);
            long long mh = stHigh.query(pos + 1, m - 1);
            high[i] = low[i] = nums[i];
            if (ml != NEG) high[i] = max(high[i], ml + nums[i]);
            if (mh != NEG) low[i] = max(low[i], mh + nums[i]);
            ans = max({ans, high[i], low[i]});
        }
        return ans;
    }
};
// @lc code=end
