#
# @lc app=leetcode id=3009 lang=python3
#
# [3009] Maximum Number of Intersections on the Chart
#
# https://leetcode.com/problems/maximum-number-of-intersections-on-the-chart/description/
#
# algorithms
# Hard (45.21%)
# Likes:    30
# Dislikes: 5
# Total Accepted:    4.4K
# Total Submissions: 9.8K
# Testcase Example:  "[1,2,1,2,1,3,2]"
#
#
# There is a line chart consisting of n points connected by line segments.
# You are given a 1-indexed integer array y. The k^th point has
# coordinates (k, y[k]). There are no horizontal lines; that is, no two
# consecutive points have the same y-coordinate.
#
# We can draw an infinitely long horizontal line. Return the maximum
# number of points of intersection of the line with the chart.
#
# Example 1:
#
# Input: y = [1,2,1,2,1,3,2]
# Output: 5
# Explanation: As you can see in the image above, the line y = 1.5 has 5
# intersections with the chart (in red crosses). You can also see the line
# y = 2 which intersects the chart in 4 points (in red crosses). It can be
# shown that there is no horizontal line intersecting the chart at more
# than 5 points. So the answer would be 5.
#
# Example 2:
#
# Input: y = [2,1,3,4,5]
# Output: 2
# Explanation: As you can see in the image above, the line y = 1.5 has 2
# intersections with the chart (in red crosses). You can also see the line
# y = 2 which intersects the chart in 2 points (in red crosses). It can be
# shown that there is no horizontal line intersecting the chart at more
# than 2 points. So the answer would be 2.
#
# Constraints:
#
# 2 <= y.length <= 10^5
#
# 1 <= y[i] <= 10^9
#
# y[i] != y[i + 1] for i in range [1, n - 1]
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def maxIntersectionCount(self, y: List[int]) -> int:
        """
        Interview explanation:
        Draw a horizontal line maximizing intersections with the polyline.
        Work in doubled coordinates so integer and half-integer heights share one
        sweep; each segment contributes an inclusive vertical range with careful
        endpoint handling so shared vertices are not double-counted.

        Algorithm:
        - For segment y[i] -> y[i+1], map to [2*y[i], 2*y[i+1] (+/-1)] so interior
          vertices are half-open except the final segment which includes its end.
        - Difference array / Counter events: +1 at lo, -1 at hi+1.
        - Sweep sorted keys; track running coverage; answer is the maximum.

        Complexity: O(n log n) time, O(n) space.
        """
        line: Counter = Counter()
        n = len(y)
        for i in range(n - 1):
            start = 2 * y[i]
            end = 2 * y[i + 1] + (0 if i == n - 2 else (-1 if y[i + 1] > y[i] else 1))
            lo, hi = min(start, end), max(start, end)
            line[lo] += 1
            line[hi + 1] -= 1

        ans = cur = 0
        for pos in sorted(line):
            cur += line[pos]
            ans = max(ans, cur)
        return ans
# @lc code=end
