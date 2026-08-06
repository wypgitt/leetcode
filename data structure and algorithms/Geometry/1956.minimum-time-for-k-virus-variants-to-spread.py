#
# @lc app=leetcode id=1956 lang=python3
#
# [1956] Minimum Time For K Virus Variants to Spread
#
# https://leetcode.com/problems/minimum-time-for-k-virus-variants-to-spread/description/
#
# algorithms
# Hard (50.63%)
# Likes:    32
# Dislikes: 7
# Total Accepted:    1.4K
# Total Submissions: 2.8K
# Testcase Example:  "[[1,1],[6,1]]\n2"
#
#
# There are n unique virus variants in an infinite 2D grid. You are given
# a 2D array points, where points[i] = [x_i, y_i] represents a virus
# originating at (x_i, y_i) on day 0. Note that it is possible for
# multiple virus variants to originate at the same point.
#
# Every day, each cell infected with a virus variant will spread the virus
# to all neighboring points in the four cardinal directions (i.e. up,
# down, left, and right). If a cell has multiple variants, all the
# variants will spread without interfering with each other.
#
# Given an integer k, return the minimum integer number of days for any
# point to contain at least k of the unique virus variants.
#
# Example 1:
#
# Input: points = [[1,1],[6,1]], k = 2
# Output: 3
# Explanation: On day 3, points (3,1) and (4,1) will contain both virus
# variants. Note that these are not the only points that will contain both
# virus variants.
#
# Example 2:
#
# Input: points = [[3,3],[1,2],[9,2]], k = 2
# Output: 2
# Explanation: On day 2, points (1,3), (2,3), (2,2), and (3,2) will
# contain the first two viruses. Note that these are not the only points
# that will contain both virus variants.
#
# Example 3:
#
# Input: points = [[3,3],[1,2],[9,2]], k = 3
# Output: 4
# Explanation: On day 4, the point (5,2) will contain all 3 viruses. Note
# that this is not the only point that will contain all 3 virus variants.
#
# Constraints:
#
# n == points.length
#
# 2 <= n <= 50
#
# points[i].length == 2
#
# 1 <= x_i, y_i <= 100
#
# 2 <= k <= n
#
# @lc code=start
from typing import List


class Solution:
    def minDayskVariants(self, points: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Premium Hard. Viruses spread Manhattan diamonds. Min time t so some
        point is covered by >= k viruses. Rotate (x,y)->(x+y,x-y) to Chebyshev
        squares; binary search t with interval-sweep coverage check.

        Algorithm:
        - Binary search t.
        - Check: for each candidate vertical boundary x0 of a square, collect
          y-intervals of squares covering x0; sweep max overlap >= k.

        Complexity: O(log W * n^2 log n) time, O(n) space.
        """
        pts = [(x + y, x - y) for x, y in points]

        def ok(t: int) -> bool:
            xs = sorted({x - t for x, _ in pts} | {x + t for x, _ in pts})
            for px in xs:
                events = []
                for x, y in pts:
                    if abs(x - px) <= t:
                        events.append((y - t, 1))
                        events.append((y + t + 1, -1))
                events.sort()
                cur = 0
                for _, d in events:
                    cur += d
                    if cur >= k:
                        return True
            return False

        lo, hi = 0, 2 * 10**9
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def minDayskVariants_corners(self, points: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate check: evaluate coverage at square-corner candidates formed
        from pairs of boundary coordinates.

        Algorithm:
        - Same binary search; for each (px,py) from boundary products, count
          viruses covering that point.

        Complexity: O(log W * n^3) time, O(n) space.
        """
        pts = [(x + y, x - y) for x, y in points]

        def covered(px: int, py: int, t: int) -> int:
            return sum(1 for x, y in pts if abs(x - px) <= t and abs(y - py) <= t)

        def ok(t: int) -> bool:
            xs = sorted({x - t for x, _ in pts} | {x + t for x, _ in pts})
            ys = sorted({y - t for _, y in pts} | {y + t for _, y in pts})
            for px in xs:
                for py in ys:
                    if covered(px, py, t) >= k:
                        return True
            return False

        lo, hi = 0, 2 * 10**9
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end

