#
# @lc app=leetcode id=3115 lang=python3
#
# [3115] Maximum Prime Difference
#
# https://leetcode.com/problems/maximum-prime-difference/description/
#
# algorithms
# Medium (59.39%)
# Likes:    133
# Dislikes: 16
# Total Accepted:    53.9K
# Total Submissions: 90.7K
# Testcase Example:  "[4,2,9,5,3]"
#
#
# You are given an integer array nums.
#
# Return an integer that is the maximum distance between the indices of
# two (not necessarily different) prime numbers in nums.
#
# Example 1:
#
# Input: nums = [4,2,9,5,3]
#
# Output: 3
#
# Explanation: nums[1], nums[3], and nums[4] are prime. So the answer is
# |4 - 1| = 3.
#
# Example 2:
#
# Input: nums = [4,8,2,8]
#
# Output: 0
#
# Explanation: nums[2] is prime. Because there is just one prime number,
# the answer is |2 - 2| = 0.
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^5
#
# 1 <= nums[i] <= 100
#
# The input is generated such that the number of prime numbers in the nums
# is at least one.
#

# @lc code=start
from typing import List


class Solution:
    def maximumPrimeDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max index distance between two primes in nums (same index allowed → 0).

        Algorithm:
        - Precompute primes ≤ 100; scan for first and last prime indices.

        Complexity: O(n + A log log A) time, O(A) space (A ≤ 100).
        """
        is_prime = [False, False] + [True] * 99
        for p in range(2, int(100**0.5) + 1):
            if is_prime[p]:
                for m in range(p * p, 101, p):
                    is_prime[m] = False
        first = last = -1
        for i, x in enumerate(nums):
            if is_prime[x]:
                if first < 0:
                    first = i
                last = i
        return last - first

    def maximumPrimeDifference_trial(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same result with on-the-fly trial division (values ≤ 100).

        Algorithm:
        - is_prime helper; track first/last prime indices in one pass.

        Complexity: O(n √A) time, O(1) space.
        """
        def prime(x: int) -> bool:
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

        first = last = -1
        for i, x in enumerate(nums):
            if prime(x):
                if first < 0:
                    first = i
                last = i
        return last - first
# @lc code=end
