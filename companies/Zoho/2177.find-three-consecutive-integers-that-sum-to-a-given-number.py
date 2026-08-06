#
# @lc app=leetcode id=2177 lang=python3
#
# [2177] Find Three Consecutive Integers That Sum to a Given Number
#
# https://leetcode.com/problems/find-three-consecutive-integers-that-sum-to-a-given-number/description/
#
# algorithms
# Medium (65.17%)
# Likes:    741
# Dislikes: 234
# Total Accepted:    70.5K
# Total Submissions: 108.1K
# Testcase Example:  "33"
#
# Given an integer num, return three consecutive integers (as a sorted array)
# that sum to num. If num cannot be expressed as the sum of three consecutive
# integers, return an empty array.
#
#
#
# Example 1:
#
# Input: num = 33
# Output: [10,11,12]
# Explanation: 33 can be expressed as 10 + 11 + 12 = 33.
# 10, 11, 12 are 3 consecutive integers, so we return [10, 11, 12].
#
# Example 2:
#
# Input: num = 4
# Output: []
# Explanation: There is no way to express 4 as the sum of 3 consecutive
# integers.
#
#
#
# Constraints:
#
#
# 0 <= num <= 10^15
#

# @lc code=start
from typing import List


class Solution:
    def sumOfThree(self, num: int) -> List[int]:
        """
        Interview explanation:
        Find three consecutive integers summing to num, or [] if impossible.
        x+(x+1)+(x+2)=3x+3=num ⇒ num % 3 == 0 and x = num//3 - 1.

        Algorithm:
        (math)
        - If num % 3: return []; else return [num//3-1, num//3, num//3+1].

        Complexity: O(1).
        """
        if num % 3:
            return []
        x = num // 3 - 1
        return [x, x + 1, x + 2]
# @lc code=end
