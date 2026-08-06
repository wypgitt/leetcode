#
# @lc app=leetcode id=812 lang=python3
#
# [812] Largest Triangle Area
#
# https://leetcode.com/problems/largest-triangle-area/description/
#
# algorithms
# Easy (72.02%)
# Likes:    857
# Dislikes: 1741
# Total Accepted:    189K
# Total Submissions: 262K
# Testcase Example:  "[[0,0],[0,1],[1,0],[0,2],[2,0]]"
#
# Given an array of points on the X-Y plane points where points[i] = [x_i,
# y_i], return the area of the largest triangle that can be formed by any three
# different points. Answers within 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input: points = [[0,0],[0,1],[1,0],[0,2],[2,0]]
# Output: 2.00000
# Explanation: The five points are shown in the above figure. The red triangle
# is the largest.
#
# Example 2:
#
# Input: points = [[1,0],[0,0],[0,1]]
# Output: 0.50000
#
# Constraints:
#
# 3 <= points.length <= 50
#
# -50 <= x_i, y_i <= 50
#
# All the given points are unique.
#

# @lc code=start

from typing import List
from itertools import combinations


class Solution:
    def largestTriangleArea(self, points: List[List[int]]) -> float:
        """
        Interview explanation:
        Brute-force all triples; area via shoelace formula
        |x1(y2-y3)+x2(y3-y1)+x3(y1-y2)|/2. Track maximum.

        Algorithm:
        - Triple nested loops; update max absolute shoelace / 2.

        Complexity: O(n^3) time, O(1) space.
        """
        def area(a, b, c):
            return abs(
                a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])
            ) / 2.0

        ans = 0.0
        n = len(points)
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    ans = max(ans, area(points[i], points[j], points[k]))
        return ans

    def largestTriangleArea_combinations(self, points: List[List[int]]) -> float:
        """
        Interview explanation:
        Same shoelace over itertools.combinations of 3 points.

        Algorithm:
        - For each triple from combinations, compute shoelace area; take max.

        Complexity: O(n^3) time, O(1) extra space.
        """
        ans = 0.0
        for a, b, c in combinations(points, 3):
            ans = max(
                ans,
                abs(a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])) / 2.0,
            )
        return ans
# @lc code=end
