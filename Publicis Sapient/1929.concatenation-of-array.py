#
# @lc app=leetcode id=1929 lang=python3
#
# [1929] Concatenation of Array
#
# https://leetcode.com/problems/concatenation-of-array/description/
#
# algorithms
# Easy (90.09%)
# Likes:    4292
# Dislikes: 466
# Total Accepted:    1.6M
# Total Submissions: 1.8M
# Testcase Example:  "[1,2,1]"
#
# Given an integer array nums of length n, you want to create an array ans of
# length 2n where ans[i] == nums[i] and ans[i + n] == nums[i] for 0 <= i < n
# (0-indexed).
#
# Specifically, ans is the concatenation of two nums arrays.
#
# Return the array ans.
#
# Example 1:
#
# Input: nums = [1,2,1]
# Output: [1,2,1,1,2,1]
# Explanation: The array ans is formed as follows:
# - ans = [nums[0],nums[1],nums[2],nums[0],nums[1],nums[2]]
# - ans = [1,2,1,1,2,1]
#
# Example 2:
#
# Input: nums = [1,3,2,1]
# Output: [1,3,2,1,1,3,2,1]
# Explanation: The array ans is formed as follows:
# - ans = [nums[0],nums[1],nums[2],nums[3],nums[0],nums[1],nums[2],nums[3]]
# - ans = [1,3,2,1,1,3,2,1]
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Return nums concatenated with itself: ans of length 2n with ans[i]=nums[i%n].

        Algorithm:
        - return nums + nums (or list comprehension).

        Complexity: O(n) time/space.
        """
        return nums + nums

    def getConcatenation_index(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: allocate 2n and fill via i % n.

        Algorithm:
        - ans[i] = nums[i % n] for i in 0..2n-1.

        Complexity: O(n) time/space.
        """
        n = len(nums)
        return [nums[i % n] for i in range(2 * n)]
# @lc code=end
