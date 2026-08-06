#
# @lc app=leetcode id=1362 lang=python3
#
# [1362] Closest Divisors
#
# https://leetcode.com/problems/closest-divisors/description/
#
# algorithms
# Medium (62.4%)
# Likes:    342
# Dislikes: 101
# Total Accepted:    30.1K
# Total Submissions: 48.3K
# Testcase Example:  "8"
#
# Given an integer num, find the closest two integers in absolute difference
# whose product equals num + 1 or num + 2.
#
# Return the two integers in any order.
#
# Example 1:
#
# Input: num = 8
# Output: [3,3]
# Explanation: For num + 1 = 9, the closest divisors are 3 & 3, for num + 2 =
# 10, the closest divisors are 2 & 5, hence 3 & 3 is chosen.
#
# Example 2:
#
# Input: num = 123
# Output: [5,25]
#
# Example 3:
#
# Input: num = 999
# Output: [40,25]
#
# Constraints:
#
# 1 <= num <= 10^9
#

# @lc code=start

from typing import List
import math


class Solution:
    def closestDivisors(self, num: int) -> List[int]:
        """
        Interview explanation:
        Find factor pairs of num+1 or num+2 with minimal |a-b|. Scanning down
        from sqrt finds the closest pair for each candidate; take the better.

        Algorithm:
        - For each x in {num+1,num+2}: d=isqrt(x)..1, first x%d==0 → pair
        - Keep pair with smaller difference

        Complexity: O(sqrt(num)) time, O(1) space.
        """
        best = None
        best_diff = float("inf")
        for x in (num + 1, num + 2):
            for d in range(int(math.isqrt(x)), 0, -1):
                if x % d == 0:
                    a, b = d, x // d
                    if b - a < best_diff:
                        best_diff = b - a
                        best = [a, b]
                    break
        return best
# @lc code=end
