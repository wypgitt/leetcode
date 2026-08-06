#
# @lc app=leetcode id=1671 lang=python3
#
# [1671] Minimum Number of Removals to Make Mountain Array
#
# https://leetcode.com/problems/minimum-number-of-removals-to-make-mountain-array/description/
#
# algorithms
# Hard (54.78%)
# Likes:    2319
# Dislikes: 41
# Total Accepted:    127K
# Total Submissions: 232K
# Testcase Example:  "[1,3,1]"
#
# You may recall that an array arr is a mountain array if and only if:
#
# arr.length >= 3
#
# There exists some index i (0-indexed) with 0 < i < arr.length - 1 such that:
#
# arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
#
# arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
#
# Given an integer array nums, return the minimum number of elements to remove
# to make nums a mountain array.
#
# Example 1:
#
# Input: nums = [1,3,1]
# Output: 0
# Explanation: The array itself is a mountain array so we do not need to remove
# any elements.
#
# Example 2:
#
# Input: nums = [2,1,1,5,6,2,3,1]
# Output: 3
# Explanation: One solution is to remove the elements at indices 0, 1, and 5,
# making the array nums = [1,5,6,3,1].
#
# Constraints:
#
# 3 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^9
#
# It is guaranteed that you can make a mountain array out of nums.
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def minimumMountainRemovals(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Mountain: strictly increase then strictly decrease, length >=3. Minimize
        removals = n - longest mountain subsequence. Compute LIS length ending
        at i and LDS length starting at i; for peaks with both >=2, max
        lis[i]+lds[i]-1.

        Algorithm (patience / DP LIS):
        - left[i]=LIS ending at i; right[i]=LIS on reversed suffix (LDS from i).
        - ans = n - max(left[i]+right[i]-1) over valid peaks.

        Complexity: O(n log n) with patience, O(n) space.
        """
        n = len(nums)

        def lis_lengths(arr):
            tails = []
            res = [0] * len(arr)
            for i, v in enumerate(arr):
                j = bisect.bisect_left(tails, v)
                if j == len(tails):
                    tails.append(v)
                else:
                    tails[j] = v
                res[i] = j + 1
            return res

        left = lis_lengths(nums)
        right = lis_lengths(nums[::-1])[::-1]
        best = 0
        for i in range(n):
            if left[i] >= 2 and right[i] >= 2:
                best = max(best, left[i] + right[i] - 1)
        return n - best

    def minimumMountainRemovals_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n^2) LIS DP for left and right lengths.

        Algorithm:
        - left[i]=1+max(left[j]) for j<i nums[j]<nums[i]; similarly right.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        left = [1] * n
        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    left[i] = max(left[i], left[j] + 1)
        right = [1] * n
        for i in range(n - 1, -1, -1):
            for j in range(i + 1, n):
                if nums[j] < nums[i]:
                    right[i] = max(right[i], right[j] + 1)
        best = 0
        for i in range(n):
            if left[i] >= 2 and right[i] >= 2:
                best = max(best, left[i] + right[i] - 1)
        return n - best
# @lc code=end
