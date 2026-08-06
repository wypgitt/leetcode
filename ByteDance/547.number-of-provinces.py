#
# @lc app=leetcode id=547 lang=python3
#
# [547] Number of Provinces
#
# https://leetcode.com/problems/number-of-provinces/description/
#
# algorithms
# Medium (70.87%)
# Likes:    11345
# Dislikes: 434
# Total Accepted:    1.6M
# Total Submissions: 2.3M
# Testcase Example:  "[[1,1,0],[1,1,0],[0,0,1]]"
#
# There are n cities. Some of them are connected, while some are not. If city a
# is connected directly with city b, and city b is connected directly with city
# c, then city a is connected indirectly with city c.
#
# A province is a group of directly or indirectly connected cities and no other
# cities outside of the group.
#
# You are given an n x n matrix isConnected where isConnected[i][j] = 1 if the
# i^th city and the j^th city are directly connected, and isConnected[i][j] = 0
# otherwise.
#
# Return the total number of provinces.
#
# Example 1:
#
# Input: isConnected = [[1,1,0],[1,1,0],[0,0,1]]
# Output: 2
#
# Example 2:
#
# Input: isConnected = [[1,0,0],[0,1,0],[0,0,1]]
# Output: 3
#
# Constraints:
#
# 1 <= n <= 200
#
# n == isConnected.length
#
# n == isConnected[i].length
#
# isConnected[i][j] is 1 or 0.
#
# isConnected[i][i] == 1
#
# isConnected[i][j] == isConnected[j][i]
#

# @lc code=start
from typing import List
class Solution:
    def findCircleNum(self, isConnected: List[List[int]]) -> int:
        """
        Interview explanation:
        Provinces are connected components in an undirected graph given by an
        adjacency matrix. Union-Find merges cities that are directly connected;
        the number of roots is the answer.

        Algorithm:
        - Init parent[i]=i; for each edge i<j with isConnected[i][j], union.
        - Count distinct find(i).

        Complexity: O(n^2 α(n)) time, O(n) space.
        """
        n = len(isConnected)
        parent = list(range(n))
        rank = [0] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        for i in range(n):
            for j in range(i + 1, n):
                if isConnected[i][j]:
                    union(i, j)
        return len({find(i) for i in range(n)})

    def findCircleNum_dfs(self, isConnected: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: DFS/BFS from each unvisited city, marking its province;
        count how many times a new traversal starts.

        Algorithm:
        - For each unvisited i, DFS all j with isConnected[i][j] and increment.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(isConnected)
        visited = [False] * n

        def dfs(i: int) -> None:
            visited[i] = True
            for j in range(n):
                if isConnected[i][j] and not visited[j]:
                    dfs(j)

        provinces = 0
        for i in range(n):
            if not visited[i]:
                provinces += 1
                dfs(i)
        return provinces
# @lc code=end

