#
# @lc app=leetcode id=1462 lang=python3
#
# [1462] Course Schedule IV
#
# https://leetcode.com/problems/course-schedule-iv/description/
#
# algorithms
# Medium (60.13%)
# Likes:    2175
# Dislikes: 94
# Total Accepted:    214K
# Total Submissions: 355K
# Testcase Example:  "6"
#
# There are a total of numCourses courses you have to take, labeled from 0 to
# numCourses - 1. You are given an array prerequisites where prerequisites[i] =
# [a_i, b_i] indicates that you must take course a_i first if you want to take
# course b_i.
#
# For example, the pair [0, 1] indicates that you have to take course 0 before
# you can take course 1.
#
# Prerequisites can also be indirect. If course a is a prerequisite of course
# b, and course b is a prerequisite of course c, then course a is a
# prerequisite of course c.
#
# You are also given an array queries where queries[j] = [u_j, v_j]. For the
# j^th query, you should answer whether course u_j is a prerequisite of course
# v_j or not.
#
# Return a boolean array answer, where answer[j] is the answer to the j^th
# query.
#
# Example 1:
#
# Input: numCourses = 2, prerequisites = [[1,0]], queries = [[0,1],[1,0]]
# Output: [false,true]
# Explanation: The pair [1, 0] indicates that you have to take course 1 before
# you can take course 0.
# Course 0 is not a prerequisite of course 1, but the opposite is true.
#
# Example 2:
#
# Input: numCourses = 2, prerequisites = [], queries = [[1,0],[0,1]]
# Output: [false,false]
# Explanation: There are no prerequisites, and each course is independent.
#
# Example 3:
#
# Input: numCourses = 3, prerequisites = [[1,2],[1,0],[2,0]], queries =
# [[1,0],[1,2]]
# Output: [true,true]
#
# Constraints:
#
# 2 <= numCourses <= 100
#
# 0 <= prerequisites.length <= (numCourses * (numCourses - 1) / 2)
#
# prerequisites[i].length == 2
#
# 0 <= a_i, b_i <= numCourses - 1
#
# a_i != b_i
#
# All the pairs [a_i, b_i] are unique.
#
# The prerequisites graph has no cycles.
#
# 1 <= queries.length <= 10^4
#
# 0 <= u_i, v_i <= numCourses - 1
#
# u_i != v_i
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def checkIfPrerequisite(
        self, numCourses: int, prerequisites: List[List[int]], queries: List[List[int]]
    ) -> List[bool]:
        """
        Interview explanation:
        Queries ask if u is a prerequisite of v (transitive). Compute reachability
        via Floyd-Warshall on the prerequisite DAG.

        Algorithm:
        - reach[u][v]=True for edges; FW: if reach[i][k] and reach[k][j] then i→j.
        - Answer queries from matrix.

        Complexity: O(n^3 + q) time, O(n^2) space.
        """
        n = numCourses
        reach = [[False] * n for _ in range(n)]
        for a, b in prerequisites:
            reach[a][b] = True
        for k in range(n):
            for i in range(n):
                if reach[i][k]:
                    for j in range(n):
                        if reach[k][j]:
                            reach[i][j] = True
        return [reach[u][v] for u, v in queries]

    def checkIfPrerequisite_bfs(
        self, numCourses: int, prerequisites: List[List[int]], queries: List[List[int]]
    ) -> List[bool]:
        """
        Interview explanation:
        Alternate: BFS/DFS from each node to collect all reachable descendants;
        good when graph is sparse.

        Algorithm:
        - Build adj; for each start BFS, fill reach[start]; answer queries.

        Complexity: O(n*(n+m) + q) time, O(n^2) space.
        """
        n = numCourses
        adj = defaultdict(list)
        for a, b in prerequisites:
            adj[a].append(b)
        reach = [set() for _ in range(n)]
        for s in range(n):
            q = deque([s])
            seen = {s}
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        reach[s].add(v)
                        q.append(v)
        return [v in reach[u] for u, v in queries]
# @lc code=end
