#
# @lc app=leetcode id=2552 lang=python3
#
# [2552] Count Increasing Quadruplets
#
# https://leetcode.com/problems/count-increasing-quadruplets/description/
#
# algorithms
# Hard (34.49%)
# Likes:    403
# Dislikes: 73
# Total Accepted:    12.8K
# Total Submissions: 37.1K
# Testcase Example:  "[1,3,2,4,5]"
#
# Given a 0-indexed integer array nums of size n containing all numbers from 1
# to n, return the number of increasing quadruplets.
#
# A quadruplet (i, j, k, l) is increasing if:
#
#
# 0 <= i < j < k < l < n, and
#
#
# nums[i] < nums[k] < nums[j] < nums[l].
#
#
#
# Example 1:
#
# Input: nums = [1,3,2,4,5]
# Output: 2
# Explanation:
# - When i = 0, j = 1, k = 2, and l = 3, nums[i] < nums[k] < nums[j] < nums[l].
# - When i = 0, j = 1, k = 2, and l = 4, nums[i] < nums[k] < nums[j] < nums[l].
# There are no other quadruplets, so we return 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 0
# Explanation: There exists only one quadruplet with i = 0, j = 1, k = 2, l = 3,
# but since nums[j] < nums[k], we return 0.
#
#
#
# Constraints:
#
#
# 4 <= nums.length <= 4000
#
#
# 1 <= nums[i] <= nums.length
#
#
# All the integers of nums are unique. nums is a permutation.
#

# @lc code=start
from typing import List


class Solution:
    def countQuadruplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count i<j<k<l with nums[i]<nums[k]<nums[j]<nums[l] on a permutation of 1..n.
        Fix j and scan k>j while tracking left-smaller and right-greater counts.

        Algorithm:
        - For each j, build prefix counts of values left of j.
        - Walk k from n-1 down to j+1: if nums[k]>nums[j], it is a candidate l;
          if nums[k]<nums[j], multiply left-smaller[nums[k]] by current right-greater.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        ans = 0
        for j in range(n):
            left_smaller = [0] * (n + 2)
            for i in range(j):
                left_smaller[nums[i]] = 1
            for v in range(1, n + 1):
                left_smaller[v] += left_smaller[v - 1]
            right_greater = 0
            for k in range(n - 1, j, -1):
                if nums[k] > nums[j]:
                    right_greater += 1
                else:
                    ans += left_smaller[nums[k]] * right_greater
        return ans
# @lc code=end
