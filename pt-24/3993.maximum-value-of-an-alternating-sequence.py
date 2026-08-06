#
# @lc app=leetcode id=3993 lang=python3
#
# [3993] Maximum Value of an Alternating Sequence
#
# https://leetcode.com/problems/maximum-value-of-an-alternating-sequence/description/
#
# algorithms
# Medium (31.43%)
# Likes:    34
# Dislikes: 1
# Total Accepted:    29.6K
# Total Submissions: 94.2K
# Testcase Example:  "4\n3\n5"
#
#
# You are given three integers n, s, and m.
#
# A sequence seq of integers of length n is considered valid if:
#
# seq[0] = s.
#
# The sequence is alternating, meaning that either:
#
# seq[0] > seq[1] < seq[2] > ..., or
#
# seq[0] < seq[1] > seq[2] < ....
#
# For every adjacent pair, |seq[i] - seq[i - 1]| <= m.
#
# A sequence of length 1 is considered alternating.
#
# Return the maximum possible element that can appear in any valid
# sequence.
#
# Example 1:
#
# Input: n = 4, s = 3, m = 5
#
# Output: 12
#
# Explanation:
#
# One valid sequence is [3, 8, 7, 12].
#
# The maximum element in the sequence is 12.
#
# Example 2:
#
# Input: n = 2, s = 4, m = 3
#
# Output: 7
#
# Explanation:
#
# One valid sequence is [4, 7].
#
# The maximum element in the sequence is 7.
#
# Constraints:
#
# 1 <= n, s <= 10^9
#
# 1 <= m <= 10^5
#

# @lc code=start
class Solution:
    def maximumValue(self, n: int, s: int, m: int) -> int:
        """
        Interview explanation:
        Maximize any value in an alternating sequence of length n starting at
        s with adjacent steps at most m. Best pattern: up by m, down by 1,
        repeat — each two steps add (m-1) after the first up.

        Algorithm:
        - If n == 1: return s.
        - Otherwise return s + (n // 2) * (m - 1) + 1.

        Complexity: O(1) time and space.
        """
        if n == 1:
            return s
        return s + n // 2 * (m - 1) + 1
# @lc code=end
