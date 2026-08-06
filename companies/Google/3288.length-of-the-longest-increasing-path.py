#
# @lc app=leetcode id=3288 lang=python3
#
# [3288] Length of the Longest Increasing Path
#
# https://leetcode.com/problems/length-of-the-longest-increasing-path/description/
#
# algorithms
# Hard (19.90%)
# Likes:    105
# Dislikes: 2
# Total Accepted:    6.3K
# Total Submissions: 31.7K
# Testcase Example:  "[[3,1],[2,2],[4,1],[0,0],[5,3]]\n1"
#
#
# You are given a 2D array of integers coordinates of length n and an
# integer k, where 0 <= k < n.
#
# coordinates[i] = [x_i, y_i] indicates the point (x_i, y_i) in a 2D
# plane.
#
# An increasing path of length m is defined as a list of points (x_1,
# y_1), (x_2, y_2), (x_3, y_3), ..., (x_m, y_m) such that:
#
# x_i < x_i + 1 and y_i < y_i + 1 for all i where 1 <= i < m.
#
# (x_i, y_i) is in the given coordinates for all i where 1 <= i <= m.
#
# Return the maximum length of an increasing path that contains
# coordinates[k].
#
# Example 1:
#
# Input: coordinates = [[3,1],[2,2],[4,1],[0,0],[5,3]], k = 1
#
# Output: 3
#
# Explanation:
#
# (0, 0), (2, 2), (5, 3) is the longest increasing path that contains (2,
# 2).
#
# Example 2:
#
# Input: coordinates = [[2,1],[7,0],[5,6]], k = 2
#
# Output: 2
#
# Explanation:
#
# (2, 1), (5, 6) is the longest increasing path that contains (5, 6).
#
# Constraints:
#
# 1 <= n == coordinates.length <= 10^5
#
# coordinates[i].length == 2
#
# 0 <= coordinates[i][0], coordinates[i][1] <= 10^9
#
# All elements in coordinates are distinct.
#
# 0 <= k <= n - 1
#

# @lc code=start
import bisect
from typing import List


class Solution:
    def maxPathLength(self, coordinates: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Longest strictly increasing (x and y) path that must include point k.
        Split into points southwest of k and northeast of k; chain LIS + 1.

        Algorithm:
        - left: x < xk and y < yk; right: x > xk and y > yk.
        - Sort by (x, -y) and patience-LIS on y for each side.
        - Answer = LIS(left) + 1 + LIS(right).

        Complexity: O(n log n) time, O(n) space.
        """
        tx, ty = coordinates[k]
        left, right = [], []
        for x, y in coordinates:
            if x < tx and y < ty:
                left.append((x, y))
            elif x > tx and y > ty:
                right.append((x, y))

        def lis(points: List[tuple]) -> int:
            if not points:
                return 0
            points.sort(key=lambda p: (p[0], -p[1]))
            tails: List[int] = []
            for _, y in points:
                i = bisect.bisect_left(tails, y)
                if i == len(tails):
                    tails.append(y)
                else:
                    tails[i] = y
            return len(tails)

        return lis(left) + 1 + lis(right)
# @lc code=end
