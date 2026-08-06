#
# @lc app=leetcode id=417 lang=python3
#
# [417] Pacific Atlantic Water Flow
#
# https://leetcode.com/problems/pacific-atlantic-water-flow/description/
#
# algorithms
# Medium (61.3%)
# Likes:    8835
# Dislikes: 1857
# Total Accepted:    845K
# Total Submissions: 1.4M
# Testcase Example:  "[[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]"
#
# There is an m x n rectangular island that borders both the Pacific Ocean and
# Atlantic Ocean. The Pacific Ocean touches the island's left and top edges,
# and the Atlantic Ocean touches the island's right and bottom edges.
#
# The island is partitioned into a grid of square cells. You are given an m x n
# integer matrix heights where heights[r][c] represents the height above sea
# level of the cell at coordinate (r, c).
#
# The island receives a lot of rain, and the rain water can flow to neighboring
# cells directly north, south, east, and west if the neighboring cell's height
# is less than or equal to the current cell's height. Water can flow from any
# cell adjacent to an ocean into the ocean.
#
# Return a 2D list of grid coordinates result where result[i] = [r_i, c_i]
# denotes that rain water can flow from cell (r_i, c_i) to both the Pacific and
# Atlantic oceans.
#
# Example 1:
#
# Input: heights =
# [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]
# Output: [[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]
# Explanation: The following cells can flow to the Pacific and Atlantic oceans,
# as shown below:
# [0,4]: [0,4] -> Pacific Ocean
# [0,4] -> Atlantic Ocean
# [1,3]: [1,3] -> [0,3] -> Pacific Ocean
# [1,3] -> [1,4] -> Atlantic Ocean
# [1,4]: [1,4] -> [1,3] -> [0,3] -> Pacific Ocean
# [1,4] -> Atlantic Ocean
# [2,2]: [2,2] -> [1,2] -> [0,2] -> Pacific Ocean
# [2,2] -> [2,3] -> [2,4] -> Atlantic Ocean
# [3,0]: [3,0] -> Pacific Ocean
# [3,0] -> [4,0] -> Atlantic Ocean
# [3,1]: [3,1] -> [3,0] -> Pacific Ocean
# [3,1] -> [4,1] -> Atlantic Ocean
# [4,0]: [4,0] -> Pacific Ocean
# [4,0] -> Atlantic Ocean
# Note that there are other possible paths for these cells to flow to the
# Pacific and Atlantic oceans.
#
# Example 2:
#
# Input: heights = [[1]]
# Output: [[0,0]]
# Explanation: The water can flow from the only cell to the Pacific and
# Atlantic oceans.
#
# Constraints:
#
# m == heights.length
#
# n == heights[r].length
#
# 1 <= m, n <= 200
#
# 0 <= heights[r][c] <= 10^5
#

# @lc code=start

from collections import deque
from typing import List, Set, Tuple


class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Multi-source DFS from both oceans inland (uphill / non-decreasing).
        Cells reachable from both Pacific and Atlantic are the answer.

        Algorithm:
        - DFS/BFS from Pacific borders and Atlantic borders into cells with
          height >= current.
        - Return intersection of the two reachable sets.

        Complexity: O(mn) time and space.
        """
        if not heights or not heights[0]:
            return []
        m, n = len(heights), len(heights[0])
        pacific: Set[Tuple[int, int]] = set()
        atlantic: Set[Tuple[int, int]] = set()

        def dfs(r: int, c: int, seen: Set[Tuple[int, int]]) -> None:
            seen.add((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < m
                    and 0 <= nc < n
                    and (nr, nc) not in seen
                    and heights[nr][nc] >= heights[r][c]
                ):
                    dfs(nr, nc, seen)

        for i in range(m):
            dfs(i, 0, pacific)
            dfs(i, n - 1, atlantic)
        for j in range(n):
            dfs(0, j, pacific)
            dfs(m - 1, j, atlantic)

        return [[r, c] for r, c in pacific & atlantic]

    def pacificAtlanticBFS(self, heights: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate multi-source BFS from both ocean borders with the same
        non-decreasing height rule; intersect reachable sets.

        Algorithm:
        - Seed queues with Pacific / Atlantic borders; BFS inland.
        - Return cells in both visited sets.

        Complexity: O(mn) time and space.
        """
        if not heights or not heights[0]:
            return []
        m, n = len(heights), len(heights[0])

        def bfs(starts: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
            q = deque(starts)
            seen = set(starts)
            while q:
                r, c = q.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < m
                        and 0 <= nc < n
                        and (nr, nc) not in seen
                        and heights[nr][nc] >= heights[r][c]
                    ):
                        seen.add((nr, nc))
                        q.append((nr, nc))
            return seen

        pac_starts = [(i, 0) for i in range(m)] + [(0, j) for j in range(1, n)]
        atl_starts = [(i, n - 1) for i in range(m)] + [(m - 1, j) for j in range(n - 1)]
        return [[r, c] for r, c in bfs(pac_starts) & bfs(atl_starts)]
# @lc code=end
