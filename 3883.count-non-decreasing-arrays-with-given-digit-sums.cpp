// Translated from 3883.count-non-decreasing-arrays-with-given-digit-sums.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3883 lang=python3
// #
// # [3883] Count Non-decreasing Arrays With Given Digit Sums
// #
// 
// # @lc code=start
// class Solution:
//     pass
// 
// 
// # @lc code=end
// 
// #
// # @lc app=leetcode id=3883 lang=python3
// #
// # [3883] Count Non Decreasing Arrays With Given Digit Sums
// #
// # --- Notes (problem restatement, feasibility, DP + prefix sums, complexity, interview) ---
// #
// # Problem restatement (from constraints)
// # Given digitSum[0..n-1], count arrays arr[0..n-1] such that:
// #   - Each arr[i] is an integer with 0 <= arr[i] <= 5000.
// #   - arr is non-decreasing: arr[i] <= arr[i+1].
// #   - Sum of decimal digits of arr[i] equals digitSum[i].
// # Return count modulo 1_000_000_007.
// #
// # Key observations
// # - digitSum[i] <= 50 (given). Only finitely many candidates exist per position once we
// #   restrict arr[i] <= 5000; pre-group integers in [0, 5000] by digit-sum.
// # - If some digitSum[i] admits NO integer in [0, 5000] with that digit-sum (e.g. 49),
// #   answer is 0 immediately (Example 3).
// #
// # DP state
// # Let dp_i[v] = number of valid fillings for prefix ending at position i with arr[i] = v.
// # Transition (non-decreasing): arr[i] must be >= arr[i-1], so
// #   dp_i[v] = sum_{u <= v} dp_{i-1}[u]   for all v allowed at position i
// #            (and 0 if v is not allowed at position i).
// # This is a capped suffix of the cumulative distribution of dp_{i-1}: prefix sums on v.
// #
// # Implementation trick (dense arrays, O(MAXV) per layer)
// # MAXV = 5000. Maintain prev[v] for v = 0..MAXV (sparse mostly zero — OK memory ~5001 ints).
// # Build pref[t] = sum_{u <= t} prev[u] mod MOD for t = 0..MAXV in one left-to-right scan.
// # Then for each v in candidates[digitSum[i]], set cur[v] = pref[v].
// #
// # Initialization (i = 0)
// # prev[v] = 1 for each v allowed by digitSum[0]; else 0. Exactly one way to end at each v.
// #
// # Answer
// # sum_v prev[v] after processing last index — any ending value is allowed.
// #
// # Why not iterate over all pairs (u,v)
// # Naive O(|V|^2) per step would be too heavy when many values share a digit-sum; prefix sums
// # reduce each layer to O(MAXV + |candidates|).
// #
// # Time complexity
// # Precompute buckets once: O(MAXV * log10 MAXV) ~ O(MAXV).
// # Each of n-1 transitions: O(MAXV) for prefix + O(|bucket|) assignments — O(MAXV) per layer.
// # Total O(n * MAXV) with MAXV = 5000, n <= 1000 -> ~5e6 operations.
// #
// # Space complexity
// # O(MAXV) for prev / cur / pref arrays (plus bucket lists total size O(MAXV)).
// #
// # Edge cases
// # - digitSum contains value with empty bucket -> 0.
// # - Single element: answer is number of integers in [0,5000] with that digit-sum (Example 2).
// # - arr[i]=0 has digit-sum 0; include 0 in digit-sum computation (loop-based routine returns 0).
// #
// # Possible improvements
// # - Coordinate compression per layer (only values appearing in adjacent buckets) if MAXV grew.
// # - Sparse map DP if ranges exploded — not needed here.
// #
// # Interview walkthrough
// # 1) Bound arr[i] <= 5000 + digit-sum constraint -> finite candidate sets per index.
// # 2) Non-decreasing chain -> cumulative sum over previous DP row.
// # 3) Modular arithmetic end-to-end.
// # --- end notes ---
// 
// # @lc code=start
// MOD = 10**9 + 7
// MAXV = 5000
// 
// 
// def _digit_sum(x: int) -> int:
//     s = 0
//     while x:
//         s += x % 10
//         x //= 10
//     return s
// 
// 
// _BY_SUM = [[] for _ in range(51)]
// for _x in range(MAXV + 1):
//     _BY_SUM[_digit_sum(_x)].append(_x)
// 
// 
// class Solution:
//     def countArrays(self, digitSum: list[int]) -> int:
//         for s in digitSum:
//             if s > 50 or not _BY_SUM[s]:
//                 return 0
// 
//         prev = [0] * (MAXV + 1)
//         for v in _BY_SUM[digitSum[0]]:
//             prev[v] = 1
// 
//         for i in range(1, len(digitSum)):
//             running = 0
//             pref = [0] * (MAXV + 1)
//             for t in range(MAXV + 1):
//                 running = (running + prev[t]) % MOD
//                 pref[t] = running
//             cur = [0] * (MAXV + 1)
//             for v in _BY_SUM[digitSum[i]]:
//                 cur[v] = pref[v]
//             prev = cur
// 
//         return sum(prev) % MOD
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
    static constexpr int MOD = 1000000007;
    static constexpr int MAXV = 5000;

    int digitSum(int x) {
        int s = 0;
        while (x) {
            s += x % 10;
            x /= 10;
        }
        return s;
    }

public:
    int countArrays(vector<int>& digitSumList) {
        vector<vector<int>> bySum(51);
        for (int x = 0; x <= MAXV; ++x) bySum[digitSum(x)].push_back(x);
        for (int s : digitSumList) if (s > 50 || bySum[s].empty()) return 0;
        vector<int> prev(MAXV + 1);
        for (int v : bySum[digitSumList[0]]) prev[v] = 1;
        for (int i = 1; i < (int)digitSumList.size(); ++i) {
            vector<int> pref(MAXV + 1), cur(MAXV + 1);
            long long running = 0;
            for (int t = 0; t <= MAXV; ++t) {
                running = (running + prev[t]) % MOD;
                pref[t] = running;
            }
            for (int v : bySum[digitSumList[i]]) cur[v] = pref[v];
            prev.swap(cur);
        }
        return accumulate(prev.begin(), prev.end(), 0LL) % MOD;
    }
};
