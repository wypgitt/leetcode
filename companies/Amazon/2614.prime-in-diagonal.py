#
# @lc app=leetcode id=2614 lang=python3
#
# [2614] Prime In Diagonal
#
# https://leetcode.com/problems/prime-in-diagonal/description/
#
# algorithms
# Easy (38.78%)
# Likes:    423
# Dislikes: 47
# Total Accepted:    77K
# Total Submissions: 198.7K
# Testcase Example:  "[[1,2,3],[5,6,7],[9,10,11]]"
#
# You are given a 0-indexed two-dimensional integer array nums.
#
# Return the largest prime number that lies on at least one of the diagonals of
# nums. In case, no prime is present on any of the diagonals, return 0.
#
# Note that:
#
#
# An integer is prime if it is greater than 1 and has no positive integer
# divisors other than 1 and itself.
#
#
# An integer val is on one of the diagonals of nums if there exists an integer i
# for which nums[i][i] = val or an i for which nums[i][nums.length - i - 1] =
# val.
#
# In the above diagram, one diagonal is [1,5,9] and another diagonal is [3,5,7].
#
#
#
# Example 1:
#
# Input: nums = [[1,2,3],[5,6,7],[9,10,11]]
# Output: 11
# Explanation: The numbers 1, 3, 6, 9, and 11 are the only numbers present on at
# least one of the diagonals. Since 11 is the largest prime, we return 11.
#
# Example 2:
#
# Input: nums = [[1,2,3],[5,17,7],[9,11,10]]
# Output: 17
# Explanation: The numbers 1, 3, 9, 10, and 17 are all present on at least one
# of the diagonals. 17 is the largest prime, so we return 17.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 300
#
#
# nums.length == nums_i.length
#
#
# 1 <= nums[i][j] <= 4*10^6
#

# @lc code=start
from typing import List


class Solution:
    def diagonalPrime(self, nums: List[List[int]]) -> int:
        """
        Interview explanation:
        Among values on the main and anti diagonals, return the largest prime
        (or 0 if none).

        Algorithm:
        - Scan nums[i][i] and nums[i][n-1-i]; test primality; track the max prime.

        Complexity: O(n * √M) time, O(1) space (M = max value).
        """
        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            if x % 2 == 0:
                return x == 2
            d = 3
            while d * d <= x:
                if x % d == 0:
                    return False
                d += 2
            return True

        n = len(nums)
        ans = 0
        for i in range(n):
            for v in (nums[i][i], nums[i][n - 1 - i]):
                if v > ans and is_prime(v):
                    ans = v
        return ans
# @lc code=end
