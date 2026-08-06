#
# @lc app=leetcode id=2357 lang=python3
#
# [2357] Make Array Zero by Subtracting Equal Amounts
#
# https://leetcode.com/problems/make-array-zero-by-subtracting-equal-amounts/description/
#
# algorithms
# Easy (73.89%)
# Likes:    1333
# Dislikes: 62
# Total Accepted:    187.7K
# Total Submissions: 254.1K
# Testcase Example:  "[1,5,0,3,5]"
#
# You are given a non-negative integer array nums. In one operation, you must:
#
#
# Choose a positive integer x such that x is less than or equal to the smallest
# non-zero element in nums.
#
#
# Subtract x from every positive element in nums.
#
# Return the minimum number of operations to make every element in nums equal to
# 0.
#
#
#
# Example 1:
#
# Input: nums = [1,5,0,3,5]
# Output: 3
# Explanation:
# In the first operation, choose x = 1. Now, nums = [0,4,0,2,4].
# In the second operation, choose x = 2. Now, nums = [0,2,0,0,2].
# In the third operation, choose x = 2. Now, nums = [0,0,0,0,0].
#
# Example 2:
#
# Input: nums = [0]
# Output: 0
# Explanation: Each element in nums is already 0 so no operations are needed.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# 0 <= nums[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Each op subtracts a positive x from all positives. Min ops to zero array.

        Algorithm:
        - Each distinct positive value needs one op => count unique non-zeros.

        Complexity: O(n) time, O(n) space.
        """
        return len({x for x in nums if x > 0})

    def minimumOperations_sort(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort unique positives; each distinct step is one operation.

        Algorithm:
        - set of positives length.

        Complexity: O(n) time, O(n) space.
        """
        return len(set(nums) - {0})
# @lc code=end
