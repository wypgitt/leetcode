#
# @lc app=leetcode id=3873 lang=python3
#
# [3873] Maximum Points Activated with One Addition
#
# https://leetcode.com/problems/maximum-points-activated-with-one-addition/description/
#
# algorithms
# Hard (44.73%)
# Likes:    73
# Dislikes: 1
# Total Accepted:    8.4K
# Total Submissions: 18.7K
# Testcase Example:  "[[1,1],[1,2],[2,2]]"
#
#
# You are given a 2D integer array points, where points[i] = [x_i, y_i]
# represents the coordinates of the i^th point. All coordinates in points
# are distinct.
#
# If a point is activated, then all points that have the same x-coordinate
# or y-coordinate become activated as well.
#
# Activation continues until no additional points can be activated.
#
# You may add one additional point at any integer coordinate (x, y) not
# already present in points. Activation begins by activating this newly
# added point.
#
# Return an integer denoting the maximum number of points that can be
# activated, including the newly added point.
#
# Example 1:
#
# Input: points = [[1,1],[1,2],[2,2]]
#
# Output: 4
#
# Explanation:
#
# Adding and activating a point such as (1, 3) causes activations:
#
# (1, 3) shares x = 1 with (1, 1) and (1, 2) -> (1, 1) and (1, 2) become
# activated.
#
# (1, 2) shares y = 2 with (2, 2) -> (2, 2) becomes activated.
#
# Thus, the activated points are (1, 3), (1, 1), (1, 2), (2, 2), so 4
# points in total. We can show this is the maximum activated.
#
# Example 2:
#
# Input: points = [[2,2],[1,1],[3,3]]
#
# Output: 3
#
# Explanation:
#
# Adding and activating a point such as (1, 2) causes activations:
#
# (1, 2) shares x = 1 with (1, 1) -> (1, 1) becomes activated.
#
# (1, 2) shares y = 2 with (2, 2) -> (2, 2) becomes activated.
#
# Thus, the activated points are (1, 2), (1, 1), (2, 2), so 3 points in
# total. We can show this is the maximum activated.
#
# Example 3:
#
# Input: points = [[2,3],[2,2],[1,1],[4,5]]
#
# Output: 4
#
# Explanation:
#
# Adding and activating a point such as (2, 1) causes activations:
#
# (2, 1) shares x = 2 with (2, 3) and (2, 2) -> (2, 3) and (2, 2) become
# activated.
#
# (2, 1) shares y = 1 with (1, 1) -> (1, 1) becomes activated.
#
# Thus, the activated points are (2, 1), (2, 3), (2, 2), (1, 1), so 4
# points in total.
#
# Constraints:
#
# 1 <= points.length <= 10^5
#
# points[i] = [x_i, y_i]
#
# -10^9 <= x_i, y_i <= 10^9
#
# points contains all distinct coordinates.
#

# @lc code=start
from collections import Counter


class Solution:
    def maxActivated(self, points: list[list[int]]) -> int:
        """
        Interview explanation:
        Shared x/y coordinates chain-activate, so points form components. One
        new point can bridge at most two components.

        Algorithm:
        - Union points that share x or y (map coords → first index).
        - Take the two largest component sizes; answer = size1 + size2 + 1.

        Complexity: O(n α(n)) time, O(n) space.
        """
        n = len(points)
        parent = list(range(n))
        size = [1] * n

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int) -> None:
            ri, rj = find(i), find(j)
            if ri == rj:
                return
            if size[ri] < size[rj]:
                ri, rj = rj, ri
            parent[rj] = ri
            size[ri] += size[rj]

        x_first: dict[int, int] = {}
        y_first: dict[int, int] = {}
        for i, (x, y) in enumerate(points):
            if x in x_first:
                union(i, x_first[x])
            else:
                x_first[x] = i
            if y in y_first:
                union(i, y_first[y])
            else:
                y_first[y] = i

        mx1 = mx2 = 0
        for i in range(n):
            if find(i) == i:
                s = size[i]
                if s > mx1:
                    mx2, mx1 = mx1, s
                elif s > mx2:
                    mx2 = s
        return mx1 + mx2 + 1

    def maxActivated_coord_uf(self, points: list[list[int]]) -> int:
        """
        Interview explanation:
        Alternate: union x-nodes with offset y-nodes, then count points per root.

        Complexity: O(n α(n)) time, O(n) space.
        """
        parent: dict[int, int] = {}

        def find(x: int) -> int:
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(a: int, b: int) -> None:
            pa, pb = find(a), find(b)
            if pa != pb:
                parent[pa] = pb

        m = 3_000_000_000
        for x, y in points:
            union(x, y + m)
        cnt = Counter(find(x) for x, _ in points)
        vals = sorted(cnt.values(), reverse=True)
        return (vals[0] if vals else 0) + (vals[1] if len(vals) > 1 else 0) + 1
# @lc code=end
