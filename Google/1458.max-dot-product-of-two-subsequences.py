#
# @lc app=leetcode id=1458 lang=python3
#
# [1458] Max Dot Product of Two Subsequences
#
# https://leetcode.com/problems/max-dot-product-of-two-subsequences/description/
#
# algorithms
# Hard (69.37%)
# Likes:    2167
# Dislikes: 51
# Total Accepted:    189K
# Total Submissions: 272K
# Testcase Example:  "[2,1,-2,5]"
#
# Given two arrays nums1 and nums2.
#
# Return the maximum dot product between non-empty subsequences of nums1 and
# nums2 with the same length.
#
# A subsequence of an array is a new array which is formed from the original
# array by deleting some (can be none) of the characters without disturbing the
# relative positions of the remaining characters. (ie, [2,3,5] is a subsequence
# of [1,2,3,4,5] while [1,5,3] is not).
#
# Example 1:
#
# Input: nums1 = [2,1,-2,5], nums2 = [3,0,-6]
# Output: 18
# Explanation: Take subsequence [2,-2] from nums1 and subsequence [3,-6] from
# nums2.
# Their dot product is (2*3 + (-2)*(-6)) = 18.
#
# Example 2:
#
# Input: nums1 = [3,-2], nums2 = [2,-6,7]
# Output: 21
# Explanation: Take subsequence [3] from nums1 and subsequence [7] from nums2.
# Their dot product is (3*7) = 21.
#
# Example 3:
#
# Input: nums1 = [-1,-1], nums2 = [1,1]
# Output: -1
# Explanation: Take subsequence [-1] from nums1 and subsequence [1] from nums2.
# Their dot product is -1.
#
# Constraints:
#
# 1 <= nums1.length, nums2.length <= 500
#
# -1000 <= nums1[i], nums2[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxDotProduct(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Max dot product of non-empty subsequences — DP similar to LCS.
        dp[i][j] = max product using nums1[:i] and nums2[:j].

        Algorithm:
        - dp[i][j] = max(nums1[i-1]*nums2[j-1],
                         dp[i-1][j-1] + nums1[i-1]*nums2[j-1] if dp exists,
                         dp[i-1][j], dp[i][j-1]).
        - Handle "must take at least one pair" carefully with -inf init.

        Complexity: O(mn) time/space (can roll to O(n)).
        """
        m, n = len(nums1), len(nums2)
        NEG = float("-inf")
        dp = [[NEG] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                prod = nums1[i - 1] * nums2[j - 1]
                dp[i][j] = max(
                    prod,
                    (dp[i - 1][j - 1] + prod) if dp[i - 1][j - 1] != NEG else prod,
                    dp[i - 1][j],
                    dp[i][j - 1],
                )
        return int(dp[m][n])

    def maxDotProduct_1d(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: 1D rolling DP over nums2 for the same recurrence.

        Algorithm:
        - Keep prev row; update cur[j] from prev[j-1], prev[j], cur[j-1].

        Complexity: O(mn) time, O(n) space.
        """
        m, n = len(nums1), len(nums2)
        NEG = float("-inf")
        prev = [NEG] * (n + 1)
        for i in range(1, m + 1):
            cur = [NEG] * (n + 1)
            for j in range(1, n + 1):
                prod = nums1[i - 1] * nums2[j - 1]
                cur[j] = max(
                    prod,
                    (prev[j - 1] + prod) if prev[j - 1] != NEG else prod,
                    prev[j],
                    cur[j - 1],
                )
            prev = cur
        return int(prev[n])
# @lc code=end
