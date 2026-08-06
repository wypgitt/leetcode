#
# @lc app=leetcode id=3591 lang=python3
#
# [3591] Check if Any Element Has Prime Frequency
#
# https://leetcode.com/problems/check-if-any-element-has-prime-frequency/description/
#
# algorithms
# Easy (62.63%)
# Likes:    76
# Dislikes: 2
# Total Accepted:    58.2K
# Total Submissions: 92.9K
# Testcase Example:  "[1,2,3,4,5,4]"
#
#
# You are given an integer array nums.
#
# Return true if the frequency of any element of the array is prime,
# otherwise, return false.
#
# The frequency of an element x is the number of times it occurs in the
# array.
#
# A prime number is a natural number greater than 1 with only two factors,
# 1 and itself.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,4]
#
# Output: true
#
# Explanation:
#
# 4 has a frequency of two, which is a prime number.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
#
# Output: false
#
# Explanation:
#
# All elements have a frequency of one.
#
# Example 3:
#
# Input: nums = [2,2,2,4,4]
#
# Output: true
#
# Explanation:
#
# Both 2 and 4 have a prime frequency.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 100
#

# @lc code=start

from collections import Counter
from typing import List


class Solution:
    def checkPrimeFrequency(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Check whether any value's frequency is a prime number.

        Algorithm:
        - Count frequencies; test each frequency for primality (n ≤ 100).

        Complexity: O(n √n) time worst-case on freqs, O(n) space.
        """
        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            d = 2
            while d * d <= x:
                if x % d == 0:
                    return False
                d += 1
            return True

        return any(is_prime(c) for c in Counter(nums).values())
# @lc code=end
