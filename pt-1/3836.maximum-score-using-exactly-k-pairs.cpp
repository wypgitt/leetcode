/*
 * @lc app=leetcode id=3836 lang=cpp
 *
 * [3836] Maximum Score Using Exactly K Pairs
 */
// Translated from 3836.maximum-score-using-exactly-k-pairs.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3836 lang=python3
// #
// # [3836] Maximum Score Using Exactly K Pairs
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given two arrays nums1 and nums2.
// #
// # Choose exactly k pairs of indices:
// #   (i1, j1), (i2, j2), ..., (ik, jk)
// #
// # such that both index sequences are strictly increasing:
// #   i1 < i2 < ... < ik
// #   j1 < j2 < ... < jk
// #
// # Pair (i, j) contributes:
// #   nums1[i] * nums2[j]
// #
// # Return the maximum total score.
// #
// #
// # Interpretation
// # This is like matching a subsequence of nums1 with a subsequence of nums2, both
// # of length exactly k, while preserving order. The score of matching nums1[i]
// # with nums2[j] is their product.
// #
// # It is similar to sequence-alignment DP, except:
// #   - we need exactly k matches,
// #   - we may skip elements in either array,
// #   - products can be negative, so impossible states must be represented
// #     carefully.
// #
// #
// # Natural DP definition
// # Let:
// #   dp[t][i][j] = maximum score using exactly t pairs from
// #                 nums1[0..i-1] and nums2[0..j-1]
// #
// # Transition:
// #   1. skip nums1[i-1]:
// #        dp[t][i][j] = dp[t][i-1][j]
// #
// #   2. skip nums2[j-1]:
// #        dp[t][i][j] = dp[t][i][j-1]
// #
// #   3. pair nums1[i-1] with nums2[j-1]:
// #        dp[t][i][j] = dp[t-1][i-1][j-1] + nums1[i-1] * nums2[j-1]
// #
// # The answer is:
// #   dp[k][n][m]
// #
// # A direct 3D DP works conceptually but uses O(k*n*m) memory. With n,m <= 100
// # that is not huge, but we can keep only two 2D layers: previous t-1 and current
// # t.
// #
// #
// # Space-optimized layer DP
// # For each t from 1 to k:
// #   - prev is the completed DP table for exactly t - 1 pairs.
// #   - cur is the DP table we are building for exactly t pairs.
// #
// # For each i and j:
// #   cur[i][j] = max(
// #       cur[i-1][j],                                      # skip nums1[i-1]
// #       cur[i][j-1],                                      # skip nums2[j-1]
// #       prev[i-1][j-1] + nums1[i-1] * nums2[j-1]           # take this pair
// #   )
// #
// # We only iterate i >= t and j >= t because choosing t pairs requires at least t
// # elements from each prefix.
// #
// #
// # Why negative infinity is necessary
// # Scores can be negative. If we initialized impossible states to 0, we might
// # accidentally prefer "choosing fewer than k pairs" over a required negative
// # total.
// #
// # Example:
// #   nums1 = [-3, -2], nums2 = [1, 2], k = 2
// #   The only valid matching scores -3*1 + -2*2 = -7.
// #
// # The answer is negative, so impossible states must be -infinity, not 0.
// #
// # Base case:
// #   With exactly 0 pairs, score is 0 for any prefixes:
// #     prev[i][j] = 0
// #
// # For t >= 1:
// #   impossible states start at -infinity.
// #
// #
// # Data structure choice
// # We use 2D Python lists for DP tables because:
// #   - n and m are at most 100,
// #   - indexing by prefix length is natural,
// #   - dense tables are simpler and faster than dictionaries for this state space.
// #
// # We use two layers:
// #   prev: dp for t - 1 pairs
// #   cur:  dp for t pairs
// #
// # This reduces space from O(k*n*m) to O(n*m).
// #
// #
// # Walkthrough of the code
// # 1. n = len(nums1), m = len(nums2).
// # 2. Initialize prev as all zeros, representing t = 0 pairs.
// # 3. For t in 1..k:
// #      - create cur filled with NEG_INF.
// #      - fill prefixes i >= t and j >= t.
// #      - use the three transitions: skip i, skip j, take pair.
// #      - after finishing, prev = cur.
// # 4. Return prev[n][m].
// #
// #
// # Correctness proof
// #
// # Lemma 1: dp[t][i][j] satisfies the recurrence above.
// # Proof:
// # Consider an optimal solution using exactly t pairs from the two prefixes.
// # Look at nums1[i-1] and nums2[j-1].
// #
// # If nums1[i-1] is not used, the solution lies entirely in
// # nums1[0..i-2] and nums2[0..j-1], giving value dp[t][i-1][j].
// #
// # If nums2[j-1] is not used, the solution lies entirely in
// # nums1[0..i-1] and nums2[0..j-2], giving value dp[t][i][j-1].
// #
// # If both are used, they must be paired with each other. Because indices are
// # increasing, no later element exists in either prefix. The remaining t - 1 pairs
// # must come from nums1[0..i-2] and nums2[0..j-2], giving:
// #   dp[t-1][i-1][j-1] + nums1[i-1] * nums2[j-1]
// #
// # These cases cover every valid optimal solution, so taking the maximum is
// # correct.
// #
// # Lemma 2: The base case for t = 0 is correct.
// # Proof:
// # Choosing exactly zero pairs always yields score 0, regardless of how many
// # prefix elements are available.
// #
// # Lemma 3: The layer-optimized implementation computes the same values as the
// # full 3D DP.
// # Proof:
// # The recurrence for layer t only depends on:
// #   - cur[i-1][j] and cur[i][j-1] from the same layer,
// #   - prev[i-1][j-1] from layer t - 1.
// # Therefore, once layer t - 1 is complete, no older layers are needed. Filling
// # cur in increasing i and j order ensures same-layer dependencies are already
// # computed.
// #
// # Theorem: The algorithm returns the maximum score using exactly k valid pairs.
// # Proof:
// # By Lemma 1 and Lemma 2, the DP definition and recurrence correctly compute the
// # optimal score for every t, i, and j. By Lemma 3, the implementation computes
// # the same final state as the full DP. Therefore prev[n][m] after processing
// # t = k is exactly the required answer.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums1), m = len(nums2).
// #
// # Time:
// #   We fill an n by m table for each t from 1 to k.
// #   Overall time complexity: O(k * n * m).
// #
// # Space:
// #   We keep two (n + 1) by (m + 1) tables.
// #   Overall space complexity: O(n * m).
// #
// # With constraints n,m <= 100, this is easily within limits.
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums1 = [1,3,2], nums2 = [4,5,1], k = 2 -> 22
// #
// # 2. Example 2 with negative and positive products:
// #      nums1 = [-2,0,5], nums2 = [-3,4,-1,2], k = 2 -> 26
// #
// # 3. All required pairs are negative:
// #      nums1 = [-3,-2], nums2 = [1,2], k = 2 -> -7
// #      This verifies that impossible states are not initialized to 0.
// #
// # 4. k = 1:
// #      Answer is the maximum product nums1[i] * nums2[j] over all i,j.
// #
// # 5. k = min(n, m) and n == m:
// #      If both arrays have length k, every index must be paired in order.
// #
// # 6. Random brute force:
// #      For small n,m, enumerate all k-index subsequences from both arrays and
// #      compare with the DP.
// #
// #
// # Edge cases
// #
// # - Negative values: handled by maximizing over signed integer scores.
// # - Zero values: products can be 0 and may be optimal.
// # - k = 1: DP still works.
// # - k = min(n, m): skipping may be limited or impossible, but recurrence handles
// #   it naturally.
// #
// #
// # Possible improvements
// #
// # - Space can be reduced further to O(m) per layer with careful reverse/forward
// #   updates, but the 2D-layer version is easier to explain and less bug-prone.
// # - A top-down memoized recursion is also natural, but iterative DP avoids
// #   recursion overhead and makes exact-k layer transitions explicit.
// # - No greedy approach works because a locally best product can block better
// #   ordered matches later.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
//         n = len(nums1)
//         m = len(nums2)
//         neg_inf = -10**30
// 
//         prev = [[0] * (m + 1) for _ in range(n + 1)]
// 
//         for pairs in range(1, k + 1):
//             cur = [[neg_inf] * (m + 1) for _ in range(n + 1)]
// 
//             for i in range(pairs, n + 1):
//                 row = cur[i]
//                 prev_row = cur[i - 1]
//                 old_prev_row = prev[i - 1]
//                 x = nums1[i - 1]
// 
//                 for j in range(pairs, m + 1):
//                     take = old_prev_row[j - 1] + x * nums2[j - 1]
//                     row[j] = max(prev_row[j], row[j - 1], take)
// 
//             prev = cur
// 
//         return prev[n][m]
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
    long long maxScore(vector<int>& nums1, vector<int>& nums2, int k) {
        int n = nums1.size(), m = nums2.size();
        const long long NEG = -(long long)4e18;
        vector<vector<long long>> prev(n + 1, vector<long long>(m + 1, 0));
        for (int pairs = 1; pairs <= k; ++pairs) {
            vector<vector<long long>> cur(n + 1, vector<long long>(m + 1, NEG));
            for (int i = pairs; i <= n; ++i) {
                for (int j = pairs; j <= m; ++j) {
                    long long take = prev[i - 1][j - 1] + 1LL * nums1[i - 1] * nums2[j - 1];
                    cur[i][j] = max({cur[i - 1][j], cur[i][j - 1], take});
                }
            }
            prev.swap(cur);
        }
        return prev[n][m];
    }
};
// @lc code=end
