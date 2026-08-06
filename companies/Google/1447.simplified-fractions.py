#
# @lc app=leetcode id=1447 lang=python3
#
# [1447] Simplified Fractions
#
# https://leetcode.com/problems/simplified-fractions/description/
#
# algorithms
# Medium (70.05%)
# Likes:    445
# Dislikes: 48
# Total Accepted:    47.4K
# Total Submissions: 67.6K
# Testcase Example:  "2"
#
# Given an integer n, return a list of all simplified fractions between 0 and 1
# (exclusive) such that the denominator is less-than-or-equal-to n. You can
# return the answer in any order.
#
# Example 1:
#
# Input: n = 2
# Output: ["1/2"]
# Explanation: "1/2" is the only unique fraction with a denominator
# less-than-or-equal-to 2.
#
# Example 2:
#
# Input: n = 3
# Output: ["1/2","1/3","2/3"]
#
# Example 3:
#
# Input: n = 4
# Output: ["1/2","1/3","1/4","2/3","3/4"]
# Explanation: "2/4" is not a simplified fraction because it can be simplified
# to "1/2".
#
# Constraints:
#
# 1 <= n <= 100
#

# @lc code=start
from typing import List
from math import gcd


class Solution:
    def simplifiedFractions(self, n: int) -> List[str]:
        """
        Interview explanation:
        All simplified fractions between 0 and 1 with denom <= n: for d=2..n,
        for num=1..d-1 if gcd==1 emit "num/d".

        Algorithm:
        (gcd)
        - Nested loops + math.gcd filter.

        Complexity: O(n^2 log n) time, O(φ-ish) output space.
        """
        ans = []
        for d in range(2, n + 1):
            for num in range(1, d):
                if gcd(num, d) == 1:
                    ans.append(f"{num}/{d}")
        return ans

    def simplifiedFractions_euler(self, n: int) -> List[str]:
        """
        Interview explanation:
        Alternate same enumeration with inline Euclidean gcd (no import).

        Algorithm:
        - def egcd; same double loop.

        Complexity: O(n^2 log n) time.
        """
        def egcd(a, b):
            while b:
                a, b = b, a % b
            return a

        ans = []
        for d in range(2, n + 1):
            for num in range(1, d):
                if egcd(num, d) == 1:
                    ans.append(str(num) + "/" + str(d))
        return ans
# @lc code=end
