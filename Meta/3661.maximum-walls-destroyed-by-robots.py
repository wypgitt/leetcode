#
# @lc app=leetcode id=3661 lang=python3
#
# [3661] Maximum Walls Destroyed by Robots
#
# https://leetcode.com/problems/maximum-walls-destroyed-by-robots/description/
#
# algorithms
# Hard (47.84%)
# Likes:    344
# Dislikes: 32
# Total Accepted:    64.6K
# Total Submissions: 135K
# Testcase Example:  "[4]\n[3]\n[1,10]"
#
#
# There is an endless straight line populated with some robots and walls.
# You are given integer arrays robots, distance, and walls:
#
# robots[i] is the position of the i^th robot.
#
# distance[i] is the maximum distance the i^th robot's bullet can travel.
#
# walls[j] is the position of the j^th wall.
#
# Every robot has one bullet that can either fire to the left or the right
# at most distance[i] meters.
#
# A bullet destroys every wall in its path that lies within its range.
# Robots are fixed obstacles: if a bullet hits another robot before
# reaching a wall, it immediately stops at that robot and cannot continue.
#
# Return the maximum number of unique walls that can be destroyed by the
# robots.
#
# Notes:
#
# A wall and a robot may share the same position; the wall can be
# destroyed by the robot at that position.
#
# Robots are not destroyed by bullets.
#
# Example 1:
#
# Input: robots = [4], distance = [3], walls = [1,10]
#
# Output: 1
#
# Explanation:
#
# robots[0] = 4 fires left with distance[0] = 3, covering [1, 4] and
# destroys walls[0] = 1.
#
# Thus, the answer is 1.
#
# Example 2:
#
# Input: robots = [10,2], distance = [5,1], walls = [5,2,7]
#
# Output: 3
#
# Explanation:
#
# robots[0] = 10 fires left with distance[0] = 5, covering [5, 10] and
# destroys walls[0] = 5 and walls[2] = 7.
#
# robots[1] = 2 fires left with distance[1] = 1, covering [1, 2] and
# destroys walls[1] = 2.
#
# Thus, the answer is 3.
#
# Example 3:
#
# Input: robots = [1,2], distance = [100,1], walls = [10]
#
# Output: 0
#
# Explanation:
#
# In this example, only robots[0] can reach the wall, but its shot to the
# right is blocked by robots[1]; thus the answer is 0.
#
# Constraints:
#
# 1 <= robots.length == distance.length <= 10^5
#
# 1 <= walls.length <= 10^5
#
# 1 <= robots[i], walls[j] <= 10^9
#
# 1 <= distance[i] <= 10^5
#
# All values in robots are unique
#
# All values in walls are unique
#

# @lc code=start
from typing import List
from bisect import bisect_left
from functools import cache


class Solution:
    def maxWalls(self, robots: List[int], distance: List[int], walls: List[int]) -> int:
        """
        Interview explanation:
        Each robot shoots left or right (blocked by neighbors). DP over
        robots with the next robot's direction to avoid double-counting
        overlapping wall ranges.

        Algorithm:
        - Sort robots and walls.
        - dfs(i, j): max walls for robots[0..i], j = next robot's direction
          (0 left / 1 right). Count walls in the clipped range via bisect.
        - Answer dfs(n-1, 1).

        Complexity: O(n log n + m log m) with memo on O(n) states.
        """
        n = len(robots)
        arr = sorted(zip(robots, distance), key=lambda x: x[0])
        walls = sorted(walls)

        @cache
        def dfs(i: int, j: int) -> int:
            if i < 0:
                return 0
            left = arr[i][0] - arr[i][1]
            if i > 0:
                left = max(left, arr[i - 1][0] + 1)
            l = bisect_left(walls, left)
            r = bisect_left(walls, arr[i][0] + 1)
            ans = dfs(i - 1, 0) + r - l
            right = arr[i][0] + arr[i][1]
            if i + 1 < n:
                if j == 0:
                    right = min(right, arr[i + 1][0] - arr[i + 1][1] - 1)
                else:
                    right = min(right, arr[i + 1][0] - 1)
            l = bisect_left(walls, arr[i][0])
            r = bisect_left(walls, right + 1)
            ans = max(ans, dfs(i - 1, 1) + r - l)
            return ans

        ans = dfs(n - 1, 1)
        dfs.cache_clear()
        return ans
# @lc code=end

