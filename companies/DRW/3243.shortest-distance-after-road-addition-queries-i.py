#
# @lc app=leetcode id=3243 lang=python3
#
# [3243] Shortest Distance After Road Addition Queries I
#
# https://leetcode.com/problems/shortest-distance-after-road-addition-queries-i/description/
#
# algorithms
# Medium (61.92%)
# Likes:    646
# Dislikes: 29
# Total Accepted:    118.3K
# Total Submissions: 191.1K
# Testcase Example:  "5\n[[2,4],[0,2],[0,4]]"
#
#
# You are given an integer n and a 2D integer array queries.
#
# There are n cities numbered from 0 to n - 1. Initially, there is a
# unidirectional road from city i to city i + 1 for all 0 <= i < n - 1.
#
# queries[i] = [u_i, v_i] represents the addition of a new unidirectional
# road from city u_i to city v_i. After each query, you need to find the
# length of the shortest path from city 0 to city n - 1.
#
# Return an array answer where for each i in the range [0, queries.length
# - 1], answer[i] is the length of the shortest path from city 0 to city n
# - 1 after processing the first i + 1 queries.
#
# Example 1:
#
# Input: n = 5, queries = [[2,4],[0,2],[0,4]]
#
# Output: [3,2,1]
#
# Explanation:
#
# After the addition of the road from 2 to 4, the length of the shortest
# path from 0 to 4 is 3.
#
# After the addition of the road from 0 to 2, the length of the shortest
# path from 0 to 4 is 2.
#
# After the addition of the road from 0 to 4, the length of the shortest
# path from 0 to 4 is 1.
#
# Example 2:
#
# Input: n = 4, queries = [[0,3],[0,2]]
#
# Output: [1,1]
#
# Explanation:
#
# After the addition of the road from 0 to 3, the length of the shortest
# path from 0 to 3 is 1.
#
# After the addition of the road from 0 to 2, the length of the shortest
# path remains 1.
#
# Constraints:
#
# 3 <= n <= 500
#
# 1 <= queries.length <= 500
#
# queries[i].length == 2
#
# 0 <= queries[i][0] < queries[i][1] < n
#
# 1 < queries[i][1] - queries[i][0]
#
# There are no repeated roads among the queries.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def shortestDistanceAfterQueries(self, n: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Cities form a path 0->1->...->n-1; each query adds a forward shortcut.
        After every addition, report dist(0, n-1). n and q are <= 500, so BFS
        after each query is fine.

        Algorithm:
        - Maintain adjacency lists; initially i -> i+1.
        - For each query, add edge u->v and BFS from 0 for shortest path.

        Complexity: O(q * (n + m)) time, O(n + m) space.

        Alternate: keep dist[] and relax forward after each edge (also O(qn)).
        """
        g: List[List[int]] = [[] for _ in range(n)]
        for i in range(n - 1):
            g[i].append(i + 1)

        def bfs() -> int:
            dist = [-1] * n
            dist[0] = 0
            q = deque([0])
            while q:
                u = q.popleft()
                if u == n - 1:
                    return dist[u]
                for v in g[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            return dist[n - 1]

        ans = []
        for u, v in queries:
            g[u].append(v)
            ans.append(bfs())
        return ans
# @lc code=end
