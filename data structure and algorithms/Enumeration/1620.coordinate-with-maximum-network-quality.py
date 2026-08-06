#
# @lc app=leetcode id=1620 lang=python3
#
# [1620] Coordinate With Maximum Network Quality
#
# https://leetcode.com/problems/coordinate-with-maximum-network-quality/description/
#
# algorithms
# Medium (39.83%)
# Likes:    93
# Dislikes: 277
# Total Accepted:    12.1K
# Total Submissions: 30.4K
# Testcase Example:  "[[1,2,5],[2,1,7],[3,1,9]]"
#
# You are given an array of network towers towers, where towers[i] = [x_i, y_i,
# q_i] denotes the i^th network tower with location (x_i, y_i) and quality
# factor q_i. All the coordinates are integral coordinates on the X-Y plane,
# and the distance between the two coordinates is the Euclidean distance.
#
# You are also given an integer radius where a tower is reachable if the
# distance is less than or equal to radius. Outside that distance, the signal
# becomes garbled, and the tower is not reachable.
#
# The signal quality of the i^th tower at a coordinate (x, y) is calculated
# with the formula ⌊q_i / (1 + d)⌋, where d is the distance between the tower
# and the coordinate. The network quality at a coordinate is the sum of the
# signal qualities from all the reachable towers.
#
# Return the array [c_x, c_y] representing the integral coordinate (c_x, c_y)
# where the network quality is maximum. If there are multiple coordinates with
# the same network quality, return the lexicographically minimum non-negative
# coordinate.
#
# Note:
#
# A coordinate (x1, y1) is lexicographically smaller than (x2, y2) if either:
#
# x1 < x2, or
#
# x1 == x2 and y1 < y2.
#
# ⌊val⌋ is the greatest integer less than or equal to val (the floor function).
#
# Example 1:
#
# Input: towers = [[1,2,5],[2,1,7],[3,1,9]], radius = 2
# Output: [2,1]
# Explanation: At coordinate (2, 1) the total quality is 13.
# - Quality of 7 from (2, 1) results in ⌊7 / (1 + sqrt(0)⌋ = ⌊7⌋ = 7
# - Quality of 5 from (1, 2) results in ⌊5 / (1 + sqrt(2)⌋ = ⌊2.07⌋ = 2
# - Quality of 9 from (3, 1) results in ⌊9 / (1 + sqrt(1)⌋ = ⌊4.5⌋ = 4
# No other coordinate has a higher network quality.
#
# Example 2:
#
# Input: towers = [[23,11,21]], radius = 9
# Output: [23,11]
# Explanation: Since there is only one tower, the network quality is highest
# right at the tower's location.
#
# Example 3:
#
# Input: towers = [[1,2,13],[2,1,7],[0,1,9]], radius = 2
# Output: [1,2]
# Explanation: Coordinate (1, 2) has the highest network quality.
#
# Constraints:
#
# 1 <= towers.length <= 50
#
# towers[i].length == 3
#
# 0 <= x_i, y_i, q_i <= 50
#
# 1 <= radius <= 50
#

# @lc code=start
from typing import List
import math


class Solution:
    def bestCoordinate(self, towers: List[List[int]], radius: int) -> List[int]:
        """
        Interview explanation:
        Quality at (x,y) = sum floor(q/(1+d)) for towers within radius.
        Coordinates in [0,50]; brute all integer points; pick max quality, then
        lexicographically smallest (x,y).

        Algorithm (brute force):
        - For x,y in 0..50 compute quality; track best.

        Complexity: O(51*51*|towers|) time.
        """
        best_q = -1
        best = [0, 0]
        for x in range(51):
            for y in range(51):
                q = 0
                for tx, ty, tq in towers:
                    d = math.hypot(x - tx, y - ty)
                    if d <= radius:
                        q += int(tq / (1 + d))
                if q > best_q or (q == best_q and [x, y] < best):
                    best_q = q
                    best = [x, y]
        return best

    def bestCoordinate_bounded(self, towers: List[List[int]], radius: int) -> List[int]:
        """
        Interview explanation:
        Alternate: restrict search to bounding box of towers (still small grid).

        Algorithm:
        - max_x/max_y from towers; scan [0..max_x]x[0..max_y] same quality formula.

        Complexity: O(X*Y*|towers|) time.
        """
        if not towers:
            return [0, 0]
        max_x = max(t[0] for t in towers)
        max_y = max(t[1] for t in towers)
        best_q = -1
        best = [0, 0]
        for x in range(max_x + 1):
            for y in range(max_y + 1):
                q = 0
                for tx, ty, tq in towers:
                    d = math.hypot(x - tx, y - ty)
                    if d <= radius:
                        q += int(tq / (1 + d))
                if q > best_q:
                    best_q = q
                    best = [x, y]
        return best
# @lc code=end
