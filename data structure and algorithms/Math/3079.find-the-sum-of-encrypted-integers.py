#
# @lc app=leetcode id=3079 lang=python3
#
# [3079] Find the Sum of Encrypted Integers
#
# https://leetcode.com/problems/find-the-sum-of-encrypted-integers/description/
#
# algorithms
# Easy (75.30%)
# Likes:    143
# Dislikes: 20
# Total Accepted:    65.5K
# Total Submissions: 87K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums containing positive integers. We
# define a function encrypt such that encrypt(x) replaces every digit in x
# with the largest digit in x. For example, encrypt(523) = 555 and
# encrypt(213) = 333.
#
# Return the sum of encrypted elements.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 6
#
# Explanation: The encrypted elements are [1,2,3]. The sum of encrypted
# elements is 1 + 2 + 3 == 6.
#
# Example 2:
#
# Input: nums = [10,21,31]
#
# Output: 66
#
# Explanation: The encrypted elements are [11,22,33]. The sum of encrypted
# elements is 11 + 22 + 33 == 66.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def sumOfEncryptedInt(self, nums: List[int]) -> int:
        """
        Interview explanation:
        encrypt(x) replaces every digit of x with its maximum digit; sum them.

        Algorithm:
        - For each x, d=max digit, rebuild a number with the same digit count
          of all d's; accumulate.

        Complexity: O(n * D) time (D <= 4), O(1) space.
        """
        def encrypt(x: int) -> int:
            s = str(x)
            d = max(s)
            return int(d * len(s))

        return sum(encrypt(x) for x in nums)

    def sumOfEncryptedInt_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate without strings: extract digits for max; rebuild via place values.

        Algorithm:
        - Scan digits of x; then form d * (111...1) with same length.

        Complexity: O(n * D) time, O(1) space.
        """
        total = 0
        for x in nums:
            t, mx, length = x, 0, 0
            while t:
                mx = max(mx, t % 10)
                t //= 10
                length += 1
            rep = 0
            for _ in range(length):
                rep = rep * 10 + mx
            total += rep
        return total
# @lc code=end
