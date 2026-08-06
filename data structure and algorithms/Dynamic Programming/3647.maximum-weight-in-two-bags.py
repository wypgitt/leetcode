#
# @lc app=leetcode id=3647 lang=python3
#
# [3647] Maximum Weight in Two Bags
#
# https://leetcode.com/problems/maximum-weight-in-two-bags/description/
#
# algorithms
# Medium (57.84%)
# Likes:    6
# Dislikes: 3
# Total Accepted:    778
# Total Submissions: 1.3K
# Testcase Example:  "[1,4,3,2]\n5\n4"
#
#
# You are given an integer array weights and two integers w1 and w2
# representing the maximum capacities of two bags.
#
# Each item may be placed in at most one bag such that:
#
# Bag 1 holds at most w1 total weight.
#
# Bag 2 holds at most w2 total weight.
#
# Return the maximum total weight that can be packed into the two bags.
#
# Example 1:
#
# Input: weights = [1,4,3,2], w1 = 5, w2 = 4
#
# Output: 9
#
# Explanation:
#
# Bag 1: Place weights[2] = 3 and weights[3] = 2 as 3 + 2 = 5 <= w1
#
# Bag 2: Place weights[1] = 4 as 4 <= w2
#
# Total weight: 5 + 4 = 9
#
# Example 2:
#
# Input: weights = [3,6,4,8], w1 = 9, w2 = 7
#
# Output: 15
#
# Explanation:
#
# Bag 1: Place weights[3] = 8 as 8 <= w1
#
# Bag 2: Place weights[0] = 3 and weights[2] = 4 as 3 + 4 = 7 <= w2
#
# Total weight: 8 + 7 = 15
#
# Example 3:
#
# Input: weights = [5,7], w1 = 2, w2 = 3
#
# Output: 0
#
# Explanation:
#
# No weight fits in either bag, thus the answer is 0.
#
# Constraints:
#
# 1 <= weights.length <= 100
#
# 1 <= weights[i] <= 100
#
# 1 <= w1, w2 <= 300
#

# @lc code=start
from typing import List


class Solution:
    def maxWeight(self, weights: List[int], w1: int, w2: int) -> int:
        """
        Interview explanation:
        Classic two-knapsack: each item goes to bag1, bag2, or neither.

        Algorithm:
        - DP set of reachable (a, b) filled weights; iterate items updating
          a+w<=w1 or b+w<=w2; track max a+b.

        Complexity: O(n * w1 * w2) time and space.
        """
        reachable = {(0, 0)}
        for w in weights:
            nxt = set(reachable)
            for a, b in reachable:
                if a + w <= w1:
                    nxt.add((a + w, b))
                if b + w <= w2:
                    nxt.add((a, b + w))
            reachable = nxt
        return max(a + b for a, b in reachable)

    def maxWeight_bool_dp(self, weights: List[int], w1: int, w2: int) -> int:
        """
        Interview explanation:
        Alternate: boolean DP table dp[a][b] whether capacity pair is achievable.

        Algorithm:
        - dp[0][0]=True; for each weight update table backward; scan for max a+b.

        Complexity: O(n * w1 * w2) time, O(w1 * w2) space.
        """
        dp = [[False] * (w2 + 1) for _ in range(w1 + 1)]
        dp[0][0] = True
        for w in weights:
            for a in range(w1, -1, -1):
                for b in range(w2, -1, -1):
                    if not dp[a][b]:
                        continue
                    if a + w <= w1:
                        dp[a + w][b] = True
                    if b + w <= w2:
                        dp[a][b + w] = True
        ans = 0
        for a in range(w1 + 1):
            for b in range(w2 + 1):
                if dp[a][b]:
                    ans = max(ans, a + b)
        return ans
# @lc code=end

