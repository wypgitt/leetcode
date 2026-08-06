#
# @lc app=leetcode id=3942 lang=python3
#
# [3942] Minimum Operations to Sort a Permutation
#
# https://leetcode.com/problems/minimum-operations-to-sort-a-permutation/description/
#
# algorithms
# Medium (27.99%)
# Likes:    90
# Dislikes: 8
# Total Accepted:    15.3K
# Total Submissions: 54.8K
# Testcase Example:  "[0,2,1]"
#
#
# You are given an integer array nums of length n, where nums is a
# permutation of the integers from 0 to n - 1.
#
# You may perform only the following operations:
#
# Reverse the entire array.
#
# Rotate Left by One: Move the first element to the end of the array, and
# rest elements to left by one position.
#
# Return an integer denoting the minimum number of operations required to
# sort the array in increasing order. If it is not possible to sort the
# array using only the given operations, return -1.
#
# Example 1:
#
# Input: nums = [0,2,1]
#
# Output: 2
#
# Explanation:
#
# Rotate Left by one: [2, 1, 0]
#
# Reverse the array: [0, 1, 2]
#
# The array becomes sorted in 2 operations, which is minimal
#
# Example 2:
#
# Input: nums = [1,0,2]
#
# Output: 2
#
# Explanation:
#
# Reverse the array: [2, 0, 1]
#
# Rotate Left by one: [0, 1, 2]
#
# The array becomes sorted in 2 operations, which is minimal.
#
# Example 3:
#
# Input: nums = [2,0,1,3]
#
# Output: -1
#
# Explanation:
#
# It is impossible to reach [2, 0, 1, 3]. Thus, the answer is -1.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 0 <= nums[i] <= n - 1
#
# nums is a permutation of integers from 0 to n - 1.
#

# @lc code=start

from typing import List
from math import inf


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Left-rotate and full reverse generate the dihedral actions on a cycle.
        The permutation is sortable iff values form an increasing circular
        sequence from 0 clockwise or counterclockwise; count min rotates/reverses.

        Algorithm:
        - zero = index of 0.
        - check(step): walking step ±1 from zero is strictly increasing by 1.
        - If clockwise: min(zero, n - zero + 2) ops.
        - If counterclockwise: min(zero + 2, n - zero) ops.
        - Else impossible (-1).

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        zero = nums.index(0)

        def check(step: int) -> bool:
            for i in range(1, n):
                prev = (zero + (i - 1) * step) % n
                curr = (zero + i * step) % n
                if nums[prev] > nums[curr]:
                    return False
            return True

        ans = inf
        if check(1):
            ans = min(ans, zero, n - zero + 2)
        if check(-1):
            ans = min(ans, zero + 2, n - zero)
        return -1 if ans is inf else ans
# @lc code=end
