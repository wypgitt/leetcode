#
# @lc app=leetcode id=3715 lang=python3
#
# [3715] Sum of Perfect Square Ancestors
#
# https://leetcode.com/problems/sum-of-perfect-square-ancestors/description/
#
# algorithms
# Hard (42.83%)
# Likes:    71
# Dislikes: 3
# Total Accepted:    7.6K
# Total Submissions: 17.8K
# Testcase Example:  "3\n[[0,1],[1,2]]\n[2,8,2]"
#
#
# You are given an integer n and an undirected tree rooted at node 0 with
# n nodes numbered from 0 to n - 1. This is represented by a 2D array
# edges of length n - 1, where edges[i] = [u_i, v_i] indicates an
# undirected edge between nodes u_i and v_i.
#
# You are also given an integer array nums, where nums[i] is the positive
# integer assigned to node i.
#
# Define a value t_i as the number of ancestors of node i such that the
# product nums[i] * nums[ancestor] is a perfect square.
#
# Return the sum of all t_i values for all nodes i in range [1, n - 1].
#
# Note:
#
# In a rooted tree, the ancestors of node i are all nodes on the path from
# node i to the root node 0, excluding i itself.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]], nums = [2,8,2]
#
# Output: 3
#
# Explanation:
#
#                         i
#                         Ancestors
#                         nums[i] * nums[ancestor]
#                         Square Check
#                         t_i
#
#                         1
#                         [0]
#                         nums[1] * nums[0] = 8 * 2 = 16
#                         16 is a perfect square
#                         1
#
#                         2
#                         [1, 0]
#                         nums[2] * nums[1] = 2 * 8 = 16
#
#                         nums[2] * nums[0] = 2 * 2 = 4
#                         Both 4 and 16 are perfect squares
#                         2
#
# Thus, the total number of valid ancestor pairs across all non-root nodes
# is 1 + 2 = 3.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[0,2]], nums = [1,2,4]
#
# Output: 1
#
# Explanation:
#
#                         i
#                         Ancestors
#                         nums[i] * nums[ancestor]
#                         Square Check
#                         t_i
#
#                         1
#                         [0]
#                         nums[1] * nums[0] = 2 * 1 = 2
#                         2 is not a perfect square
#                         0
#
#                         2
#                         [0]
#                         nums[2] * nums[0] = 4 * 1 = 4
#                         4 is a perfect square
#                         1
#
# Thus, the total number of valid ancestor pairs across all non-root nodes
# is 1.
#
# Example 3:
#
# Input: n = 4, edges = [[0,1],[0,2],[1,3]], nums = [1,2,9,4]
#
# Output: 2
#
# Explanation:
#
#                         i
#                         Ancestors
#                         nums[i] * nums[ancestor]
#                         Square Check
#                         t_i
#
#                         1
#                         [0]
#                         nums[1] * nums[0] = 2 * 1 = 2
#                         2 is not a perfect square
#                         0
#
#                         2
#                         [0]
#                         nums[2] * nums[0] = 9 * 1 = 9
#                         9 is a perfect square
#                         1
#
#                         3
#                         [1, 0]
#                         nums[3] * nums[1] = 4 * 2 = 8
#
#                         nums[3] * nums[0] = 4 * 1 = 4
#                         Only 4 is a perfect square
#                         1
#
# Thus, the total number of valid ancestor pairs across all non-root nodes
# is 0 + 1 + 1 = 2.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] = [u_i, v_i]
#
# 0 <= u_i, v_i <= n - 1
#
# nums.length == n
#
# 1 <= nums[i] <= 10^5
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def sumOfAncestors(self, n: int, edges: List[List[int]], nums: List[int]) -> int:
        """
        Interview explanation:
        nums[i]*nums[anc] is square iff their square-free kernels match. DFS with
        a frequency map of ancestor kernels counts valid pairs.

        Algorithm:
        - Linear sieve for SPF up to 1e5; kernel = product of primes with odd exponent.
        - DFS from 0: answer += freq[kernel(u)]; push; recurse; pop.

        Complexity: O(n + U log log U) time, O(n + U) space (U = 1e5).
        """
        U = 10**5 + 1
        spf = list(range(U))
        for i in range(2, int(U**0.5) + 1):
            if spf[i] == i:
                step = i
                start = i * i
                for j in range(start, U, step):
                    if spf[j] == j:
                        spf[j] = i

        def kernel(x: int) -> int:
            res = 1
            while x > 1:
                p = spf[x]
                if res % p == 0:
                    res //= p
                else:
                    res *= p
                x //= p
            return res

        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        freq = defaultdict(int)
        ans = 0

        def dfs(u: int, p: int) -> None:
            nonlocal ans
            k = kernel(nums[u])
            ans += freq[k]
            freq[k] += 1
            for v in g[u]:
                if v != p:
                    dfs(v, u)
            freq[k] -= 1

        dfs(0, -1)
        return ans
# @lc code=end
