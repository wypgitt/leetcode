#
# @lc app=leetcode id=2464 lang=python3
#
# [2464] Minimum Subarrays in a Valid Split
#
# https://leetcode.com/problems/minimum-subarrays-in-a-valid-split/description/
#
# algorithms
# Medium (64.43%)
# Likes:    42
# Dislikes: 9
# Total Accepted:    3.6K
# Total Submissions: 5.6K
# Testcase Example:  "[2,6,3,4,3]"
#
#
# You are given an integer array nums.
#
# Splitting of an integer array nums into subarrays is valid if:
#
# the greatest common divisor of the first and last elements of each
# subarray is greater than 1, and
#
# each element of nums belongs to exactly one subarray.
#
# Return the minimum number of subarrays in a valid subarray splitting of
# nums. If a valid subarray splitting is not possible, return -1.
#
# Note that:
#
# The greatest common divisor of two numbers is the largest positive
# integer that evenly divides both numbers.
#
# A subarray is a contiguous non-empty part of an array.
#
# Example 1:
#
# Input: nums = [2,6,3,4,3]
# Output: 2
# Explanation: We can create a valid split in the following way: [2,6] |
# [3,4,3].
# - The starting element of the 1^st subarray is 2 and the ending is 6.
# Their greatest common divisor is 2, which is greater than 1.
# - The starting element of the 2^nd subarray is 3 and the ending is 3.
# Their greatest common divisor is 3, which is greater than 1.
# It can be proved that 2 is the minimum number of subarrays that we can
# obtain in a valid split.
#
# Example 2:
#
# Input: nums = [3,5]
# Output: 2
# Explanation: We can create a valid split in the following way: [3] |
# [5].
# - The starting element of the 1^st subarray is 3 and the ending is 3.
# Their greatest common divisor is 3, which is greater than 1.
# - The starting element of the 2^nd subarray is 5 and the ending is 5.
# Their greatest common divisor is 5, which is greater than 1.
# It can be proved that 2 is the minimum number of subarrays that we can
# obtain in a valid split.
#
# Example 3:
#
# Input: nums = [1,2,1]
# Output: -1
# Explanation: It is impossible to create valid split.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List
from math import gcd, inf


class Solution:
    def validSubarraySplit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Split nums into contiguous subarrays where gcd(first, last)
        of each piece > 1. Minimize number of pieces; -1 if impossible.

        Algorithm:
        - DP: dp[i] = min pieces for prefix nums[0..i]; transition if
          gcd(nums[j], nums[i]) > 1.

        Complexity: O(n^2 log A) time, O(n) space.
        """
        n = len(nums)
        dp = [inf] * n
        for i in range(n):
            for j in range(i + 1):
                if gcd(nums[j], nums[i]) > 1:
                    dp[i] = min(dp[i], 1 if j == 0 else dp[j - 1] + 1)
        return -1 if dp[-1] == inf else int(dp[-1])

    def validSubarraySplit_dfs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate memoized DFS from split starts.

        Algorithm:
        - dfs(i) = min 1+dfs(j+1) over j>=i with gcd(nums[i], nums[j])>1.

        Complexity: O(n^2 log A) time, O(n) space.
        """
        from functools import lru_cache

        n = len(nums)

        @lru_cache(None)
        def dfs(i: int) -> int:
            if i >= n:
                return 0
            ans = 10**9
            for j in range(i, n):
                if gcd(nums[i], nums[j]) > 1:
                    ans = min(ans, 1 + dfs(j + 1))
            return ans

        res = dfs(0)
        return res if res < 10**9 else -1
# @lc code=end

