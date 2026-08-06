#
# @lc app=leetcode id=3637 lang=python3
#
# [3637] Trionic Array I
#
# https://leetcode.com/problems/trionic-array-i/description/
#
# algorithms
# Easy (49.52%)
# Likes:    478
# Dislikes: 40
# Total Accepted:    200.2K
# Total Submissions: 404.2K
# Testcase Example:  "[1,3,5,4,2,6]"
#
#
# You are given an integer array nums of length n.
#
# An array is trionic if there exist indices 0 < p < q < n − 1 such that:
#
# nums[0...p] is strictly increasing,
#
# nums[p...q] is strictly decreasing,
#
# nums[q...n − 1] is strictly increasing.
#
# Return true if nums is trionic, otherwise return false.
#
# Example 1:
#
# Input: nums = [1,3,5,4,2,6]
#
# Output: true
#
# Explanation:
#
# Pick p = 2, q = 4:
#
# nums[0...2] = [1, 3, 5] is strictly increasing (1 < 3 < 5).
#
# nums[2...4] = [5, 4, 2] is strictly decreasing (5 > 4 > 2).
#
# nums[4...5] = [2, 6] is strictly increasing (2 < 6).
#
# Example 2:
#
# Input: nums = [2,1,3]
#
# Output: false
#
# Explanation:
#
# There is no way to pick p and q to form the required three segments.
#
# Constraints:
#
# 3 <= n <= 100
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def isTrionic(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Check for a single peak then valley: strictly up, strictly down,
        strictly up, covering the whole array.

        Algorithm:
        - Advance p while strictly increasing.
        - Advance q while strictly decreasing.
        - Advance i while strictly increasing.
        - Valid iff 0 < p < q < i == n-1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        p = 0
        while p + 1 < n and nums[p] < nums[p + 1]:
            p += 1
        q = p
        while q + 1 < n and nums[q] > nums[q + 1]:
            q += 1
        i = q
        while i + 1 < n and nums[i] < nums[i + 1]:
            i += 1
        return 0 < p < q < i == n - 1
# @lc code=end

