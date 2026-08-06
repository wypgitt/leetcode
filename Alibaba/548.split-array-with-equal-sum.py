#
# @lc app=leetcode id=548 lang=python3
#
# [548] Split Array with Equal Sum
#
# https://leetcode.com/problems/split-array-with-equal-sum/description/
#
# algorithms
# Hard (50.06%)
# Likes:    418
# Dislikes: 132
# Total Accepted:    25.1K
# Total Submissions: 50.2K
# Testcase Example:  "[1,2,1,2,1,2,1]"
#
#
# Given an integer array nums of length n, return true if there is a
# triplet (i, j, k) which satisfies the following conditions:
#
# 0 < i, i + 1 < j, j + 1 < k < n - 1
#
# The sum of subarrays (0, i - 1), (i + 1, j - 1), (j + 1, k - 1) and (k +
# 1, n - 1) is equal.
#
# A subarray (l, r) represents a slice of the original array starting from
# the element indexed l to the element indexed r.
#
# Example 1:
#
# Input: nums = [1,2,1,2,1,2,1]
# Output: true
# Explanation:
# i = 1, j = 3, k = 5.
# sum(0, i - 1) = sum(0, 0) = 1
# sum(i + 1, j - 1) = sum(2, 2) = 1
# sum(j + 1, k - 1) = sum(4, 4) = 1
# sum(k + 1, n - 1) = sum(6, 6) = 1
#
# Example 2:
#
# Input: nums = [1,2,1,2,1,2,1,2]
# Output: false
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 2000
#
# -10^6 <= nums[i] <= 10^6
#
# @lc code=start
from typing import List
class Solution:
    def splitArray(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Find indices i < j < k such that
        sum(0..i-1) = sum(i+1..j-1) = sum(j+1..k-1) = sum(k+1..n-1).
        Use prefix sums; for each middle cut j, collect equal-sum cuts on the
        left, then check the right for a matching sum.

        Algorithm:
        - prefix[t] = sum(nums[:t]).
        - For j from 3..n-4: build set of sums where left of j can split equally;
          for k > j+1 check if right of j can split to a sum in that set.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        if n < 7:
            return False
        prefix = [0] * (n + 1)
        for i, x in enumerate(nums):
            prefix[i + 1] = prefix[i] + x

        def range_sum(l: int, r: int) -> int:
            # sum nums[l..r] inclusive
            return prefix[r + 1] - prefix[l]

        for j in range(3, n - 3):
            left_sums = set()
            for i in range(1, j - 1):
                left = range_sum(0, i - 1)
                mid = range_sum(i + 1, j - 1)
                if left == mid:
                    left_sums.add(left)
            if not left_sums:
                continue
            for k in range(j + 2, n - 1):
                mid = range_sum(j + 1, k - 1)
                right = range_sum(k + 1, n - 1)
                if mid == right and mid in left_sums:
                    return True
        return False
# @lc code=end

