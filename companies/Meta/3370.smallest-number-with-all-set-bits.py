#
# @lc app=leetcode id=3370 lang=python3
#
# [3370] Smallest Number With All Set Bits
#
# https://leetcode.com/problems/smallest-number-with-all-set-bits/description/
#
# algorithms
# Easy (80.12%)
# Likes:    378
# Dislikes: 15
# Total Accepted:    177.8K
# Total Submissions: 222K
# Testcase Example:  "5"
#
#
# You are given a positive number n.
#
# Return the smallest number x greater than or equal to n, such that the
# binary representation of x contains only set bits
#
# Example 1:
#
# Input: n = 5
#
# Output: 7
#
# Explanation:
#
# The binary representation of 7 is "111".
#
# Example 2:
#
# Input: n = 10
#
# Output: 15
#
# Explanation:
#
# The binary representation of 15 is "1111".
#
# Example 3:
#
# Input: n = 3
#
# Output: 3
#
# Explanation:
#
# The binary representation of 3 is "11".
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def smallestNumber(self, n: int) -> int:
        """
        Interview explanation:
        Smallest x >= n that is all 1-bits is the Mersenne number with enough bits.

        Algorithm:
        - Grow x = 1; while x < n: x = (x << 1) | 1.

        Complexity: O(log n) time, O(1) space.
        """
        x = 1
        while x < n:
            x = (x << 1) | 1
        return x

    def smallestNumber_bit_length(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: (1 << bit_length(n)) - 1 is the smallest all-ones >= n when n
        itself is not already all ones; if n is all ones it equals n.

        Complexity: O(1) time, O(1) space.
        """
        return (1 << n.bit_length()) - 1
# @lc code=end
