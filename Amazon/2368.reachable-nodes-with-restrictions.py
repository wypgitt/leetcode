#
# @lc app=leetcode id=2368 lang=python3
#
# [2368] Reachable Nodes With Restrictions
#
# https://leetcode.com/problems/reachable-nodes-with-restrictions/description/
#
# algorithms
# Medium (60.67%)
# Likes:    788
# Dislikes: 34
# Total Accepted:    91.5K
# Total Submissions: 150.8K
# Testcase Example:  "7\n[[0,1],[1,2],[3,1],[4,0],[0,5],[5,6]]\n[4,5]"
#
# There is an undirected tree with n nodes labeled from 0 to n - 1 and n - 1
# edges.
#
# You are given a 2D integer array edges of length n - 1 where edges[i] = [a_i,
# b_i] indicates that there is an edge between nodes a_i and b_i in the tree.
# You are also given an integer array restricted which represents restricted
# nodes.
#
# Return the maximum number of nodes you can reach from node 0 without visiting
# a restricted node.
#
# Note that node 0 will not be a restricted node.
#
#
#
# Example 1:
#
# Input: n = 7, edges = [[0,1],[1,2],[3,1],[4,0],[0,5],[5,6]], restricted =
# [4,5]
# Output: 4
# Explanation: The diagram above shows the tree.
# We have that [0,1,2,3] are the only nodes that can be reached from node 0
# without visiting a restricted node.
#
# Example 2:
#
# Input: n = 7, edges = [[0,1],[0,2],[0,5],[0,4],[3,2],[6,5]], restricted =
# [4,2,1]
# Output: 3
# Explanation: The diagram above shows the tree.
# We have that [0,5,6] are the only nodes that can be reached from node 0
# without visiting a restricted node.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^5
#
#
# edges.length == n - 1
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i < n
#
#
# a_i != b_i
#
#
# edges represents a valid tree.
#
#
# 1 <= restricted.length < n
#
#
# 1 <= restricted[i] < n
#
#
# All the values of restricted are unique.
#

# @lc code=start

from typing import List
from collections import defaultdict, deque


class Solution:
    def reachableNodes(self, n: int, edges: List[List[int]], restricted: List[int]) -> int:
        """
        Interview explanation:
        Undirected tree; cannot visit restricted nodes. Count nodes reachable
        from 0 without entering restricted.

        Algorithm:
        - BFS/DFS from 0 on graph excluding restricted nodes.

        Complexity: O(n) time, O(n) space.
        """
        ban = set(restricted)
        g = defaultdict(list)
        for a, b in edges:
            if a not in ban and b not in ban:
                g[a].append(b)
                g[b].append(a)
        if 0 in ban:
            return 0
        seen = {0}
        q = deque([0])
        while q:
            u = q.popleft()
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return len(seen)

    def reachableNodes_dfs(self, n: int, edges: List[List[int]], restricted: List[int]) -> int:
        """
        Interview explanation:
        Alternate: recursive DFS count from 0.

        Algorithm:
        - Build adj excluding ban; dfs mark visited.

        Complexity: O(n) time, O(n) space.
        """
        ban = set(restricted)
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        seen = set()

        def dfs(u: int) -> None:
            seen.add(u)
            for v in g[u]:
                if v not in seen and v not in ban:
                    dfs(v)

        if 0 in ban:
            return 0
        dfs(0)
        return len(seen)

    def reachableNodes_uf(self, n: int, edges: List[List[int]], restricted: List[int]) -> int:
        """
        Interview explanation:
        Alternate: Union-Find connecting non-restricted edges; size of 0's component.

        Algorithm:
        - UF unite allowed edges; count nodes with same parent as 0.

        Complexity: O(n α(n)) time, O(n) space.
        """
        ban = set(restricted)
        parent = list(range(n))
        size = [1] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            parent[rb] = ra
            size[ra] += size[rb]

        for a, b in edges:
            if a not in ban and b not in ban:
                union(a, b)
        return 0 if 0 in ban else size[find(0)]
# @lc code=end
