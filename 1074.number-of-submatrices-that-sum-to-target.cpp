/*
 * @lc app=leetcode id=1074 lang=cpp
 *
 * [1074] Number of Submatrices That Sum to Target
 */
// Translated from 1074.number-of-submatrices-that-sum-to-target.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1074 lang=python3
// #
// # [1074] Number of Submatrices That Sum to Target
// #
// 
// # --- Interview notes (2D→1D, prefix sum + map, complexity, edges, tests) ---
// #
// # Problem
// # Count submatrices (contiguous rows and columns) whose element sum equals target. Overlapping / different
// # positions count separately.
// #
// # Key idea — compress a vertical band to one row
// # Fix a top row index i and a bottom row index j (i <= j). For each column c, let
// #   col[c] = sum of matrix[t][c] for t in [i, j].
// # Any submatrix that uses exactly rows i..j and columns a..b has total sum
// #   col[a] + col[a+1] + ... + col[b].
// # So for fixed (i, j) the 2D problem becomes: number of subarrays of the 1D array col whose sum is target.
// #
// # Subproblem — subarray sum = target (LeetCode 560 style)
// # For array nums, use prefix sums S[0]=0, S[k]= nums[0]+...+nums[k-1]. Subarray nums[p..k-1] sums to target iff
// #   S[k] - S[p] = target  ⟺  S[p] = S[k] - target.
// # Scan k from 1 to n with running sum s = S[k]: add to answer the number of earlier indices with prefix sum
// # s - target. A hash map stores frequency of each prefix sum seen so far; initialize count[0] = 1.
// #
// # Why a hash map
// # O(1) average update and lookup of how many times a needed prefix sum has appeared.
// #
// # Full algorithm
// # ans = 0
// # for each top row i:
// #   col = [0] * n
// #   for bottom row j from i to m-1:
// #       col[k] += matrix[j][k]  for all k
// #       ans += subarray_count(col, target)
// # return ans
// #
// # Time complexity
// # O(m^2 * n) where m = rows, n = cols: O(m^2) pairs (i, j) and each 1D pass is O(n) with hash map.
// # With m, n <= 100 → ~10^8 worst-case operations acceptable in Python with tight constants.
// #
// # Space complexity
// # O(n) for col plus O(distinct prefix sums) for the map — O(n) typical worst-case storage per inner loop.
// #
// # Edge cases
// # Negative numbers allowed — prefix sums are not monotone; hash-map approach still works (no two-pointer shortcut).
// # Single cell matrix — one iteration of f(col).
// #
// # Tests (statement)
// # [[0,1,0],[1,1,1],[0,1,0]], target 0 → 4
// # [[1,-1],[-1,1]], target 0 → 5
// # [[904]], target 0 → 0
// #
// # Improvements / variants
// # - If columns >> rows, transpose first so the inner dimension is min(m,n) — same asymptotics here since both ≤100.
// # - Fenwick tree unnecessary — cumulative col[k] already computed incrementally when extending j.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from collections import defaultdict
// from typing import List
// 
// 
// class Solution:
//     def numSubmatrixSumTarget(self, matrix: List[List[int]], target: int) -> int:
//         def count_subarrays(nums: List[int]) -> int:
//             freq = defaultdict(int)
//             freq[0] = 1
//             cnt = pref = 0
//             for x in nums:
//                 pref += x
//                 cnt += freq[pref - target]
//                 freq[pref] += 1
//             return cnt
// 
//         m, n = len(matrix), len(matrix[0])
//         ans = 0
//         for top in range(m):
//             col = [0] * n
//             for bot in range(top, m):
//                 for k in range(n):
//                     col[k] += matrix[bot][k]
//                 ans += count_subarrays(col)
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

class Solution {
public:
    int numSubmatrixSumTarget(vector<vector<int>>& matrix, int target) {
        auto countSubarrays = [&](const vector<int>& nums) {
            unordered_map<int, int> freq;
            freq[0] = 1;
            int cnt = 0, pref = 0;
            for (int x : nums) {
                pref += x;
                if (freq.count(pref - target)) cnt += freq[pref - target];
                ++freq[pref];
            }
            return cnt;
        };
        int m = matrix.size(), n = matrix[0].size(), ans = 0;
        for (int top = 0; top < m; ++top) {
            vector<int> col(n, 0);
            for (int bot = top; bot < m; ++bot) {
                for (int j = 0; j < n; ++j) col[j] += matrix[bot][j];
                ans += countSubarrays(col);
            }
        }
        return ans;
    }
};
// @lc code=end
