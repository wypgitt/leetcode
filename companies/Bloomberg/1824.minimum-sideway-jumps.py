#
# @lc app=leetcode id=1824 lang=python3
#
# [1824] Minimum Sideway Jumps
#
# https://leetcode.com/problems/minimum-sideway-jumps/description/
#
# algorithms
# Medium (51.88%)
# Likes:    1290
# Dislikes: 51
# Total Accepted:    61.1K
# Total Submissions: 118K
# Testcase Example:  "[0,1,2,3,0]"
#
# There is a 3 lane road of length n that consists of n + 1 points labeled from
# 0 to n. A frog starts at point 0 in the second lane and wants to jump to
# point n. However, there could be obstacles along the way.
#
# You are given an array obstacles of length n + 1 where each obstacles[i]
# (ranging from 0 to 3) describes an obstacle on the lane obstacles[i] at point
# i. If obstacles[i] == 0, there are no obstacles at point i. There will be at
# most one obstacle in the 3 lanes at each point.
#
# For example, if obstacles[2] == 1, then there is an obstacle on lane 1 at
# point 2.
#
# The frog can only travel from point i to point i + 1 on the same lane if
# there is not an obstacle on the lane at point i + 1. To avoid obstacles, the
# frog can also perform a side jump to jump to another lane (even if they are
# not adjacent) at the same point if there is no obstacle on the new lane.
#
# For example, the frog can jump from lane 3 at point 3 to lane 1 at point 3.
#
# Return the minimum number of side jumps the frog needs to reach any lane at
# point n starting from lane 2 at point 0.
#
# Note: There will be no obstacles on points 0 and n.
#
# Example 1:
#
# Input: obstacles = [0,1,2,3,0]
# Output: 2
# Explanation: The optimal solution is shown by the arrows above. There are 2
# side jumps (red arrows).
# Note that the frog can jump over obstacles only when making side jumps (as
# shown at point 2).
#
# Example 2:
#
# Input: obstacles = [0,1,1,3,3,0]
# Output: 0
# Explanation: There are no obstacles on lane 2. No side jumps are required.
#
# Example 3:
#
# Input: obstacles = [0,2,1,0,3,0]
# Output: 2
# Explanation: The optimal solution is shown by the arrows above. There are 2
# side jumps.
#
# Constraints:
#
# obstacles.length == n + 1
#
# 1 <= n <= 5 * 10^5
#
# 0 <= obstacles[i] <= 3
#
# obstacles[0] == obstacles[n] == 0
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minSideJumps(self, obstacles: List[int]) -> int:
        """
        Interview explanation:
        3 lanes; start lane 2; forward free; side jump costs 1. Min jumps to end.

        Algorithm (DP):
        - dp[3] min jumps at current point; INF on obstacle; relax side jumps.

        Complexity: O(n) time, O(1) space.
        """
        INF = 10**9
        dp = [1, 0, 1]
        for obs in obstacles[1:]:
            for lane in range(3):
                if obs == lane + 1:
                    dp[lane] = INF
            for _ in range(3):
                for lane in range(3):
                    if obs == lane + 1:
                        continue
                    for other in range(3):
                        if other != lane and obs != other + 1:
                            dp[lane] = min(dp[lane], dp[other] + 1)
        return min(dp)

    def minSideJumps_bfs(self, obstacles: List[int]) -> int:
        """
        Interview explanation:
        Alternate 0-1 BFS: forward edge cost 0, side jump cost 1.

        Algorithm (0-1 BFS):
        - State (pos, lane); deque; forward appendleft; side jump append.

        Complexity: O(n) time, O(n) space.
        """
        n = len(obstacles)
        INF = 10**9
        dist = [[INF] * 3 for _ in range(n)]
        dist[0][1] = 0
        q = deque([(0, 1)])
        while q:
            pos, lane = q.popleft()
            d = dist[pos][lane]
            if pos == n - 1:
                return d
            # forward
            if pos + 1 < n and obstacles[pos + 1] != lane + 1:
                if d < dist[pos + 1][lane]:
                    dist[pos + 1][lane] = d
                    q.appendleft((pos + 1, lane))
            # side jump
            for nl in range(3):
                if nl != lane and obstacles[pos] != nl + 1:
                    if d + 1 < dist[pos][nl]:
                        dist[pos][nl] = d + 1
                        q.append((pos, nl))
        return -1
# @lc code=end
