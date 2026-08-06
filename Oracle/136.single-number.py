#
# @lc app=leetcode id=136 lang=python3
#
# [136] Single Number
#
# https://leetcode.com/problems/single-number/description/
#
# algorithms
# Easy (78.1%)
# Likes:    19039
# Dislikes: 914
# Total Accepted:    4.8M
# Total Submissions: 6.2M
# Testcase Example:  "[2,2,1]"
#
# Given a non-empty array of integers nums, every element appears twice except
# for one. Find that single one.
#
# You must implement a solution with a linear runtime complexity and use only
# constant extra space.
#
# Example 1:
#
# Input: nums = [2,2,1]
#
# Output: 1
#
# Example 2:
#
# Input: nums = [4,1,2,1,2]
#
# Output: 4
#
# Example 3:
#
# Input: nums = [1]
#
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# -3 * 10^4 <= nums[i] <= 3 * 10^4
#
# Each element in the array appears twice except for one element which appears
# only once.
#

# @lc code=start
from typing import List
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        """
        Interview explanation:
        XOR cancels pairs: a ^ a = 0 and a ^ 0 = a. XORing everything leaves
        the unique number. Best O(1)-space solution.

        Algorithm:
        - Fold XOR across the array; return the accumulator.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for x in nums:
            ans ^= x
        return ans

    def singleNumberHash(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count frequencies (or use a set toggle). The element with count 1 is
        the answer. Uses extra memory.

        Algorithm:
        - Toggle membership in a set for each number; the remaining element is unique.

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        for x in nums:
            if x in seen:
                seen.remove(x)
            else:
                seen.add(x)
        return next(iter(seen))
# @lc code=end
