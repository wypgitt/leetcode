#
# @lc app=leetcode id=1390 lang=python3
#
# [1390] Four Divisors
#
# https://leetcode.com/problems/four-divisors/description/
#
# algorithms
# Medium (56.53%)
# Likes:    898
# Dislikes: 223
# Total Accepted:    202K
# Total Submissions: 358K
# Testcase Example:  "[21,4,7]"
#
# Given an integer array nums, return the sum of divisors of the integers in
# that array that have exactly four divisors. If there is no such integer in
# the array, return 0.
#
# Example 1:
#
# Input: nums = [21,4,7]
# Output: 32
# Explanation:
# 21 has 4 divisors: 1, 3, 7, 21
# 4 has 3 divisors: 1, 2, 4
# 7 has 2 divisors: 1, 7
# The answer is the sum of divisors of 21 only.
#
# Example 2:
#
# Input: nums = [21,21]
# Output: 64
#
# Example 3:
#
# Input: nums = [1,2,3,4,5]
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List
import math


class Solution:
    def sumFourDivisors(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum of divisors for numbers that have exactly four divisors. Factorize
        up to sqrt; exactly 4 divisors means form p^3 or p*q (distinct primes).

        Algorithm:
        - For each num: collect divisors while d*d<=num; if len==4 add sum

        Complexity: O(n * sqrt(M)) time, O(1) space.
        """
        ans = 0
        for num in nums:
            divs = set()
            for d in range(1, int(math.isqrt(num)) + 1):
                if num % d == 0:
                    divs.add(d)
                    divs.add(num // d)
                    if len(divs) > 4:
                        break
            if len(divs) == 4:
                ans += sum(divs)
        return ans
# @lc code=end
