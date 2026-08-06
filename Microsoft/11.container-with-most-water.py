#
# @lc app=leetcode id=11 lang=python3
#
# [11] Container With Most Water
#
# https://leetcode.com/problems/container-with-most-water/description/
#
# algorithms
# Medium (59.96%)
# Likes:    34351
# Dislikes: 2212
# Total Accepted:    5.3M
# Total Submissions: 8.9M
# Testcase Example:  '[1,8,6,2,5,4,8,3,7]'
#
# You are given an integer array height of length n. There are n vertical lines
# drawn such that the two endpoints of the i^th line are (i, 0) and (i,
# height[i]).
# 
# Find two lines that together with the x-axis form a container, such that the
# container contains the most water.
# 
# Return the maximum amount of water a container can store.
# 
# Notice that you may not slant the container.
# 
# 
# Example 1:
# 
# 
# Input: height = [1,8,6,2,5,4,8,3,7]
# Output: 49
# Explanation: The above vertical lines are represented by array
# [1,8,6,2,5,4,8,3,7]. In this case, the max area of water (blue section) the
# container can contain is 49.
# 
# 
# Example 2:
# 
# 
# Input: height = [1,1]
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# n == height.length
# 2 <= n <= 10^5
# 0 <= height[i] <= 10^4
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def maxArea(self, height: List[int]) -> int:
        """
        Interview explanation:
        Two pointers work because the area is limited by the shorter wall. With
        pointers at both ends, moving the taller wall cannot improve the height
        limit and only reduces width, so the only useful move is to advance the
        shorter wall in search of a taller boundary.

        Algorithm:
        - left starts at 0, right starts at n - 1.
        - Compute width * min(height[left], height[right]).
        - Move the pointer at the smaller height inward.

        Edge cases and tests:
        - Two lines produce their single possible area.
        - Monotonic heights still work because every width is considered only
          when it can still be optimal.
        - Equal heights can move either pointer.

        Complexity: O(n) time, O(1) space.
        """
        left, right = 0, len(height) - 1
        best = 0

        while left < right:
            best = max(best, (right - left) * min(height[left], height[right]))
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1

        return best
# @lc code=end


