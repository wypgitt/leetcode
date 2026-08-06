#
# @lc app=leetcode id=675 lang=python3
#
# [675] Cut Off Trees for Golf Event
#
# https://leetcode.com/problems/cut-off-trees-for-golf-event/description/
#
# algorithms
# Hard (36.7%)
# Likes:    1304
# Dislikes: 691
# Total Accepted:    87.2K
# Total Submissions: 238K
# Testcase Example:  "[[1,2,3],[0,0,4],[7,6,5]]"
#
# You are asked to cut off all the trees in a forest for a golf event. The
# forest is represented as an m x n matrix. In this matrix:
#
# 0 means the cell cannot be walked through.
#
# 1 represents an empty cell that can be walked through.
#
# A number greater than 1 represents a tree in a cell that can be walked
# through, and this number is the tree's height.
#
# In one step, you can walk in any of the four directions: north, east, south,
# and west. If you are standing in a cell with a tree, you can choose whether
# to cut it off.
#
# You must cut off the trees in order from shortest to tallest. When you cut
# off a tree, the value at its cell becomes 1 (an empty cell).
#
# Starting from the point (0, 0), return the minimum steps you need to walk to
# cut off all the trees. If you cannot cut off all the trees, return -1.
#
# Note: The input is generated such that no two trees have the same height, and
# there is at least one tree needs to be cut off.
#
# Example 1:
#
# Input: forest = [[1,2,3],[0,0,4],[7,6,5]]
# Output: 6
# Explanation: Following the path above allows you to cut off the trees from
# shortest to tallest in 6 steps.
#
# Example 2:
#
# Input: forest = [[1,2,3],[0,0,0],[7,6,5]]
# Output: -1
# Explanation: The trees in the bottom row cannot be accessed as the middle row
# is blocked.
#
# Example 3:
#
# Input: forest = [[2,3,4],[0,0,5],[8,7,6]]
# Output: 6
# Explanation: You can follow the same path as Example 1 to cut off all the
# trees.
# Note that you can cut off the first tree at (0, 0) before making any steps.
#
# Constraints:
#
# m == forest.length
#
# n == forest[i].length
#
# 1 <= m, n <= 50
#
# 0 <= forest[i][j] <= 10^9
#
# Heights of all trees are distinct.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def cutOffTree(self, forest: List[List[int]]) -> int:
        """
        Interview explanation:
        Must cut trees in increasing height order, walking from (0,0) between
        cuts. Each walk is a shortest path on the grid (0 = blocked). Sum BFS
        distances between consecutive targets; return -1 if unreachable.

        Algorithm:
        - Collect (height, r, c) for cells > 1; sort by height.
        - From (0,0), for each tree: BFS to target; accumulate steps.
        - BFS: 4-dir, skip 0 / OOB / visited.

        Complexity: O(t * m * n) time (t trees), O(m*n) space per BFS.
        """
        m, n = len(forest), len(forest[0])
        trees = sorted(
            (forest[i][j], i, j)
            for i in range(m)
            for j in range(n)
            if forest[i][j] > 1
        )

        def bfs(sr: int, sc: int, tr: int, tc: int) -> int:
            if sr == tr and sc == tc:
                return 0
            q = deque([(sr, sc, 0)])
            seen = {(sr, sc)}
            while q:
                r, c, d = q.popleft()
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen and forest[nr][nc]:
                        if nr == tr and nc == tc:
                            return d + 1
                        seen.add((nr, nc))
                        q.append((nr, nc, d + 1))
            return -1

        ans = 0
        cr = cc = 0
        for _, tr, tc in trees:
            dist = bfs(cr, cc, tr, tc)
            if dist < 0:
                return -1
            ans += dist
            cr, cc = tr, tc
        return ans
# @lc code=end
