#
# @lc app=leetcode id=797 lang=python3
#
# [797] All Paths From Source to Target
#
# https://leetcode.com/problems/all-paths-from-source-to-target/description/
#
# algorithms
# Medium (83.76%)
# Likes:    7693
# Dislikes: 156
# Total Accepted:    713K
# Total Submissions: 851K
# Testcase Example:  "[[1,2],[3],[3],[]]"
#
# Given a directed acyclic graph (DAG) of n nodes labeled from 0 to n - 1, find
# all possible paths from node 0 to node n - 1 and return them in any order.
#
# The graph is given as follows: graph[i] is a list of all nodes you can visit
# from node i (i.e., there is a directed edge from node i to node graph[i][j]).
#
# Example 1:
#
# Input: graph = [[1,2],[3],[3],[]]
# Output: [[0,1,3],[0,2,3]]
# Explanation: There are two paths: 0 -> 1 -> 3 and 0 -> 2 -> 3.
#
# Example 2:
#
# Input: graph = [[4,3,1],[3,2,4],[3],[4],[]]
# Output: [[0,4],[0,3,4],[0,1,3,4],[0,1,2,3,4],[0,1,4]]
#
# Constraints:
#
# n == graph.length
#
# 2 <= n <= 15
#
# 0 <= graph[i][j] < n
#
# graph[i][j] != i (i.e., there will be no self-loops).
#
# All the elements of graph[i] are unique.
#
# The input graph is guaranteed to be a DAG.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def allPathsSourceTarget(self, graph: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        DAG from 0 to n-1; enumerate all paths via DFS backtracking: append
        node, recurse to neighbors, pop. Record path when reaching n-1.

        Algorithm (DFS):
        - path=[0]; dfs(0): if u==n-1: record copy; else for v in graph[u]:
          push v, dfs(v), pop.

        Complexity: O(2^n * n) time/space worst case (path enumeration).
        """
        n = len(graph)
        res: List[List[int]] = []
        path = [0]

        def dfs(u: int) -> None:
            if u == n - 1:
                res.append(path[:])
                return
            for v in graph[u]:
                path.append(v)
                dfs(v)
                path.pop()

        dfs(0)
        return res

    def allPathsSourceTarget_bfs(self, graph: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: BFS queue of paths; when a path ends at n-1, collect it;
        else extend by each neighbor.

        Algorithm:
        - q=[[0]]; while q: path=pop; if end collect else enqueue path+[v].

        Complexity: O(2^n * n) time/space.
        """
        n = len(graph)
        res: List[List[int]] = []
        q = deque([[0]])
        while q:
            path = q.popleft()
            u = path[-1]
            if u == n - 1:
                res.append(path)
                continue
            for v in graph[u]:
                q.append(path + [v])
        return res
# @lc code=end

