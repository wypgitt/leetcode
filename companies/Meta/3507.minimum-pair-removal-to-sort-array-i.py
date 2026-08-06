#
# @lc app=leetcode id=3507 lang=python3
#
# [3507] Minimum Pair Removal to Sort Array I
#
# https://leetcode.com/problems/minimum-pair-removal-to-sort-array-i/description/
#
# algorithms
# Easy (65.25%)
# Likes:    502
# Dislikes: 97
# Total Accepted:    153.8K
# Total Submissions: 235.7K
# Testcase Example:  "[5,2,3,1]"
#
#
# Given an array nums, you can perform the following operation any number
# of times:
#
# Select the adjacent pair with the minimum sum in nums. If multiple such
# pairs exist, choose the leftmost one.
#
# Replace the pair with their sum.
#
# Return the minimum number of operations needed to make the array
# non-decreasing.
#
# An array is said to be non-decreasing if each element is greater than or
# equal to its previous element (if it exists).
#
# Example 1:
#
# Input: nums = [5,2,3,1]
#
# Output: 2
#
# Explanation:
#
# The pair (3,1) has the minimum sum of 4. After replacement, nums =
# [5,2,4].
#
# The pair (2,4) has the minimum sum of 6. After replacement, nums =
# [5,6].
#
# The array nums became non-decreasing in two operations.
#
# Example 2:
#
# Input: nums = [1,2,2]
#
# Output: 0
#
# Explanation:
#
# The array nums is already sorted.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def minimumPairRemoval(self, nums: List[int]) -> int:
        """
        Interview explanation:
        n <= 50 — simulate: while not non-decreasing, merge the leftmost
        adjacent pair with minimum sum.

        Algorithm:
        - Scan for unsorted; find min adjacent sum; splice in the sum; count ops.

        Complexity: O(n^2) time, O(n) space.
        """
        a = list(nums)
        ops = 0
        while True:
            if all(a[i] <= a[i + 1] for i in range(len(a) - 1)):
                return ops
            best_i, best_s = 0, a[0] + a[1]
            for i in range(1, len(a) - 1):
                s = a[i] + a[i + 1]
                if s < best_s:
                    best_s, best_i = s, i
            a = a[:best_i] + [best_s] + a[best_i + 2 :]
            ops += 1
# @lc code=end
