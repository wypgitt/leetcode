#
# @lc app=leetcode id=45 lang=python3
#
# [45] Jump Game II
#
# https://leetcode.com/problems/jump-game-ii/description/
#
# algorithms
# Medium (42.81%)
# Likes:    16535
# Dislikes: 707
# Total Accepted:    2.1M
# Total Submissions: 5M
# Testcase Example:  '[2,3,1,1,4]'
#
# You are given a 0-indexed array of integers nums of length n. You are
# initially positioned at index 0.
# 
# Each element nums[i] represents the maximum length of a forward jump from
# index i. In other words, if you are at index i, you can jump to any index (i
# + j) where:
# 
# 
# 0 <= j <= nums[i] and
# i + j < n
# 
# 
# Return the minimum number of jumps to reach index n - 1. The test cases are
# generated such that you can reach index n - 1.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,3,1,1,4]
# Output: 2
# Explanation: The minimum number of jumps to reach the last index is 2. Jump 1
# step from index 0 to 1, then 3 steps to the last index.
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,3,0,1,4]
# Output: 2
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^4
# 0 <= nums[i] <= 1000
# It's guaranteed that you can reach nums[n - 1].
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def jump(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Treat jumps like BFS levels over array indices, but compress each level
        into a range. current_end is the farthest index reachable with the
        current number of jumps; farthest is the best reach discovered while
        scanning that range. When the scan reaches current_end, we must take one
        more jump and extend the range to farthest.

        Edge cases and tests:
        - Length 1 needs 0 jumps.
        - Arrays where first jump reaches the end return 1.
        - Constraints guarantee reachability.

        Complexity: O(n) time, O(1) space.
        """
        jumps = 0
        current_end = 0
        farthest = 0

        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == current_end:
                jumps += 1
                current_end = farthest

        return jumps
# @lc code=end


