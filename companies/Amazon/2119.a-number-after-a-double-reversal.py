#
# @lc app=leetcode id=2119 lang=python3
#
# [2119] A Number After a Double Reversal
#
# https://leetcode.com/problems/a-number-after-a-double-reversal/description/
#
# algorithms
# Easy (82.65%)
# Likes:    808
# Dislikes: 51
# Total Accepted:    172.7K
# Total Submissions: 209K
# Testcase Example:  "526"
#
# Reversing an integer means to reverse all its digits.
#
#
# For example, reversing 2021 gives 1202. Reversing 12300 gives 321 as the
# leading zeros are not retained.
#
# Given an integer num, reverse num to get reversed1, then reverse reversed1 to
# get reversed2. Return true if reversed2 equals num. Otherwise return false.
#
#
#
# Example 1:
#
# Input: num = 526
# Output: true
# Explanation: Reverse num to get 625, then reverse 625 to get 526, which equals
# num.
#
# Example 2:
#
# Input: num = 1800
# Output: false
# Explanation: Reverse num to get 81, then reverse 81 to get 18, which does not
# equal num.
#
# Example 3:
#
# Input: num = 0
# Output: true
# Explanation: Reverse num to get 0, then reverse 0 to get 0, which equals num.
#
#
#
# Constraints:
#
#
# 0 <= num <= 10^6
#


# @lc code=start
class Solution:
    def isSameAfterReversals(self, num: int) -> bool:
        """
        Interview explanation:
        Reverse digits twice (leading zeros dropped on reverse). Equal to original
        iff num==0 or num has no trailing zero.

        Algorithm:
        - Return num == 0 or num % 10 != 0.

        Complexity: O(1).
        """
        return num == 0 or num % 10 != 0
# @lc code=end

