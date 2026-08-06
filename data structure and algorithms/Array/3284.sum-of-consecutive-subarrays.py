#
# @lc app=leetcode id=3284 lang=python3
#
# [3284] Sum of Consecutive Subarrays
#
# https://leetcode.com/problems/sum-of-consecutive-subarrays/description/
#
# algorithms
# Medium (42.92%)
# Likes:    12
# Dislikes: 3
# Total Accepted:    933
# Total Submissions: 2.2K
# Testcase Example:  "[1,2,3]"
#
#
# We call an array arr of length n consecutive if one of the following
# holds:
#
# arr[i] - arr[i - 1] == 1 for all 1 <= i < n.
#
# arr[i] - arr[i - 1] == -1 for all 1 <= i < n.
#
# The value of an array is the sum of its elements.
#
# For example, [3, 4, 5] is a consecutive array of value 12 and [9, 8] is
# another of value 17. While [3, 4, 3] and [8, 6] are not consecutive.
#
# Given an array of integers nums, return the sum of the values of all
# consecutive subarrays.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note that an array of length 1 is also considered consecutive.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 20
#
# Explanation:
#
# The consecutive subarrays are: [1], [2], [3], [1, 2], [2, 3], [1, 2, 3].
#
# Sum of their values would be: 1 + 2 + 3 + 3 + 5 + 6 = 20.
#
# Example 2:
#
# Input: nums = [1,3,5,7]
#
# Output: 16
#
# Explanation:
#
# The consecutive subarrays are: [1], [3], [5], [7].
#
# Sum of their values would be: 1 + 3 + 5 + 7 = 16.
#
# Example 3:
#
# Input: nums = [7,6,1,2]
#
# Output: 32
#
# Explanation:
#
# The consecutive subarrays are: [7], [6], [1], [2], [7, 6], [1, 2].
#
# Sum of their values would be: 7 + 6 + 1 + 2 + 13 + 3 = 32.
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
    def getSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Only subarrays that stay consecutive with a fixed step ±1 contribute.
        Partition into maximal arithmetic segments of difference ±1.

        Algorithm:
        - Scan runs with constant diff d in {+1,-1}.
        - In a run of length L, nums[t] appears in (t+1)*(L-t) subarrays.
        - Sum contributions mod 10^9+7 (length-1 runs are included).

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        ans = 0
        i = 0
        while i < n:
            j = i
            if j + 1 < n and abs(nums[j + 1] - nums[j]) == 1:
                d = nums[j + 1] - nums[j]
                while j + 1 < n and nums[j + 1] - nums[j] == d:
                    j += 1
            L = j - i + 1
            for t in range(L):
                ans = (ans + nums[i + t] * (t + 1) * (L - t)) % MOD
            i = j + 1
        return ans
# @lc code=end
