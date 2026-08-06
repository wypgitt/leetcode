#
# @lc app=leetcode id=3575 lang=python3
#
# [3575] Maximum Good Subtree Score
#
# https://leetcode.com/problems/maximum-good-subtree-score/description/
#
# algorithms
# Hard (44.00%)
# Likes:    58
# Dislikes: 8
# Total Accepted:    5.2K
# Total Submissions: 11.8K
# Testcase Example:  "[2,3]\n[-1,0]"
#
#
# You are given an undirected tree rooted at node 0 with n nodes numbered
# from 0 to n - 1. Each node i has an integer value vals[i], and its
# parent is given by par[i].
#
# A subset of nodes within the subtree of a node is called good if every
# digit from 0 to 9 appears at most once in the decimal representation of
# the values of the selected nodes.
#
# The score of a good subset is the sum of the values of its nodes.
#
# Define an array maxScore of length n, where maxScore[u] represents the
# maximum possible sum of values of a good subset of nodes that belong to
# the subtree rooted at node u, including u itself and all its
# descendants.
#
# Return the sum of all values in maxScore.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: vals = [2,3], par = [-1,0]
#
# Output: 8
#
# Explanation:
#
# The subtree rooted at node 0 includes nodes {0, 1}. The subset {2, 3} is
# good as the digits 2 and 3 appear only once. The score of this subset is
# 2 + 3 = 5.
#
# The subtree rooted at node 1 includes only node {1}. The subset {3} is
# good. The score of this subset is 3.
#
# The maxScore array is [5, 3], and the sum of all values in maxScore is 5
# + 3 = 8. Thus, the answer is 8.
#
# Example 2:
#
# Input: vals = [1,5,2], par = [-1,0,0]
#
# Output: 15
#
# Explanation:
#
# The subtree rooted at node 0 includes nodes {0, 1, 2}. The subset {1, 5,
# 2} is good as the digits 1, 5 and 2 appear only once. The score of this
# subset is 1 + 5 + 2 = 8.
#
# The subtree rooted at node 1 includes only node {1}. The subset {5} is
# good. The score of this subset is 5.
#
# The subtree rooted at node 2 includes only node {2}. The subset {2} is
# good. The score of this subset is 2.
#
# The maxScore array is [8, 5, 2], and the sum of all values in maxScore
# is 8 + 5 + 2 = 15. Thus, the answer is 15.
#
# Example 3:
#
# Input: vals = [34,1,2], par = [-1,0,1]
#
# Output: 42
#
# Explanation:
#
# The subtree rooted at node 0 includes nodes {0, 1, 2}. The subset {34,
# 1, 2} is good as the digits 3, 4, 1 and 2 appear only once. The score of
# this subset is 34 + 1 + 2 = 37.
#
# The subtree rooted at node 1 includes node {1, 2}. The subset {1, 2} is
# good as the digits 1 and 2 appear only once. The score of this subset is
# 1 + 2 = 3.
#
# The subtree rooted at node 2 includes only node {2}. The subset {2} is
# good. The score of this subset is 2.
#
# The maxScore array is [37, 3, 2], and the sum of all values in maxScore
# is 37 + 3 + 2 = 42. Thus, the answer is 42.
#
# Example 4:
#
# Input: vals = [3,22,5], par = [-1,0,1]
#
# Output: 18
#
# Explanation:
#
# The subtree rooted at node 0 includes nodes {0, 1, 2}. The subset {3,
# 22, 5} is not good, as digit 2 appears twice. Therefore, the subset {3,
# 5} is valid. The score of this subset is 3 + 5 = 8.
#
# The subtree rooted at node 1 includes nodes {1, 2}. The subset {22, 5}
# is not good, as digit 2 appears twice. Therefore, the subset {5} is
# valid. The score of this subset is 5.
#
# The subtree rooted at node 2 includes {2}. The subset {5} is good. The
# score of this subset is 5.
#
# The maxScore array is [8, 5, 5], and the sum of all values in maxScore
# is 8 + 5 + 5 = 18. Thus, the answer is 18.
#
# Constraints:
#
# 1 <= n == vals.length <= 500
#
# 1 <= vals[i] <= 10^9
#
# par.length == n
#
# par[0] == -1
#
# 0 <= par[i] < n for i in [1, n - 1]
#
# The input is generated such that the parent array par represents a valid
# tree.
#

# @lc code=start

from typing import List


class Solution:
    def goodSubtreeSum(self, vals: List[int], par: List[int]) -> int:
        """
        Interview explanation:
        A good subset has pairwise-disjoint decimal digits. Encode each node's
        value as a 10-bit mask (invalid if it repeats a digit). Tree DP merges
        child subset-masks into the parent via knapsack over compatible masks.

        Algorithm:
        - dfs(u): map mask → max sum of a good subset in u's subtree.
        - Init with 0 and (mask(u), vals[u]) if valid.
        - For each child map, combine every (m1,m2) with m1&m2==0.
        - Add max(map values) into the global answer (mod 10^9+7).

        Complexity: O(n · 3^D) style merges with D≤10; fine for n≤500.
        """
        MOD = 10**9 + 7
        n = len(vals)
        adj = [[] for _ in range(n)]
        for i in range(1, n):
            adj[par[i]].append(i)

        def digit_mask(x: int) -> int:
            mask = 0
            while x:
                d = x % 10
                if mask & (1 << d):
                    return -1
                mask |= 1 << d
                x //= 10
            return mask

        ans = 0

        def dfs(u: int) -> dict:
            nonlocal ans
            dp = {0: 0}
            m = digit_mask(vals[u])
            if m != -1:
                dp[m] = vals[u]
            for v in adj[u]:
                child = dfs(v)
                ndp = dict(dp)
                for m1, s1 in dp.items():
                    for m2, s2 in child.items():
                        if m1 & m2 == 0:
                            comb = m1 | m2
                            s = s1 + s2
                            if s > ndp.get(comb, 0):
                                ndp[comb] = s
                dp = ndp
            ans = (ans + max(dp.values())) % MOD
            return dp

        dfs(0)
        return ans
# @lc code=end
