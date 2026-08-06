#
# @lc app=leetcode id=462 lang=python3
#
# [462] Minimum Moves to Equal Array Elements II
#
# https://leetcode.com/problems/minimum-moves-to-equal-array-elements-ii/description/
#
# algorithms
# Medium (61.88%)
# Likes:    3537
# Dislikes: 132
# Total Accepted:    228K
# Total Submissions: 368.5K
# Testcase Example:  '[1,2,3]'
#
# Given an integer array nums of size n, return the minimum number of moves
# required to make all array elements equal.
# 
# In one move, you can increment or decrement an element of the array by 1.
# 
# Test cases are designed so that the answer will fit in a 32-bit integer.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3]
# Output: 2
# Explanation:
# Only two moves are needed (remember each move increments or decrements one
# element):
# [1,2,3]  =>  [2,2,3]  =>  [2,2,2]
# 
# 
# Example 2:
# 
# 
# Input: nums = [1,10,2,9]
# Output: 16
# 
# 
# 
# Constraints:
# 
# 
# n == nums.length
# 1 <= nums.length <= 10^5
# -10^9 <= nums[i] <= 10^9
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minMoves2(self, nums: List[int]) -> int:
        nums.sort()
        median = nums[len(nums) // 2]
        return sum(abs(x - median) for x in nums)
# @lc code=end

"""
Interview explanation:
The sum of absolute deviations is minimized at any median. Sorting exposes the median directly, then the minimum move count is the total distance to it.

Why median: moving the target between two sorted values changes the objective by (#left - #right); the optimum is where those counts balance.

Edge cases: for even n, either middle value is optimal. Negative numbers work because absolute distance is used.

Complexity: sorting dominates at O(n log n). Space is O(1) beyond the sort's implementation details and the input array is reordered.
"""
