#
# @lc app=leetcode id=3464 lang=python3
#
# [3464] Maximize the Distance Between Points on a Square
#
# https://leetcode.com/problems/maximize-the-distance-between-points-on-a-square/description/
#
# algorithms
# Hard (50.81%)
# Likes:    157
# Dislikes: 20
# Total Accepted:    55.5K
# Total Submissions: 109.3K
# Testcase Example:  "2\n[[0,2],[2,0],[2,2],[0,0]]\n4"
#
#
# You are given an integer side, representing the edge length of a square
# with corners at (0, 0), (0, side), (side, 0), and (side, side) on a
# Cartesian plane.
#
# You are also given a positive integer k and a 2D integer array points,
# where points[i] = [x_i, y_i] represents the coordinate of a point lying
# on the boundary of the square.
#
# You need to select k elements among points such that the minimum
# Manhattan distance between any two points is maximized.
#
# Return the maximum possible minimum Manhattan distance between the
# selected k points.
#
# The Manhattan Distance between two cells (x_i, y_i) and (x_j, y_j) is
# |x_i - x_j| + |y_i - y_j|.
#
# Example 1:
#
# Input: side = 2, points = [[0,2],[2,0],[2,2],[0,0]], k = 4
#
# Output: 2
#
# Explanation:
#
# Select all four points.
#
# Example 2:
#
# Input: side = 2, points = [[0,0],[1,2],[2,0],[2,2],[2,1]], k = 4
#
# Output: 1
#
# Explanation:
#
# Select the points (0, 0), (2, 0), (2, 2), and (2, 1).
#
# Example 3:
#
# Input: side = 2, points = [[0,0],[0,1],[0,2],[1,2],[2,0],[2,2],[2,1]], k
# = 5
#
# Output: 1
#
# Explanation:
#
# Select the points (0, 0), (0, 1), (0, 2), (1, 2), and (2, 2).
#
# Constraints:
#
# 1 <= side <= 10^9
#
# 4 <= points.length <= min(4 * side, 15 * 10^3)
#
# points[i] == [x_i, y_i]
#
# The input is generated such that:
#
# points[i] lies on the boundary of the square.
#
# All points[i] are unique.
#
# 4 <= k <= min(25, points.length)
#

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    def maxDistance(self, side: int, points: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Maximize the minimum Manhattan distance among k boundary points.
        Map the square perimeter to a circle, binary-search the distance,
        and greedily place points.

        Algorithm:
        - Map (x,y) to a 1D perimeter coordinate in [0, 4*side); sort.
        - Binary search d; for each start, greedily pick next points at least
          d ahead, staying within start + perimeter - d (circular gap).
        - Feasible => try larger d.

        Complexity: O(n^2 log n * log side) with n starts and bisect, O(n) space.
        """
        nums: List[int] = []
        for x, y in points:
            if x == 0:
                nums.append(y)
            elif y == side:
                nums.append(side + x)
            elif x == side:
                nums.append(side * 3 - y)
            else:
                nums.append(side * 4 - x)
        nums.sort()

        def check(lo: int) -> bool:
            perimeter = side * 4
            for start in nums:
                end = start + perimeter - lo
                cur = start
                ok = True
                for _ in range(k - 1):
                    j = bisect_left(nums, cur + lo)
                    if j == len(nums) or nums[j] > end:
                        ok = False
                        break
                    cur = nums[j]
                if ok:
                    return True
            return False

        lo, hi = 0, side
        while lo < hi:
            mid = (lo + hi + 1) >> 1
            if check(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end

