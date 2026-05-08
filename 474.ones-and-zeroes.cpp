// Translated from 474.ones-and-zeroes.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=474 lang=python3
// #
// # [474] Ones and Zeroes
// #
// # https://leetcode.com/problems/ones-and-zeroes/description/
// #
// # algorithms
// # Medium (53.31%)
// # Likes:    6093
// # Dislikes: 509
// # Total Accepted:    351K
// # Total Submissions: 658.4K
// # Testcase Example:  '["10","0001","111001","1","0"]\n5\n3'
// #
// # You are given an array of binary strings strs and two integers m and n.
// # 
// # Return the size of the largest subset of strs such that there are at most m
// # 0's and n 1's in the subset.
// # 
// # A set x is a subset of a set y if all elements of x are also elements of
// # y.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: strs = ["10","0001","111001","1","0"], m = 5, n = 3
// # Output: 4
// # Explanation: The largest subset with at most 5 0's and 3 1's is {"10",
// # "0001", "1", "0"}, so the answer is 4.
// # Other valid but smaller subsets include {"0001", "1"} and {"10", "1", "0"}.
// # {"111001"} is an invalid subset because it contains 4 1's, greater than the
// # maximum of 3.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: strs = ["10","0","1"], m = 1, n = 1
// # Output: 2
// # Explanation: The largest subset is {"0", "1"}, so the answer is 2.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= strs.length <= 600
// # 1 <= strs[i].length <= 100
// # strs[i] consists only of digits '0' and '1'.
// # 1 <= m, n <= 100
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def findMaxForm(self, strs: List[str], m: int, n: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given binary strings and two resource limits:
// 
//             at most m zeroes
//             at most n ones
// 
//         We need choose the largest possible subset of strings whose total number
//         of zeroes is <= m and total number of ones is <= n.
// 
//         Each string can be chosen at most once.
// 
//         Recognize the pattern
//         ---------------------
//         This is a 0/1 knapsack problem with two capacities.
// 
//         For each string:
// 
//             cost_zeroes = number of '0' characters
//             cost_ones   = number of '1' characters
//             value       = 1 selected string
// 
//         We want maximize total value while staying within both resource limits.
// 
//         DP definition
//         -------------
//         Let:
// 
//             dp[zeroes][ones]
// 
//         be the maximum number of strings we can choose using at most:
// 
//             zeroes zeroes
//             ones ones
// 
//         after processing some prefix of the input strings.
// 
//         The final answer is:
// 
//             dp[m][n]
// 
//         Transition
//         ----------
//         For a string with:
// 
//             z = number of zeroes
//             o = number of ones
// 
//         if we have enough capacity, we can choose it:
// 
//             dp[zeroes][ones] =
//                 max(
//                     dp[zeroes][ones],
//                     dp[zeroes - z][ones - o] + 1
//                 )
// 
//         The first term means "skip this string".
//         The second term means "take this string".
// 
//         Why iterate capacities backward?
//         --------------------------------
//         This is the most important implementation detail.
// 
//         Each string can be used at most once.  If we looped `zeroes` and `ones`
//         upward, then after updating a smaller capacity with the current string,
//         a larger capacity in the same iteration could reuse that updated value,
//         effectively taking the same string multiple times.
// 
//         By looping backward:
// 
//             for zeroes from m down to z
//             for ones from n down to o
// 
//         the state `dp[zeroes - z][ones - o]` still belongs to the previous set
//         of processed strings, so the current string is used at most once.
// 
//         Data structure choice
//         ---------------------
//         We use a 2D list:
// 
//             (m + 1) x (n + 1)
// 
//         because both capacities are at most 100.  This is small:
// 
//             101 * 101 = 10201 states
// 
//         A dictionary of reachable states would also work, but a list is faster
//         and simpler for dense small capacities.
// 
//         Algorithm
//         ---------
//         1. Initialize `dp` with zeroes.
//         2. For every string in `strs`:
//               - count its zeroes `z`
//               - compute ones `o = len(string) - z`
//               - update the DP table in reverse capacity order
//         3. Return `dp[m][n]`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: After processing any prefix of strings, `dp[a][b]` is the
//         maximum number of strings selectable from that prefix using at most `a`
//         zeroes and at most `b` ones.
//         Initially, before processing any strings, selecting zero strings is the
//         only option, so all states are correctly 0.  When processing a new
//         string, any optimal subset for capacity `(a, b)` either skips it, keeping
//         the old value, or takes it, in which case the remaining capacity is
//         `(a - z, b - o)` and the value is one plus the optimum for that previous
//         capacity.  The transition takes the maximum of exactly these choices.
// 
//         Lemma 2: Reverse iteration ensures each string is counted at most once.
//         During the update for one string, every referenced state
//         `dp[a - z][b - o]` has not yet been updated for the current string at
//         this iteration because capacities are traversed downward.  Therefore the
//         transition can only add the current string to a subset formed from
//         earlier strings.
// 
//         Theorem: The algorithm returns the largest valid subset size.
//         By Lemma 1, after all strings are processed, `dp[m][n]` is the maximum
//         number of strings selectable with at most `m` zeroes and `n` ones.  By
//         Lemma 2, every string is used at most once.  This is exactly the problem
//         requirement.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             S = len(strs)
//             L = maximum string length
// 
//         Counting zeroes across all strings costs O(S * L).
//         For each string, we update an `(m + 1) x (n + 1)` DP table.
// 
//         Total time:
// 
//             O(S * L + S * m * n)
// 
//         Since `m, n <= 100` and `S <= 600`, this is well within limits.
// 
//         Total space:
// 
//             O(m * n)
// 
//         Edge cases
//         ----------
//         * A string individually exceeds both capacities:
//           The reverse loops simply never include it.
// 
//         * Capacity is small:
//           The DP naturally keeps only feasible subsets.
// 
//         * Many duplicate strings:
//           They are separate items and may each be chosen at most once.
// 
//         * A string has only zeroes or only ones:
//           One of its costs is 0, and the same transition still works.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               ["10","0001","111001","1","0"], m = 5, n = 3 -> 4
//               ["10","0","1"], m = 1, n = 1 -> 2
// 
//         * Strings that exceed capacity.
//         * Strings with only zeroes or only ones.
//         * Duplicate strings.
//         * Random small cases compared against brute-force subset enumeration.
// 
//         Possible improvement?
//         ---------------------
//         This is already the standard optimal dynamic programming approach for
//         these constraints.  A full 3D DP over item index would be easier to
//         visualize but uses more memory.  The 2D reverse-loop version gives the
//         same result with O(m * n) space.
//         """
// 
//         dp = [[0] * (n + 1) for _ in range(m + 1)]
// 
//         for text in strs:
//             zeroes = text.count("0")
//             ones = len(text) - zeroes
// 
//             for zero_capacity in range(m, zeroes - 1, -1):
//                 for one_capacity in range(n, ones - 1, -1):
//                     dp[zero_capacity][one_capacity] = max(
//                         dp[zero_capacity][one_capacity],
//                         dp[zero_capacity - zeroes][one_capacity - ones] + 1,
//                     )
// 
//         return dp[m][n]
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
    int findMaxForm(vector<string>& strs, int m, int n) {
        vector<vector<int>> dp(m + 1, vector<int>(n + 1));
        for (auto& text : strs) {
            int zeros = count(text.begin(), text.end(), '0');
            int ones = text.size() - zeros;
            for (int z = m; z >= zeros; --z) for (int o = n; o >= ones; --o) dp[z][o] = max(dp[z][o], dp[z - zeros][o - ones] + 1);
        }
        return dp[m][n];
    }
};
