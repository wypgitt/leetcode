#
# @lc app=leetcode id=1443 lang=python3
#
# [1443] Minimum Time to Collect All Apples in a Tree
#
# https://leetcode.com/problems/minimum-time-to-collect-all-apples-in-a-tree/description/
#
# algorithms
# Medium (63.82%)
# Likes:    3889
# Dislikes: 335
# Total Accepted:    159K
# Total Submissions: 249K
# Testcase Example:  "7"
#
# Given an undirected tree consisting of n vertices numbered from 0 to n-1,
# which has some apples in their vertices. You spend 1 second to walk over one
# edge of the tree. Return the minimum time in seconds you have to spend to
# collect all apples in the tree, starting at vertex 0 and coming back to this
# vertex.
#
# The edges of the undirected tree are given in the array edges, where edges[i]
# = [a_i, b_i] means that exists an edge connecting the vertices a_i and b_i.
# Additionally, there is a boolean array hasApple, where hasApple[i] = true
# means that vertex i has an apple; otherwise, it does not have any apple.
#
# Example 1:
#
# Input: n = 7, edges = [[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]], hasApple =
# [false,false,true,false,true,true,false]
# Output: 8
# Explanation: The figure above represents the given tree where red vertices
# have an apple. One optimal path to collect all apples is shown by the green
# arrows.
#
# Example 2:
#
# Input: n = 7, edges = [[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]], hasApple =
# [false,false,true,false,false,true,false]
# Output: 6
# Explanation: The figure above represents the given tree where red vertices
# have an apple. One optimal path to collect all apples is shown by the green
# arrows.
#
# Example 3:
#
# Input: n = 7, edges = [[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]], hasApple =
# [false,false,false,false,false,false,false]
# Output: 0
#
# Constraints:
#
# 1 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= a_i < b_i <= n - 1
#
# hasApple.length == n
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def minTime(self, n: int, edges: List[List[int]], hasApple: List[bool]) -> int:
        """
        Interview explanation:
        Undirected tree rooted at 0. Collect all apples and return to 0; each
        edge traversed twice if subtree has an apple. DFS returns whether
        subtree needs visit; cost += 2 per child edge that is needed.

        Algorithm:
        (DFS)
        - Build adj; dfs(u,parent): for children, if child_has: time+=2+child_time; return has or any child.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)

        def dfs(u: int, parent: int) -> int:
            time = 0
            for v in g[u]:
                if v == parent:
                    continue
                child = dfs(v, u)
                if child > 0 or hasApple[v]:
                    time += child + 2
            return time

        return dfs(0, -1)

    def minTime_postorder(self, n: int, edges: List[List[int]], hasApple: List[bool]) -> int:
        """
        Interview explanation:
        Alternate: mark nodes that lie on path to an apple (propagate up), then
        count marked edges * 2.

        Algorithm:
        - Build children tree; postorder mark; count edges to marked children.

        Complexity: O(n) time, O(n) space.
        """
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        children = [[] for _ in range(n)]

        def build(u, p):
            for v in g[u]:
                if v != p:
                    children[u].append(v)
                    build(v, u)

        build(0, -1)
        need = hasApple[:]

        def mark(u):
            for v in children[u]:
                if mark(v):
                    need[u] = True
            return need[u]

        mark(0)
        ans = 0
        for u in range(n):
            for v in children[u]:
                if need[v]:
                    ans += 2
        return ans
# @lc code=end
