#
# @lc app=leetcode id=3025 lang=python3
#
# [3025] Find the Number of Ways to Place People I
#
# https://leetcode.com/problems/find-the-number-of-ways-to-place-people-i/description/
#
# algorithms
# Medium (64.03%)
# Likes:    484
# Dislikes: 182
# Total Accepted:    116.4K
# Total Submissions: 181.7K
# Testcase Example:  "[[1,1],[2,2],[3,3]]"
#
#
# You are given a 2D array points of size n x 2 representing integer
# coordinates of some points on a 2D plane, where points[i] = [x_i, y_i].
#
# Count the number of pairs of points (A, B), where
#
# A is on the upper left side of B, and
#
# there are no other points in the rectangle (or line) they make
# (including the border), except for the points A and B.
#
# Return the count.
#
# Example 1:
#
# Input: points = [[1,1],[2,2],[3,3]]
#
# Output: 0
#
# Explanation:
#
# There is no way to choose A and B such that A is on the upper left side
# of B.
#
# Example 2:
#
# Input: points = [[6,2],[4,4],[2,6]]
#
# Output: 2
#
# Explanation:
#
# The left one is the pair (points[1], points[0]), where points[1] is on
# the upper left side of points[0] and the rectangle is empty.
#
# The middle one is the pair (points[2], points[1]), same as the left one
# it is a valid pair.
#
# The right one is the pair (points[2], points[0]), where points[2] is on
# the upper left side of points[0], but points[1] is inside the rectangle
# so it's not a valid pair.
#
# Example 3:
#
# Input: points = [[3,1],[1,3],[1,1]]
#
# Output: 2
#
# Explanation:
#
# The left one is the pair (points[2], points[0]), where points[2] is on
# the upper left side of points[0] and there are no other points on the
# line they form. Note that it is a valid state when the two points form a
# line.
#
# The middle one is the pair (points[1], points[2]), it is a valid pair
# same as the left one.
#
# The right one is the pair (points[1], points[0]), it is not a valid pair
# as points[2] is on the border of the rectangle.
#
# Constraints:
#
# 2 <= n <= 50
#
# points[i].length == 2
#
# 0 <= points[i][0], points[i][1] <= 50
#
# All points[i] are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def numberOfPairs(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Count pairs (A,B) where A is upper-left of B and the axis-aligned
        rectangle (including border) contains no other point. n<=50.

        Algorithm:
        - Brute all ordered pairs; A upper-left means Ax<=Bx and Ay>=By,
          and not the same point.
        - For each candidate pair, scan all other points for containment.

        Complexity: O(n^3) time, O(1) extra space.
        """
        n = len(points)
        ans = 0
        for i in range(n):
            ax, ay = points[i]
            for j in range(n):
                if i == j:
                    continue
                bx, by = points[j]
                if ax > bx or ay < by:
                    continue
                ok = True
                for k in range(n):
                    if k == i or k == j:
                        continue
                    x, y = points[k]
                    if ax <= x <= bx and by <= y <= ay:
                        ok = False
                        break
                if ok:
                    ans += 1
        return ans

    def numberOfPairs_sorted(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Same problem with the O(n^2) sweep used for the hard follow-up.

        Algorithm:
        - Sort by x asc, y desc. For each Alice i, scan Bob j>i; accept the
          first decreasing y-chain under Alice's y (blocks later Bobs).

        Complexity: O(n^2) time, O(n) space.
        """
        pts = sorted(points, key=lambda p: (p[0], -p[1]))
        n = len(pts)
        ans = 0
        for i in range(n):
            yi = pts[i][1]
            max_y = float("-inf")
            for j in range(i + 1, n):
                yj = pts[j][1]
                if yj <= yi and yj > max_y:
                    ans += 1
                    max_y = yj
        return ans
# @lc code=end
