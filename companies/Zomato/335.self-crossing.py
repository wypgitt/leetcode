#
# @lc app=leetcode id=335 lang=python3
#
# [335] Self Crossing
#
# https://leetcode.com/problems/self-crossing/description/
#
# algorithms
# Hard (35.77%)
# Likes:    421
# Dislikes: 523
# Total Accepted:    51.0K
# Total Submissions: 143K
# Testcase Example:  "[2,1,1,2]"
#
# You are given an array of integers distance.
#
# You start at the point (0, 0) on an X-Y plane, and you move distance[0]
# meters to the north, then distance[1] meters to the west, distance[2] meters
# to the south, distance[3] meters to the east, and so on. In other words,
# after each move, your direction changes counter-clockwise.
#
# Return true if your path crosses itself or false if it does not.
#
# Example 1:
#
# Input: distance = [2,1,1,2]
# Output: true
# Explanation: The path crosses itself at the point (0, 1).
#
# Example 2:
#
# Input: distance = [1,2,3,4]
# Output: false
# Explanation: The path does not cross itself at any point.
#
# Example 3:
#
# Input: distance = [1,1,1,2,1]
# Output: true
# Explanation: The path crosses itself at the point (0, 0).
#
# Constraints:
#
# 1 <= distance.length <= 10^5
#
# 1 <= distance[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def isSelfCrossing(self, distance: List[int]) -> bool:
        """
        Interview explanation:
        Geometry case analysis for axis-aligned spiral: a new segment can only
        cross recent ones (i-3, i-4, i-5 patterns). Check the three classic
        crossing configurations while walking the path.

        Algorithm:
        - For i from 3..n-1:
          - Case i-3: distance[i] >= distance[i-2] and distance[i-1] <= distance[i-3]
          - Case i-4: distance[i-1] == distance[i-3] and
            distance[i] + distance[i-4] >= distance[i-2]
          - Case i-5: distance[i-2] >= distance[i-4] and
            distance[i-3] >= distance[i-1] and
            distance[i] + distance[i-4] >= distance[i-2] and
            distance[i-1] + distance[i-5] >= distance[i-3]
        - Return True on any hit.

        Complexity: O(n) time, O(1) space.
        """
        d = distance
        n = len(d)
        for i in range(3, n):
            if d[i] >= d[i - 2] and d[i - 1] <= d[i - 3]:
                return True
            if i >= 4 and d[i - 1] == d[i - 3] and d[i] + d[i - 4] >= d[i - 2]:
                return True
            if (
                i >= 5
                and d[i - 2] >= d[i - 4]
                and d[i - 3] >= d[i - 1]
                and d[i] + d[i - 4] >= d[i - 2]
                and d[i - 1] + d[i - 5] >= d[i - 3]
            ):
                return True
        return False
# @lc code=end
