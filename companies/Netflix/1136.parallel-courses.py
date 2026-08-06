#
# @lc app=leetcode id=1136 lang=python3
#
# [1136] Parallel Courses
#
# https://leetcode.com/problems/parallel-courses/description/
#
# algorithms
# Medium (62.33%)
# Likes:    1230
# Dislikes: 28
# Total Accepted:    113.9K
# Total Submissions: 182.7K
# Testcase Example:  "3\n[[1,3],[2,3]]"
#
#
# You are given an integer n, which indicates that there are n courses
# labeled from 1 to n. You are also given an array relations where
# relations[i] = [prevCourse_i, nextCourse_i], representing a prerequisite
# relationship between course prevCourse_i and course nextCourse_i: course
# prevCourse_i has to be taken before course nextCourse_i.
#
# In one semester, you can take any number of courses as long as you have
# taken all the prerequisites in the previous semester for the courses you
# are taking.
#
# Return the minimum number of semesters needed to take all courses. If
# there is no way to take all the courses, return -1.
#
# Example 1:
#
# Input: n = 3, relations = [[1,3],[2,3]]
# Output: 2
# Explanation: The figure above represents the given graph.
# In the first semester, you can take courses 1 and 2.
# In the second semester, you can take course 3.
#
# Example 2:
#
# Input: n = 3, relations = [[1,2],[2,3],[3,1]]
# Output: -1
# Explanation: No course can be studied because they are prerequisites of
# each other.
#
# Constraints:
#
# 1 <= n <= 5000
#
# 1 <= relations.length <= 5000
#
# relations[i].length == 2
#
# 1 <= prevCourse_i, nextCourse_i <= n
#
# prevCourse_i != nextCourse_i
#
# All the pairs [prevCourse_i, nextCourse_i] are unique.
#
# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minimumSemesters(self, n: int, relations: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Courses 1..n with prerequisites; take any number per semester.
        Min semesters = longest path in DAG (+1), or -1 if cycle. Kahn BFS
        levels is the classic approach.

        Algorithm (topo BFS):
        - Build graph + indegree; queue zeros; each layer = one semester.
        - If not all courses taken, cycle → -1.

        Complexity: O(n + E) time/space.
        """
        graph: List[List[int]] = [[] for _ in range(n + 1)]
        indeg = [0] * (n + 1)
        for a, b in relations:
            graph[a].append(b)
            indeg[b] += 1

        q = deque([i for i in range(1, n + 1) if indeg[i] == 0])
        sem = 0
        taken = 0
        while q:
            for _ in range(len(q)):
                u = q.popleft()
                taken += 1
                for v in graph[u]:
                    indeg[v] -= 1
                    if indeg[v] == 0:
                        q.append(v)
            sem += 1
        return sem if taken == n else -1

    def minimumSemesters_dfs(self, n: int, relations: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic DFS alternate: detect cycle with 3-color; DP longest path
        length from each node as minimum semesters needed from that course.

        Algorithm:
        - dfs returns max chain length; state 0/1/2 for unvis/visiting/done.
        - Answer = max over all nodes; -1 on back-edge.

        Complexity: O(n + E) time/space.
        """
        graph: List[List[int]] = [[] for _ in range(n + 1)]
        for a, b in relations:
            graph[a].append(b)

        state = [0] * (n + 1)
        dist = [0] * (n + 1)

        def dfs(u: int) -> bool:
            if state[u] == 1:
                return False
            if state[u] == 2:
                return True
            state[u] = 1
            best = 1
            for v in graph[u]:
                if not dfs(v):
                    return False
                best = max(best, 1 + dist[v])
            dist[u] = best
            state[u] = 2
            return True

        for i in range(1, n + 1):
            if state[i] == 0 and not dfs(i):
                return -1
        return max(dist[1:])
# @lc code=end
