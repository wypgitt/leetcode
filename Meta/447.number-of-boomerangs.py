#
# @lc app=leetcode id=447 lang=python3
#
# [447] Number of Boomerangs
#
# https://leetcode.com/problems/number-of-boomerangs/description/
#
# algorithms
# Medium (57.88%)
# Likes:    905
# Dislikes: 1047
# Total Accepted:    122K
# Total Submissions: 211K
# Testcase Example:  "[[0,0],[1,0],[2,0]]"
#
# You are given n points in the plane that are all distinct, where points[i] =
# [x_i, y_i]. A boomerang is a tuple of points (i, j, k) such that the distance
# between i and j equals the distance between i and k (the order of the tuple
# matters).
#
# Return the number of boomerangs.
#
# Example 1:
#
# Input: points = [[0,0],[1,0],[2,0]]
# Output: 2
# Explanation: The two boomerangs are [[1,0],[0,0],[2,0]] and
# [[1,0],[2,0],[0,0]].
#
# Example 2:
#
# Input: points = [[1,1],[2,2],[3,3]]
# Output: 2
#
# Example 3:
#
# Input: points = [[1,1]]
# Output: 0
#
# Constraints:
#
# n == points.length
#
# 1 <= n <= 500
#
# points[i].length == 2
#
# -10^4 <= x_i, y_i <= 10^4
#
# All the points are unique.
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def numberOfBoomerangs(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        For each point i as the middle of a boomerang, group other points by
        squared distance. For a distance with c points, permutations P(c,2)=c*(c-1)
        form boomerangs.

        Algorithm:
        - For each i: count distances to all j!=i; ans += c*(c-1) for each bucket.

        Complexity: O(n^2) time, O(n) space per center.
        """
        ans = 0
        for i, (x1, y1) in enumerate(points):
            dist = defaultdict(int)
            for j, (x2, y2) in enumerate(points):
                if i == j:
                    continue
                d = (x1 - x2) ** 2 + (y1 - y2) ** 2
                dist[d] += 1
            for c in dist.values():
                ans += c * (c - 1)
        return ans
# @lc code=end
