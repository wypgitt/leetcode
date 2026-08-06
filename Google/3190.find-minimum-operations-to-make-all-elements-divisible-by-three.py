#
# @lc app=leetcode id=3190 lang=python3
#
# [3190] Find Minimum Operations to Make All Elements Divisible by Three
#
# https://leetcode.com/problems/find-minimum-operations-to-make-all-elements-divisible-by-three/description/
#
# algorithms
# Easy (90.82%)
# Likes:    537
# Dislikes: 34
# Total Accepted:    283.5K
# Total Submissions: 312.1K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given an integer array nums. In one operation, you can add or
# subtract 1 from any element of nums.
#
# Return the minimum number of operations to make all elements of nums
# divisible by 3.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
#
# Output: 3
#
# Explanation:
#
# All array elements can be made divisible by 3 using 3 operations:
#
# Subtract 1 from 1.
#
# Add 1 to 2.
#
# Subtract 1 from 4.
#
# Example 2:
#
# Input: nums = [3,6,9]
#
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 50
#

# @lc code=start

from typing import List


class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Each +/-1 operation changes a value by 1. Residue 0 needs 0 ops; 1 or 2
        each need one op to reach a multiple of 3.

        Algorithm:
        - Count elements with nums[i] % 3 != 0.

        Complexity: O(n) time, O(1) space.
        """
        return sum(1 for x in nums if x % 3)

    def minimumOperations_explicit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same residue idea spelled out with min(r, 3-r) for each element.

        Algorithm:
        - For each x, add min(x%3, 3-x%3); for r in {0,1,2} this is 0/1/1.

        Complexity: O(n) time, O(1) space.
        """
        return sum(min(x % 3, 3 - x % 3) for x in nums)
# @lc code=end
