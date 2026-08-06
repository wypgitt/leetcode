#
# @lc app=leetcode id=3454 lang=python3
#
# [3454] Separate Squares II
#
# https://leetcode.com/problems/separate-squares-ii/description/
#
# algorithms
# Hard (59.23%)
# Likes:    277
# Dislikes: 66
# Total Accepted:    61.5K
# Total Submissions: 103.9K
# Testcase Example:  "[[0,0,1],[2,2,1]]"
#
#
# You are given a 2D integer array squares. Each squares[i] = [x_i, y_i,
# l_i] represents the coordinates of the bottom-left point and the side
# length of a square parallel to the x-axis.
#
# Find the minimum y-coordinate value of a horizontal line such that the
# total area covered by squares above the line equals the total area
# covered by squares below the line.
#
# Answers within 10^-5 of the actual answer will be accepted.
#
# Note: Squares may overlap. Overlapping areas should be counted only once
# in this version.
#
# Example 1:
#
# Input: squares = [[0,0,1],[2,2,1]]
#
# Output: 1.00000
#
# Explanation:
#
# Any horizontal line between y = 1 and y = 2 results in an equal split,
# with 1 square unit above and 1 square unit below. The minimum y-value is
# 1.
#
# Example 2:
#
# Input: squares = [[0,0,2],[1,1,1]]
#
# Output: 1.00000
#
# Explanation:
#
# Since the blue square overlaps with the red square, it will not be
# counted again. Thus, the line y = 1 splits the squares into two equal
# parts.
#
# Constraints:
#
# 1 <= squares.length <= 5 * 10^4
#
# squares[i] = [x_i, y_i, l_i]
#
# squares[i].length == 3
#
# 0 <= x_i, y_i <= 10^9
#
# 1 <= l_i <= 10^9
#
# The total area of all the squares will not exceed 10^15.
#

# @lc code=start

from typing import List


class _Node:
    __slots__ = ("l", "r", "cnt", "length")

    def __init__(self) -> None:
        self.l = self.r = 0
        self.cnt = self.length = 0


class _SegmentTree:
    def __init__(self, nums: List[int]) -> None:
        n = len(nums) - 1
        self.nums = nums
        self.tr = [_Node() for _ in range(n << 2)]
        self._build(1, 0, n - 1)

    def _build(self, u: int, l: int, r: int) -> None:
        self.tr[u].l, self.tr[u].r = l, r
        if l != r:
            mid = (l + r) >> 1
            self._build(u << 1, l, mid)
            self._build(u << 1 | 1, mid + 1, r)

    def modify(self, u: int, l: int, r: int, k: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        if l > r:
            return
        if self.tr[u].l >= l and self.tr[u].r <= r:
            self.tr[u].cnt += k
        else:
            mid = (self.tr[u].l + self.tr[u].r) >> 1
            if l <= mid:
                self.modify(u << 1, l, r, k)
            if r > mid:
                self.modify(u << 1 | 1, l, r, k)
        self._pushup(u)

    def _pushup(self, u: int) -> None:
        if self.tr[u].cnt:
            self.tr[u].length = self.nums[self.tr[u].r + 1] - self.nums[self.tr[u].l]
        elif self.tr[u].l == self.tr[u].r:
            self.tr[u].length = 0
        else:
            self.tr[u].length = self.tr[u << 1].length + self.tr[u << 1 | 1].length

    @property
    def length(self) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        return self.tr[1].length


class Solution:
    def separateSquares(self, squares: List[List[int]]) -> float:
        """
        Interview explanation:
        Same half-area horizontal cut as Separate Squares I, but overlapping area
        counts once — need the geometric union.

        Algorithm:
        - Sweep y-events (bottom +1 / top -1). Segment tree on compressed x keeps
          covered union width; accumulate strip areas for total, then resweep to
          interpolate the y where cumulative union area hits half.

        Complexity: O(n log n) time and space.
        """
        xs: set[int] = set()
        segs: list[tuple[int, int, int, int]] = []
        for x1, y1, L in squares:
            x2, y2 = x1 + L, y1 + L
            xs.update((x1, x2))
            segs.append((y1, x1, x2, 1))
            segs.append((y2, x1, x2, -1))
        segs.sort()
        st = sorted(xs)
        tree = _SegmentTree(st)
        d = {x: i for i, x in enumerate(st)}

        area = 0.0
        y0 = 0
        for y, x1, x2, k in segs:
            area += (y - y0) * tree.length
            tree.modify(1, d[x1], d[x2] - 1, k)
            y0 = y

        target = area / 2.0
        area = 0.0
        y0 = 0
        for y, x1, x2, k in segs:
            width = tree.length
            t = (y - y0) * width
            if width and area + t >= target:
                return y0 + (target - area) / width
            area += t
            tree.modify(1, d[x1], d[x2] - 1, k)
            y0 = y
        return 0.0
# @lc code=end

