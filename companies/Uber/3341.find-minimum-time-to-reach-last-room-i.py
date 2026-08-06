#
# @lc app=leetcode id=3341 lang=python3
#
# [3341] Find Minimum Time to Reach Last Room I
#
# https://leetcode.com/problems/find-minimum-time-to-reach-last-room-i/description/
#
# algorithms
# Medium (55.47%)
# Likes:    555
# Dislikes: 176
# Total Accepted:    118.5K
# Total Submissions: 213.5K
# Testcase Example:  "[[0,4],[4,4]]"
#
#
# There is a dungeon with n x m rooms arranged as a grid.
#
# You are given a 2D array moveTime of size n x m, where moveTime[i][j]
# represents the minimum time in seconds after which the room opens and
# can be moved to. You start from the room (0, 0) at time t = 0 and can
# move to an adjacent room. Moving between adjacent rooms takes exactly
# one second.
#
# Return the minimum time to reach the room (n - 1, m - 1).
#
# Two rooms are adjacent if they share a common wall, either horizontally
# or vertically.
#
# Example 1:
#
# Input: moveTime = [[0,4],[4,4]]
#
# Output: 6
#
# Explanation:
#
# The minimum time required is 6 seconds.
#
# At time t == 4, move from room (0, 0) to room (1, 0) in one second.
#
# At time t == 5, move from room (1, 0) to room (1, 1) in one second.
#
# Example 2:
#
# Input: moveTime = [[0,0,0],[0,0,0]]
#
# Output: 3
#
# Explanation:
#
# The minimum time required is 3 seconds.
#
# At time t == 0, move from room (0, 0) to room (1, 0) in one second.
#
# At time t == 1, move from room (1, 0) to room (1, 1) in one second.
#
# At time t == 2, move from room (1, 1) to room (1, 2) in one second.
#
# Example 3:
#
# Input: moveTime = [[0,1],[1,2]]
#
# Output: 3
#
# Constraints:
#
# 2 <= n == moveTime.length <= 50
#
# 2 <= m == moveTime[i].length <= 50
#
# 0 <= moveTime[i][j] <= 10^9
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def minTimeToReach(self, moveTime: List[List[int]]) -> int:
        """
        Interview explanation:
        Earliest arrival at (n-1,m-1). Moving to a room is allowed only after it
        opens; each move costs 1 second. Shortest path with waiting → Dijkstra.

        Algorithm:
        - dist[r][c] = min time to arrive at (r,c); start dist[0][0]=0.
        - Pop (t,r,c); for each neighbor, nt = max(t, moveTime[nr][nc]) + 1.
        - Relax if nt improves dist.

        Complexity: O(nm log(nm)) time, O(nm) space.
        """
        n, m = len(moveTime), len(moveTime[0])
        dist = [[10**18] * m for _ in range(n)]
        dist[0][0] = 0
        pq = [(0, 0, 0)]
        while pq:
            t, r, c = heapq.heappop(pq)
            if t != dist[r][c]:
                continue
            if r == n - 1 and c == m - 1:
                return t
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < n and 0 <= nc < m:
                    nt = max(t, moveTime[nr][nc]) + 1
                    if nt < dist[nr][nc]:
                        dist[nr][nc] = nt
                        heapq.heappush(pq, (nt, nr, nc))
        return -1
# @lc code=end
