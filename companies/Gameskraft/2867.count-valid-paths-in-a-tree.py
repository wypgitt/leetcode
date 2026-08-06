#
# @lc app=leetcode id=2867 lang=python3
#
# [2867] Count Valid Paths in a Tree
#
# https://leetcode.com/problems/count-valid-paths-in-a-tree/description/
#
# algorithms
# Hard (36.92%)
# Likes:    294
# Dislikes: 9
# Total Accepted:    10.4K
# Total Submissions: 28.1K
# Testcase Example:  "5\n[[1,2],[1,3],[2,4],[2,5]]"
#
#
# There is an undirected tree with n nodes labeled from 1 to n. You are
# given the integer n and a 2D integer array edges of length n - 1, where
# edges[i] = [u_i, v_i] indicates that there is an edge between nodes u_i
# and v_i in the tree.
#
# Return the number of valid paths in the tree.
#
# A path (a, b) is valid if there exists exactly one prime number among
# the node labels in the path from a to b.
#
# Note that:
#
# The path (a, b) is a sequence of distinct nodes starting with node a and
# ending with node b such that every two adjacent nodes in the sequence
# share an edge in the tree.
#
# Path (a, b) and path (b, a) are considered the same and counted only
# once.
#
# Example 1:
#
# Input: n = 5, edges = [[1,2],[1,3],[2,4],[2,5]]
# Output: 4
# Explanation: The pairs with exactly one prime number on the path between
# them are:
# - (1, 2) since the path from 1 to 2 contains prime number 2.
# - (1, 3) since the path from 1 to 3 contains prime number 3.
# - (1, 4) since the path from 1 to 4 contains prime number 2.
# - (2, 4) since the path from 2 to 4 contains prime number 2.
# It can be shown that there are only 4 valid paths.
#
# Example 2:
#
# Input: n = 6, edges = [[1,2],[1,3],[2,4],[3,5],[3,6]]
# Output: 6
# Explanation: The pairs with exactly one prime number on the path between
# them are:
# - (1, 2) since the path from 1 to 2 contains prime number 2.
# - (1, 3) since the path from 1 to 3 contains prime number 3.
# - (1, 4) since the path from 1 to 4 contains prime number 2.
# - (1, 6) since the path from 1 to 6 contains prime number 3.
# - (2, 4) since the path from 2 to 4 contains prime number 2.
# - (3, 6) since the path from 3 to 6 contains prime number 3.
# It can be shown that there are only 6 valid paths.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 1 <= u_i, v_i <= n
#
# The input is generated such that edges represent a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def countPaths(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Count unordered paths whose node labels contain exactly one prime.
        Paths with 0 or >=2 primes do not count.

        Algorithm:
        - Sieve primes in [1..n]; build adjacency list.
        - DFS returning (#nodes with 0 primes on rootward path prefix in subtree,
          #with exactly 1). When combining parent-side counts with a child, add
          zero*one + one*zero cross products to the answer.
        - Through a prime node, only zero-prime child sizes may extend a
          one-prime path; one-prime children stop (would become two primes).

        Alternate: union-find non-prime components, then for each prime sum
        neighbor component sizes and pairwise products.

        Complexity: O(n log log n) sieve + O(n) DFS; O(n) space.
        """
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(n**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, n + 1, i):
                    is_prime[j] = False

        graph = [[] for _ in range(n + 1)]
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        ans = 0

        def dfs(u: int, parent: int) -> tuple[int, int]:
            nonlocal ans
            zero = 0 if is_prime[u] else 1
            one = 1 if is_prime[u] else 0
            for v in graph[u]:
                if v == parent:
                    continue
                cz, co = dfs(v, u)
                ans += zero * co + one * cz
                if is_prime[u]:
                    one += cz
                else:
                    zero += cz
                    one += co
            return zero, one

        dfs(1, -1)
        return ans
# @lc code=end
