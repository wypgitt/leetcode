#
# @lc app=leetcode id=3342 lang=python3
#
# [3342] Find Minimum Time to Reach Last Room II
#
# https://leetcode.com/problems/find-minimum-time-to-reach-last-room-ii/description/
#
# algorithms
# Medium (67.60%)
# Likes:    374
# Dislikes: 57
# Total Accepted:    98K
# Total Submissions: 145K
# Testcase Example:  "[[0,4],[4,4]]"
#
#
# There is a dungeon with n x m rooms arranged as a grid.
#
# You are given a 2D array moveTime of size n x m, where moveTime[i][j]
# represents the minimum time in seconds when you can start moving to that
# room. You start from the room (0, 0) at time t = 0 and can move to an
# adjacent room. Moving between adjacent rooms takes one second for one
# move and two seconds for the next, alternating between the two.
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
# Output: 7
#
# Explanation:
#
# The minimum time required is 7 seconds.
#
# At time t == 4, move from room (0, 0) to room (1, 0) in one second.
#
# At time t == 5, move from room (1, 0) to room (1, 1) in two seconds.
#
# Example 2:
#
# Input: moveTime = [[0,0,0,0],[0,0,0,0]]
#
# Output: 6
#
# Explanation:
#
# The minimum time required is 6 seconds.
#
# At time t == 0, move from room (0, 0) to room (1, 0) in one second.
#
# At time t == 1, move from room (1, 0) to room (1, 1) in two seconds.
#
# At time t == 3, move from room (1, 1) to room (1, 2) in one second.
#
# At time t == 4, move from room (1, 2) to room (1, 3) in two seconds.
#
# Example 3:
#
# Input: moveTime = [[0,1],[1,2]]
#
# Output: 4
#
# Constraints:
#
# 2 <= n == moveTime.length <= 750
#
# 2 <= m == moveTime[i].length <= 750
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
        Same dungeon as I, but move costs alternate 1,2,1,2,... So state needs
        move-parity; Dijkstra on (r,c,parity).

        Algorithm:
        - dist[r][c][p] = min arrival with p = (#moves so far) mod 2.
        - Next move cost is 1 if p==0 else 2; arrive max(t, open) + cost.

        Complexity: O(nm log(nm)) time, O(nm) space.
        """
        n, m = len(moveTime), len(moveTime[0])
        dist = [[[10**18, 10**18] for _ in range(m)] for _ in range(n)]
        dist[0][0][0] = 0
        pq = [(0, 0, 0, 0)]  # time, r, c, parity
        while pq:
            t, r, c, p = heapq.heappop(pq)
            if t != dist[r][c][p]:
                continue
            if r == n - 1 and c == m - 1:
                return t
            cost = 1 if p == 0 else 2
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < n and 0 <= nc < m:
                    nt = max(t, moveTime[nr][nc]) + cost
                    np = 1 - p
                    if nt < dist[nr][nc][np]:
                        dist[nr][nc][np] = nt
                        heapq.heappush(pq, (nt, nr, nc, np))
        return -1
# @lc code=end
