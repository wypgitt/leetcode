#
# @lc app=leetcode id=3102 lang=python3
#
# [3102] Minimize Manhattan Distances
#
# https://leetcode.com/problems/minimize-manhattan-distances/description/
#
# algorithms
# Hard (32.74%)
# Likes:    188
# Dislikes: 15
# Total Accepted:    11.1K
# Total Submissions: 33.8K
# Testcase Example:  "[[3,10],[5,15],[10,2],[4,4]]"
#
#
# You are given an array points representing integer coordinates of some
# points on a 2D plane, where points[i] = [x_i, y_i].
#
# The distance between two points is defined as their Manhattan distance.
#
# Return the minimum possible value for maximum distance between any two
# points by removing exactly one point.
#
# Example 1:
#
# Input: points = [[3,10],[5,15],[10,2],[4,4]]
#
# Output: 12
#
# Explanation:
#
# The maximum distance after removing each point is the following:
#
# After removing the 0^th point the maximum distance is between points (5,
# 15) and (10, 2), which is |5 - 10| + |15 - 2| = 18.
#
# After removing the 1^st point the maximum distance is between points (3,
# 10) and (10, 2), which is |3 - 10| + |10 - 2| = 15.
#
# After removing the 2^nd point the maximum distance is between points (5,
# 15) and (4, 4), which is |5 - 4| + |15 - 4| = 12.
#
# After removing the 3^rd point the maximum distance is between points (5,
# 15) and (10, 2), which is |5 - 10| + |15 - 2| = 18.
#
# 12 is the minimum possible maximum distance between any two points after
# removing exactly one point.
#
# Example 2:
#
# Input: points = [[1,1],[1,1],[1,1]]
#
# Output: 0
#
# Explanation:
#
# Removing any of the points results in the maximum distance between any
# two points of 0.
#
# Constraints:
#
# 3 <= points.length <= 10^5
#
# points[i].length == 2
#
# 1 <= points[i][0], points[i][1] <= 10^8
#

# @lc code=start
from typing import List


class Solution:
    def minimumDistance(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Max Manhattan among points equals max of ranges of (x+y) and (x-y).
        Remove exactly one point to minimize that diameter.

        Algorithm:
        - Only extremes of x+y / x-y can shrink the diameter; try removing each.
        - After a candidate removal, diameter = max(max_sum-min_sum, max_diff-min_diff).

        Complexity: O(n) time, O(1) space.
        """
        def diameter(exclude: int) -> int:
            max_sum = max_diff = float("-inf")
            min_sum = min_diff = float("inf")
            for i, (x, y) in enumerate(points):
                if i == exclude:
                    continue
                max_sum = max(max_sum, x + y)
                min_sum = min(min_sum, x + y)
                max_diff = max(max_diff, x - y)
                min_diff = min(min_diff, x - y)
            return max(max_sum - min_sum, max_diff - min_diff)

        max_sum_i = min_sum_i = max_diff_i = min_diff_i = 0
        for i, (x, y) in enumerate(points):
            if x + y > points[max_sum_i][0] + points[max_sum_i][1]:
                max_sum_i = i
            if x + y < points[min_sum_i][0] + points[min_sum_i][1]:
                min_sum_i = i
            if x - y > points[max_diff_i][0] - points[max_diff_i][1]:
                max_diff_i = i
            if x - y < points[min_diff_i][0] - points[min_diff_i][1]:
                min_diff_i = i
        return min(
            diameter(i)
            for i in {max_sum_i, min_sum_i, max_diff_i, min_diff_i}
        )
# @lc code=end
