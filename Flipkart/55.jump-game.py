#
# @lc app=leetcode id=55 lang=python3
#
# [55] Jump Game
#
# https://leetcode.com/problems/jump-game/description/
#
# algorithms
# Medium (40.83%)
# Likes:    21791
# Dislikes: 1493
# Total Accepted:    3.2M
# Total Submissions: 7.8M
# Testcase Example:  '[2,3,1,1,4]'
#
# You are given an integer array nums. You are initially positioned at the
# array's first index, and each element in the array represents your maximum
# jump length at that position.
# 
# Return true if you can reach the last index, or false otherwise.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,3,1,1,4]
# Output: true
# Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.
# 
# 
# Example 2:
# 
# 
# Input: nums = [3,2,1,0,4]
# Output: false
# Explanation: You will always arrive at index 3 no matter what. Its maximum
# jump length is 0, which makes it impossible to reach the last index.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^4
# 0 <= nums[i] <= 10^5
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        The only state needed is the farthest reachable index so far. If the
        scan reaches an index greater than farthest, that index is impossible and
        the end cannot be reached. Otherwise update farthest with i + nums[i].

        Edge cases and tests:
        - Single element is already at the end.
        - A zero is harmless if farthest can jump past it.
        - A zero that blocks progress returns False.

        Complexity: O(n) time, O(1) space.
        """
        farthest = 0
        for i, jump in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + jump)
            if farthest >= len(nums) - 1:
                return True
        return True
# @lc code=end


