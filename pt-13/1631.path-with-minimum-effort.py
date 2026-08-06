#
# @lc app=leetcode id=1631 lang=python3
#
# [1631] Path With Minimum Effort
#
# https://leetcode.com/problems/path-with-minimum-effort/description/
#
# algorithms
# Medium (63.81%)
# Likes:    6987
# Dislikes: 243
# Total Accepted:    506K
# Total Submissions: 793K
# Testcase Example:  "[[1,2,2],[3,8,2],[5,3,5]]"
#
# You are a hiker preparing for an upcoming hike. You are given heights, a 2D
# array of size rows x columns, where heights[row][col] represents the height
# of cell (row, col). You are situated in the top-left cell, (0, 0), and you
# hope to travel to the bottom-right cell, (rows-1, columns-1) (i.e.,
# 0-indexed). You can move up, down, left, or right, and you wish to find a
# route that requires the minimum effort.
#
# A route's effort is the maximum absolute difference in heights between two
# consecutive cells of the route.
#
# Return the minimum effort required to travel from the top-left cell to the
# bottom-right cell.
#
# Example 1:
#
# Input: heights = [[1,2,2],[3,8,2],[5,3,5]]
# Output: 2
# Explanation: The route of [1,3,5,3,5] has a maximum absolute difference of 2
# in consecutive cells.
# This is better than the route of [1,2,2,2,5], where the maximum absolute
# difference is 3.
#
# Example 2:
#
# Input: heights = [[1,2,3],[3,8,4],[5,3,5]]
# Output: 1
# Explanation: The route of [1,2,3,4,5] has a maximum absolute difference of 1
# in consecutive cells, which is better than route [1,3,5,3,5].
#
# Example 3:
#
# Input: heights =
# [[1,2,1,1,1],[1,2,1,2,1],[1,2,1,2,1],[1,2,1,2,1],[1,1,1,2,1]]
# Output: 0
# Explanation: This route does not require any effort.
#
# Constraints:
#
# rows == heights.length
#
# columns == heights[i].length
#
# 1 <= rows, columns <= 100
#
# 1 <= heights[i][j] <= 10^6
#

# @lc code=start
from typing import List
import heapq
from collections import deque


class Solution:
    def minimumEffortPath(self, heights: List[List[int]]) -> int:
        """
        Interview explanation:
        Effort = max absolute height diff along path. Minimize effort from (0,0)
        to (m-1,n-1). Dijkstra on effort is classic.

        Algorithm (Dijkstra):
        - dist[r][c]=min effort to reach; pq by effort; relax neighbors with
          max(curr_effort, |h diff|).

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(heights), len(heights[0])
        dist = [[10**18] * n for _ in range(m)]
        dist[0][0] = 0
        pq = [(0, 0, 0)]
        while pq:
            d, r, c = heapq.heappop(pq)
            if (r, c) == (m - 1, n - 1):
                return d
            if d > dist[r][c]:
                continue
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < m and 0 <= nc < n:
                    nd = max(d, abs(heights[nr][nc] - heights[r][c]))
                    if nd < dist[nr][nc]:
                        dist[nr][nc] = nd
                        heapq.heappush(pq, (nd, nr, nc))
        return 0

    def minimumEffortPath_binary_search(self, heights: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: binary search effort X; BFS/DFS if path exists with all
        edge diffs <= X.

        Algorithm (binary search + BFS):
        - lo=0, hi=1e6; mid check connectivity under threshold mid.

        Complexity: O(mn log H) time, O(mn) space.
        """
        m, n = len(heights), len(heights[0])

        def ok(mid: int) -> bool:
            seen = [[False] * n for _ in range(m)]
            q = deque([(0, 0)])
            seen[0][0] = True
            while q:
                r, c = q.popleft()
                if (r, c) == (m - 1, n - 1):
                    return True
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc]:
                        if abs(heights[nr][nc] - heights[r][c]) <= mid:
                            seen[nr][nc] = True
                            q.append((nr, nc))
            return False

        lo, hi = 0, 10**6
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
