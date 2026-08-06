#
# @lc app=leetcode id=2503 lang=python3
#
# [2503] Maximum Number of Points From Grid Queries
#
# https://leetcode.com/problems/maximum-number-of-points-from-grid-queries/description/
#
# algorithms
# Hard (59.24%)
# Likes:    1114
# Dislikes: 51
# Total Accepted:    99.6K
# Total Submissions: 168.1K
# Testcase Example:  "[[1,2,3],[2,5,7],[3,5,1]]\n[5,6,2]"
#
# You are given an m x n integer matrix grid and an array queries of size k.
#
# Find an array answer of size k such that for each integer queries[i] you start
# in the top left cell of the matrix and repeat the following process:
#
#
# If queries[i] is strictly greater than the value of the current cell that you
# are in, then you get one point if it is your first time visiting this cell,
# and you can move to any adjacent cell in all 4 directions: up, down, left, and
# right.
#
#
# Otherwise, you do not get any points, and you end this process.
#
# After the process, answer[i] is the maximum number of points you can get. Note
# that for each query you are allowed to visit the same cell multiple times.
#
# Return the resulting array answer.
#
#
#
# Example 1:
#
# Input: grid = [[1,2,3],[2,5,7],[3,5,1]], queries = [5,6,2]
# Output: [5,8,1]
# Explanation: The diagrams above show which cells we visit to get points for
# each query.
#
# Example 2:
#
# Input: grid = [[5,2,1],[1,1,2]], queries = [3]
# Output: [0]
# Explanation: We can not get any points because the value of the top left cell
# is already greater than or equal to 3.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 2 <= m, n <= 1000
#
#
# 4 <= m * n <= 10^5
#
#
# k == queries.length
#
#
# 1 <= k <= 10^4
#
#
# 1 <= grid[i][j], queries[i] <= 10^6
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maxPoints(self, grid: List[List[int]], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        For each query q, max cells reachable from (0,0) via 4-dir moves where
        every visited cell value is strictly < q (points = distinct cells).

        Algorithm:
        - Sort queries ascending; grow a min-heap BFS frontier of reachable cells
          ordered by value; while heap top < q, pop and expand neighbors. Answers
          are monotonic so process queries in order and map back by index.

        Complexity: O(mn log(mn) + k log k) time, O(mn + k) space.
        """
        m, n = len(grid), len(grid[0])
        ordered = sorted(enumerate(queries), key=lambda x: x[1])
        ans = [0] * len(queries)
        heap = [(grid[0][0], 0, 0)]
        seen = {(0, 0)}
        points = 0
        dirs = ((0, 1), (1, 0), (0, -1), (-1, 0))
        for idx, q in ordered:
            while heap and heap[0][0] < q:
                _, r, c = heapq.heappop(heap)
                points += 1
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        heapq.heappush(heap, (grid[nr][nc], nr, nc))
            ans[idx] = points
        return ans
# @lc code=end
