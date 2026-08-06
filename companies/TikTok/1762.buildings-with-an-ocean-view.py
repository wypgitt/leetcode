#
# @lc app=leetcode id=1762 lang=python3
#
# [1762] Buildings With an Ocean View
#
# https://leetcode.com/problems/buildings-with-an-ocean-view/description/
#
# algorithms
# Medium (80.87%)
# Likes:    1324
# Dislikes: 151
# Total Accepted:    344.8K
# Total Submissions: 426.3K
# Testcase Example:  "[4,2,3,1]"
#
#
# There are n buildings in a line. You are given an integer array heights
# of size n that represents the heights of the buildings in the line.
#
# The ocean is to the right of the buildings. A building has an ocean view
# if the building can see the ocean without obstructions. Formally, a
# building has an ocean view if all the buildings to its right have a
# smaller height.
#
# Return a list of indices (0-indexed) of buildings that have an ocean
# view, sorted in increasing order.
#
# Example 1:
#
# Input: heights = [4,2,3,1]
# Output: [0,2,3]
# Explanation: Building 1 (0-indexed) does not have an ocean view because
# building 2 is taller.
#
# Example 2:
#
# Input: heights = [4,3,2,1]
# Output: [0,1,2,3]
# Explanation: All the buildings have an ocean view.
#
# Example 3:
#
# Input: heights = [1,3,2,4]
# Output: [3]
# Explanation: Only building 3 has an ocean view.
#
# Constraints:
#
# 1 <= heights.length <= 10^5
#
# 1 <= heights[i] <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def findBuildings(self, heights: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium: ocean is to the right; a building has an ocean view iff it is
        strictly taller than every building to its right. Scan right→left with
        a running max.

        Algorithm:
        - mx=0; for i from n-1..0: if heights[i] > mx: record i; mx=heights[i].
        - Reverse the recorded indices.

        Complexity: O(n) time, O(k) output space.
        """
        ans = []
        mx = 0
        for i in range(len(heights) - 1, -1, -1):
            if heights[i] > mx:
                ans.append(i)
                mx = heights[i]
        ans.reverse()
        return ans

    def findBuildings_stack(self, heights: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate monotonic stack left→right: keep strictly decreasing heights;
        anything ≤ current loses its ocean view.

        Algorithm:
        - While stack top height ≤ current: pop; then push index.

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        for i, h in enumerate(heights):
            while stack and heights[stack[-1]] <= h:
                stack.pop()
            stack.append(i)
        return stack
# @lc code=end
