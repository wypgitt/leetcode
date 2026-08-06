#
# @lc app=leetcode id=3836 lang=python3
#
# [3836] Maximum Score Using Exactly K Pairs
#
# https://leetcode.com/problems/maximum-score-using-exactly-k-pairs/description/
#
# algorithms
# Hard (41.83%)
# Likes:    74
# Dislikes: 4
# Total Accepted:    15.4K
# Total Submissions: 36.7K
# Testcase Example:  "[1,3,2]\n[4,5,1]\n2"
#
#
# You are given two integer arrays nums1 and nums2 of lengths n and m
# respectively, and an integer k.
#
# You must choose exactly k pairs of indices (i_1, j_1), (i_2, j_2), ...,
# (i_k, j_k) such that:
#
# 0 <= i_1 < i_2 < ... < i_k < n
#
# 0 <= j_1 < j_2 < ... < j_k < m
#
# For each chosen pair (i, j), you gain a score of nums1[i] * nums2[j].
#
# The total score is the sum of the products of all selected pairs.
#
# Return an integer representing the maximum achievable total score.
#
# Example 1:
#
# Input: nums1 = [1,3,2], nums2 = [4,5,1], k = 2
#
# Output: 22
#
# Explanation:
#
# One optimal choice of index pairs is:
#
# (i_1, j_1) = (1, 0) which scores 3 * 4 = 12
#
# (i_2, j_2) = (2, 1) which scores 2 * 5 = 10
#
# This gives a total score of 12 + 10 = 22.
#
# Example 2:
#
# Input: nums1 = [-2,0,5], nums2 = [-3,4,-1,2], k = 2
#
# Output: 26
#
# Explanation:
#
# One optimal choice of index pairs is:
#
# (i_1, j_1) = (0, 0) which scores -2 * -3 = 6
#
# (i_2, j_2) = (2, 1) which scores 5 * 4 = 20
#
# The total score is 6 + 20 = 26.
#
# Example 3:
#
# Input: nums1 = [-3,-2], nums2 = [1,2], k = 2
#
# Output: -7
#
# Explanation:
#
# The optimal choice of index pairs is:
#
# (i_1, j_1) = (0, 0) which scores -3 * 1 = -3
#
# (i_2, j_2) = (1, 1) which scores -2 * 2 = -4
#
# The total score is -3 + (-4) = -7.
#
# Constraints:
#
# 1 <= n == nums1.length <= 100
#
# 1 <= m == nums2.length <= 100
#
# -10^6 <= nums1[i], nums2[i] <= 10^6
#
# 1 <= k <= min(n, m)
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Choose exactly k increasing index pairs (i, j) maximizing sum of
        nums1[i] * nums2[j]. Classic 2D DP over prefixes and pair count.

        Algorithm:
        - dp[pairs][i][j] = best using first i of nums1 and first j of nums2
          with exactly `pairs` matches.
        - Transition: skip nums1[i-1], skip nums2[j-1], or pair them with
          previous best for pairs-1.

        Complexity: O(k n m) time, O(n m) space.
        """
        n = len(nums1)
        m = len(nums2)
        neg_inf = -10**30

        prev = [[0] * (m + 1) for _ in range(n + 1)]

        for pairs in range(1, k + 1):
            cur = [[neg_inf] * (m + 1) for _ in range(n + 1)]

            for i in range(pairs, n + 1):
                row = cur[i]
                prev_row = cur[i - 1]
                old_prev_row = prev[i - 1]
                x = nums1[i - 1]

                for j in range(pairs, m + 1):
                    take = old_prev_row[j - 1] + x * nums2[j - 1]
                    row[j] = max(prev_row[j], row[j - 1], take)

            prev = cur

        return prev[n][m]
# @lc code=end
