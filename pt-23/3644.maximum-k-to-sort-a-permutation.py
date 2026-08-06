#
# @lc app=leetcode id=3644 lang=python3
#
# [3644] Maximum K to Sort a Permutation
#
# https://leetcode.com/problems/maximum-k-to-sort-a-permutation/description/
#
# algorithms
# Medium (37.60%)
# Likes:    103
# Dislikes: 36
# Total Accepted:    33.8K
# Total Submissions: 89.9K
# Testcase Example:  "[0,3,2,1]"
#
#
# You are given an integer array nums of length n, where nums is a
# permutation of the numbers in the range [0..n - 1].
#
# You may swap elements at indices i and j only if nums[i] AND nums[j] ==
# k, where AND denotes the bitwise AND operation and k is a non-negative
# integer.
#
# Return the maximum value of k such that the array can be sorted in
# non-decreasing order using any number of such swaps. If nums is already
# sorted, return 0.
#
# Example 1:
#
# Input: nums = [0,3,2,1]
#
# Output: 1
#
# Explanation:
#
# Choose k = 1. Swapping nums[1] = 3 and nums[3] = 1 is allowed since
# nums[1] AND nums[3] == 1, resulting in a sorted permutation: [0, 1, 2,
# 3].
#
# Example 2:
#
# Input: nums = [0,1,3,2]
#
# Output: 2
#
# Explanation:
#
# Choose k = 2. Swapping nums[2] = 3 and nums[3] = 2 is allowed since
# nums[2] AND nums[3] == 2, resulting in a sorted permutation: [0, 1, 2,
# 3].
#
# Example 3:
#
# Input: nums = [3,2,1,0]
#
# Output: 0
#
# Explanation:
#
# Only k = 0 allows sorting since no greater k allows the required swaps
# where nums[i] AND nums[j] == k.
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


class Solution:
    def sortPermutation(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Swaps require nums[i] AND nums[j] == k. Max k is the AND of every
        value that is not already in its sorted position; sorted → 0.

        Algorithm:
        - AND all nums[i] where nums[i] != i; if none, return 0.

        Complexity: O(n) time, O(1) space.
        """
        ans = -1
        for i, x in enumerate(nums):
            if x != i:
                ans &= x
        return 0 if ans == -1 else ans

    def sortPermutation_reduce(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: collect misplaced values and fold with bitwise AND.

        Algorithm:
        - misplaced = [x for i,x in enumerate(nums) if x != i]
        - return 0 if empty else functools.reduce(and_, misplaced).

        Complexity: O(n) time, O(n) space.
        """
        from functools import reduce
        from operator import and_

        misplaced = [x for i, x in enumerate(nums) if x != i]
        return 0 if not misplaced else reduce(and_, misplaced)
# @lc code=end

