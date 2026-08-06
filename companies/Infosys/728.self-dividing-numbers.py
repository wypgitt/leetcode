#
# @lc app=leetcode id=728 lang=python3
#
# [728] Self Dividing Numbers
#
# https://leetcode.com/problems/self-dividing-numbers/description/
#
# algorithms
# Easy (81.08%)
# Likes:    1960
# Dislikes: 387
# Total Accepted:    356K
# Total Submissions: 439K
# Testcase Example:  "1"
#
# A self-dividing number is a number that is divisible by every digit it
# contains.
#
# For example, 128 is a self-dividing number because 128 % 1 == 0, 128 % 2 ==
# 0, and 128 % 8 == 0.
#
# A self-dividing number is not allowed to contain the digit zero.
#
# Given two integers left and right, return a list of all the self-dividing
# numbers in the range [left, right] (both inclusive).
#
# Example 1:
#
# Input: left = 1, right = 22
# Output: [1,2,3,4,5,6,7,8,9,11,12,15,22]
#
# Example 2:
#
# Input: left = 47, right = 85
# Output: [48,55,66,77]
#
# Constraints:
#
# 1 <= left <= right <= 10^4
#


# @lc code=start
from typing import List


class Solution:
    def selfDividingNumbers(self, left: int, right: int) -> List[int]:
        """
        Interview explanation:
        A self-dividing number is divisible by every digit and has no zero
        digit. Check each integer in [left, right].

        Algorithm:
        - For n in range: extract digits; fail on 0 or n % d != 0; else keep.

        Complexity: O((right-left+1) * D) time for D digits; O(1) extra space.
        """
        def ok(n: int) -> bool:
            x = n
            while x:
                d = x % 10
                if d == 0 or n % d:
                    return False
                x //= 10
            return True

        return [n for n in range(left, right + 1) if ok(n)]
# @lc code=end

