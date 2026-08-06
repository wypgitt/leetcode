#
# @lc app=leetcode id=2876 lang=python3
#
# [2876] Count Visited Nodes in a Directed Graph
#
# https://leetcode.com/problems/count-visited-nodes-in-a-directed-graph/description/
#
# algorithms
# Hard (31.34%)
# Likes:    370
# Dislikes: 7
# Total Accepted:    15.2K
# Total Submissions: 48.4K
# Testcase Example:  "[1,2,0,0]"
#
#
# There is a directed graph consisting of n nodes numbered from 0 to n - 1
# and n directed edges.
#
# You are given a 0-indexed array edges where edges[i] indicates that
# there is an edge from node i to node edges[i].
#
# Consider the following process on the graph:
#
# You start from a node x and keep visiting other nodes through edges
# until you reach a node that you have already visited before on this same
# process.
#
# Return an array answer where answer[i] is the number of different nodes
# that you will visit if you perform the process starting from node i.
#
# Example 1:
#
# Input: edges = [1,2,0,0]
# Output: [3,3,3,4]
# Explanation: We perform the process starting from each node in the
# following way:
# - Starting from node 0, we visit the nodes 0 -> 1 -> 2 -> 0. The number
# of different nodes we visit is 3.
# - Starting from node 1, we visit the nodes 1 -> 2 -> 0 -> 1. The number
# of different nodes we visit is 3.
# - Starting from node 2, we visit the nodes 2 -> 0 -> 1 -> 2. The number
# of different nodes we visit is 3.
# - Starting from node 3, we visit the nodes 3 -> 0 -> 1 -> 2 -> 0. The
# number of different nodes we visit is 4.
#
# Example 2:
#
# Input: edges = [1,2,3,4,0]
# Output: [5,5,5,5,5]
# Explanation: Starting from any node we can visit every node in the graph
# in the process.
#
# Constraints:
#
# n == edges.length
#
# 2 <= n <= 10^5
#
# 0 <= edges[i] <= n - 1
#
# edges[i] != i
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def countVisitedNodes(self, edges: List[int]) -> List[int]:
        """
        Interview explanation:
        Functional graph: each node outdegree 1. From i, walk until a repeat;
        answer[i] = distinct nodes visited (cycle length + tail length into it).

        Algorithm:
        - Peel indegree-0 nodes (Kahn) onto a stack; remaining nodes lie on cycles.
        - Assign each cycle node the cycle length; then pop the stack and set
          ans[u] = ans[edges[u]] + 1 for tails.

        Alternate: DFS with path stack / colors to detect cycles then memoize.

        Complexity: O(n) time, O(n) space.
        """
        n = len(edges)
        ans = [0] * n
        indeg = [0] * n
        for v in edges:
            indeg[v] += 1

        seen = [False] * n
        stack: List[int] = []
        q = deque(i for i, d in enumerate(indeg) if d == 0)
        while q:
            u = q.popleft()
            seen[u] = True
            stack.append(u)
            indeg[edges[u]] -= 1
            if indeg[edges[u]] == 0:
                q.append(edges[u])

        for i in range(n):
            if not seen[i]:
                length = 0
                u = i
                while not seen[u]:
                    seen[u] = True
                    length += 1
                    u = edges[u]
                ans[i] = length
                u = edges[i]
                while u != i:
                    ans[u] = length
                    u = edges[u]

        while stack:
            u = stack.pop()
            ans[u] = ans[edges[u]] + 1
        return ans
# @lc code=end
