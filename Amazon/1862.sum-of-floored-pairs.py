#
# @lc app=leetcode id=1862 lang=python3
#
# [1862] Sum of Floored Pairs
#
# https://leetcode.com/problems/sum-of-floored-pairs/description/
#
# algorithms
# Hard (31.3%)
# Likes:    471
# Dislikes: 39
# Total Accepted:    12.9K
# Total Submissions: 41.1K
# Testcase Example:  "[2,5,9]"
#
# Given an integer array nums, return the sum of floor(nums[i] / nums[j]) for
# all pairs of indices 0 <= i, j < nums.length in the array. Since the answer
# may be too large, return it modulo 10^9 + 7.
#
# The floor() function returns the integer part of the division.
#
# Example 1:
#
# Input: nums = [2,5,9]
# Output: 10
# Explanation:
# floor(2 / 5) = floor(2 / 9) = floor(5 / 9) = 0
# floor(2 / 2) = floor(5 / 5) = floor(9 / 9) = 1
# floor(5 / 2) = 2
# floor(9 / 2) = 4
# floor(9 / 5) = 1
# We calculate the floor of the division for every pair of indices in the array
# then sum them up.
#
# Example 2:
#
# Input: nums = [7,7,7,7,7,7,7]
# Output: 49
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def sumOfFlooredPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum floor(nums[i]/nums[j]) over all pairs mod 1e9+7. Count frequencies;
        for each divisor y, walk multiples and accumulate k * counts in buckets.

        Algorithm (counting + multiples):
        - freq[v]++; pref of counts to max(nums).
        - For each y>0 with freq[y]: for k=1..max/y add k*freq[y]*cnt[[ky,(k+1)y)).

        Complexity: O(M log M) time, O(M) space (M=max(nums)).
        """
        MOD = 10**9 + 7
        mx = max(nums)
        freq = [0] * (mx + 1)
        for x in nums:
            freq[x] += 1
        pref = [0] * (mx + 1)
        for i in range(1, mx + 1):
            pref[i] = pref[i - 1] + freq[i]
        ans = 0
        for y in range(1, mx + 1):
            if freq[y] == 0:
                continue
            k = 1
            while k * y <= mx:
                left = k * y
                right = min(mx, (k + 1) * y - 1)
                cnt = pref[right] - pref[left - 1]
                ans = (ans + freq[y] * k * cnt) % MOD
                k += 1
        return ans

    def sumOfFlooredPairs_bruteforce(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: directly sum floor(a/b) for all pairs (too slow for limits).

        Algorithm:
        - Nested loops over nums.

        Complexity: O(n^2) time.
        """
        MOD = 10**9 + 7
        return sum(a // b for a in nums for b in nums) % MOD
# @lc code=end
