#
# @lc app=leetcode id=593 lang=python3
#
# [593] Valid Square
#
# https://leetcode.com/problems/valid-square/description/
#
# algorithms
# Medium (44.98%)
# Likes:    1125
# Dislikes: 914
# Total Accepted:    130.5K
# Total Submissions: 290.2K
# Testcase Example:  '[0,0]\n[1,1]\n[1,0]\n[0,1]'
#
# Given the coordinates of four points in 2D space p1, p2, p3 and p4, return
# true if the four points construct a square.
# 
# The coordinate of a point pi is represented as [xi, yi]. The input is not
# given in any order.
# 
# A valid square has four equal sides with positive length and four equal
# angles (90-degree angles).
# 
# 
# Example 1:
# 
# 
# Input: p1 = [0,0], p2 = [1,1], p3 = [1,0], p4 = [0,1]
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: p1 = [0,0], p2 = [1,1], p3 = [1,0], p4 = [0,12]
# Output: false
# 
# 
# Example 3:
# 
# 
# Input: p1 = [1,0], p2 = [-1,0], p3 = [0,1], p4 = [0,-1]
# Output: true
# 
# 
# 
# Constraints:
# 
# 
# p1.length == p2.length == p3.length == p4.length == 2
# -10^4 <= xi, yi <= 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def validSquare(self, p1: List[int], p2: List[int], p3: List[int], p4: List[int]) -> bool:
        points = [p1, p2, p3, p4]
        dists = []
        for i in range(4):
            for j in range(i + 1, 4):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dists.append(dx * dx + dy * dy)
        dists.sort()
        return dists[0] > 0 and dists[0] == dists[1] == dists[2] == dists[3] and dists[4] == dists[5] == 2 * dists[0]
# @lc code=end

"""
Interview explanation:
A square has six pairwise distances: four equal positive side lengths and two equal diagonals, each twice the squared side length. Squared distances avoid floating-point square roots.

Data structure: collect and sort the six distances.

Edge cases: duplicate points create zero side length and must be rejected. The check is orientation-independent, so no point ordering is required.

Complexity: constant time and space because there are always four points.
"""
