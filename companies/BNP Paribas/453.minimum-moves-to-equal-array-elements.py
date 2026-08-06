#
# @lc app=leetcode id=453 lang=python3
#
# [453] Minimum Moves to Equal Array Elements
#
# https://leetcode.com/problems/minimum-moves-to-equal-array-elements/description/
#
# algorithms
# Medium (58.97%)
# Likes:    2849
# Dislikes: 1914
# Total Accepted:    226K
# Total Submissions: 383K
# Testcase Example:  "[1,2,3]"
#
# Given an integer array nums of size n, return the minimum number of moves
# required to make all array elements equal.
#
# In one move, you can increment n - 1 elements of the array by 1.
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: 3
# Explanation: Only three moves are needed (remember each move increments two
# elements):
# [1,2,3] => [2,3,3] => [3,4,3] => [4,4,4]
#
# Example 2:
#
# Input: nums = [1,1,1]
# Output: 0
#
# Constraints:
#
# n == nums.length
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# The answer is guaranteed to fit in a 32-bit integer.
#

# @lc code=start
from typing import List


class Solution:
    def minMoves(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Incrementing n-1 elements by 1 ≡ decrementing one element by 1.
        Equalizing by decrementing everything down to the minimum takes
        sum(nums[i] - min) moves.

        Algorithm:
        - m = min(nums); return sum(x - m for x in nums).

        Complexity: O(n) time, O(1) space.
        """
        m = min(nums)
        return sum(x - m for x in nums)
# @lc code=end
