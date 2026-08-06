#
# @lc app=leetcode id=3353 lang=python3
#
# [3353] Minimum Total Operations
#
# https://leetcode.com/problems/minimum-total-operations/description/
#
# algorithms
# Easy (63.52%)
# Likes:    15
# Dislikes: 1
# Total Accepted:    1.5K
# Total Submissions: 2.3K
# Testcase Example:  "[1,4,2]"
#
#
# Given an array of integers nums, you can perform any number of
# operations on this array.
#
# In each operation, you can:
#
# Choose a prefix of the array.
#
# Choose an integer k (which can be negative) and add k to each element in
# the chosen prefix.
#
# A prefix of an array is a subarray that starts from the beginning of the
# array and extends to any point within it.
#
# Return the minimum number of operations required to make all elements in
# arr equal.
#
# Example 1:
#
# Input: nums = [1,4,2]
#
# Output: 2
#
# Explanation:
#
# Operation 1: Choose the prefix [1, 4] of length 2 and add -2 to each
# element of the prefix. The array becomes [-1, 2, 2].
#
# Operation 2: Choose the prefix [-1] of length 1 and add 3 to it. The
# array becomes [2, 2, 2].
#
# Thus, the minimum number of required operations is 2.
#
# Example 2:
#
# Input: nums = [10,10,10]
#
# Output: 0
#
# Explanation:
#
# All elements are already equal, so no operations are needed.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Prefix += k flips the difference between nums[i] and nums[i+1] when the
        prefix ends at i. Each adjacent inequality must be fixed once.

        Algorithm:
        - Count indices i where nums[i] != nums[i+1].

        Complexity: O(n) time, O(1) space.
        """
        return sum(a != b for a, b in zip(nums, nums[1:]))
# @lc code=end
