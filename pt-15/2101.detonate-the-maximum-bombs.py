#
# @lc app=leetcode id=2101 lang=python3
#
# [2101] Detonate the Maximum Bombs
#
# https://leetcode.com/problems/detonate-the-maximum-bombs/description/
#
# algorithms
# Medium (50.31%)
# Likes:    3436
# Dislikes: 163
# Total Accepted:    186.8K
# Total Submissions: 371.2K
# Testcase Example:  "[[2,1,3],[6,1,4]]"
#
# You are given a list of bombs. The range of a bomb is defined as the area
# where its effect can be felt. This area is in the shape of a circle with the
# center as the location of the bomb.
#
# The bombs are represented by a 0-indexed 2D integer array bombs where bombs[i]
# = [x_i, y_i, r_i]. x_i and y_i denote the X-coordinate and Y-coordinate of the
# location of the i^th bomb, whereas r_i denotes the radius of its range.
#
# You may choose to detonate a single bomb. When a bomb is detonated, it will
# detonate all bombs that lie in its range. These bombs will further detonate
# the bombs that lie in their ranges.
#
# Given the list of bombs, return the maximum number of bombs that can be
# detonated if you are allowed to detonate only one bomb.
#
#
#
# Example 1:
#
# Input: bombs = [[2,1,3],[6,1,4]]
# Output: 2
# Explanation:
# The above figure shows the positions and ranges of the 2 bombs.
# If we detonate the left bomb, the right bomb will not be affected.
# But if we detonate the right bomb, both bombs will be detonated.
# So the maximum bombs that can be detonated is max(1, 2) = 2.
#
# Example 2:
#
# Input: bombs = [[1,1,5],[10,10,5]]
# Output: 1
# Explanation:
# Detonating either bomb will not detonate the other bomb, so the maximum number
# of bombs that can be detonated is 1.
#
# Example 3:
#
# Input: bombs = [[1,2,3],[2,3,1],[3,4,2],[4,5,3],[5,6,4]]
# Output: 5
# Explanation:
# The best bomb to detonate is bomb 0 because:
# - Bomb 0 detonates bombs 1 and 2. The red circle denotes the range of bomb 0.
# - Bomb 2 detonates bomb 3. The blue circle denotes the range of bomb 2.
# - Bomb 3 detonates bomb 4. The green circle denotes the range of bomb 3.
# Thus all 5 bombs are detonated.
#
#
#
# Constraints:
#
#
# 1 <= bombs.length <= 100
#
#
# bombs[i].length == 3
#
#
# 1 <= x_i, y_i, r_i <= 10^5
#


# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def maximumDetonation(self, bombs: List[List[int]]) -> int:
        """
        Interview explanation:
        Bombs form a directed graph: i can detonate j if j is within i's blast
        radius. Find the largest set reachable from any single starting bomb.

        Algorithm:
        - Build directed edges by distance checks.
        - BFS/DFS from each bomb; track max reachable count.

        Complexity: O(n^3) time (n starts * O(n^2) edges walk), O(n^2) space.
        """
        n = len(bombs)
        g = [[] for _ in range(n)]
        for i in range(n):
            x1, y1, r1 = bombs[i]
            for j in range(n):
                if i == j:
                    continue
                x2, y2, _ = bombs[j]
                dx, dy = x1 - x2, y1 - y2
                if dx * dx + dy * dy <= r1 * r1:
                    g[i].append(j)

        def bfs(start: int) -> int:
            seen = {start}
            q = deque([start])
            while q:
                u = q.popleft()
                for v in g[u]:
                    if v not in seen:
                        seen.add(v)
                        q.append(v)
            return len(seen)

        return max(bfs(i) for i in range(n))

    def maximumDetonation_dfs(self, bombs: List[List[int]]) -> int:
        """
        Interview explanation:
        Same graph model; DFS reachability from each start.

        Algorithm:
        - Build digraph; recursive DFS; max visited size.

        Complexity: O(n^3) time, O(n^2) space.
        """
        n = len(bombs)
        g = [[] for _ in range(n)]
        for i in range(n):
            x1, y1, r1 = bombs[i]
            for j in range(n):
                if i == j:
                    continue
                x2, y2, _ = bombs[j]
                dx, dy = x1 - x2, y1 - y2
                if dx * dx + dy * dy <= r1 * r1:
                    g[i].append(j)

        def dfs(u: int, seen: set) -> None:
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    dfs(v, seen)

        ans = 0
        for i in range(n):
            seen = {i}
            dfs(i, seen)
            ans = max(ans, len(seen))
        return ans
# @lc code=end

