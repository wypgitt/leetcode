#
# @lc app=leetcode id=3910 lang=python3
#
# [3910] Count Connected Subgraphs with Even Node Sum
#
# https://leetcode.com/problems/count-connected-subgraphs-with-even-node-sum/description/
#
# algorithms
# Hard (62.25%)
# Likes:    42
# Dislikes: 2
# Total Accepted:    9.2K
# Total Submissions: 14.7K
# Testcase Example:  "[1,0,1]\n[[0,1],[1,2]]"
#
#
# You are given an undirected graph with n nodes labeled from 0 to n - 1.
# Node i has a value of nums[i], which is either 0 or 1. The edges of the
# graph are given by a 2D array edges where edges[i] = [u_i, v_i]
# represents an edge between node u_i and node v_i.
#
# For a non-empty subset s of nodes in the graph, we consider the induced
# subgraph of s generated as follows:
#
# We keep only the nodes in s.
#
# We keep only the edges whose two endpoints are both in s.
#
# Return an integer representing the number of non-empty subsets s of
# nodes in the graph such that:
#
# The induced subgraph of s is connected.
#
# The sum of node values in s is even.
#
# Example 1:
#
# Input: nums = [1,0,1], edges = [[0,1],[1,2]]
#
# Output: 2
#
# Explanation:
#
#                         s
#                         connected?
#                         sum of node values
#                         counted?
#
#                         [0]
#                         Yes
#                         1
#                         No
#
#                         [1]
#                         Yes
#                         0
#                         Yes
#
#                         [2]
#                         Yes
#                         1
#                         No
#
#                         [0,1]
#                         Yes
#                         1
#                         No
#
#                         [0,2]
#                         No, node 0 and node 2 are disconnected.
#                         2
#                         No
#
#                         [1,2]
#                         Yes
#                         1
#                         No
#
#                         [0,1,2]
#                         Yes
#                         2
#                         Yes
#
# Example 2:
#
# Input: nums = [1], edges = []
#
# Output: 0
#
# Explanation:
#
#                         s
#                         connected?
#                         sum of node values
#                         counted?
#
#                         [0]
#                         Yes
#                         1
#                         No
#
# Constraints:
#
# 1 <= n == nums.length <= 13
#
# nums[i] is 0 or 1.
#
# 0 <= edges.length <= n * (n - 1) / 2
#
# edges[i] = [u_i, v_i]
#
# 0 <= u_i < v_i < n
#
# All edges are distinct.
#

# @lc code=start
class Solution:
    def evenSumSubgraphs(self, nums: list[int], edges: list[list[int]]) -> int:
        """
        Interview explanation:
        n ≤ 13 → enumerate all nonempty subsets; keep those that are connected
        in the induced subgraph and have even value-sum.

        Algorithm:
        - Build adjacency lists.
        - For each mask: BFS/DFS from any set bit through edges inside mask;
          check full coverage and popcount(mask & odd_bits) even.

        Complexity: O((n + m) 2^n) time, O(n + m) space.
        """
        n = len(nums)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        odd_mask = 0
        for i, v in enumerate(nums):
            if v:
                odd_mask |= 1 << i

        def connected(mask: int) -> bool:
            start = (mask & -mask).bit_length() - 1
            rem = mask ^ (1 << start)
            stk = [start]
            while stk:
                u = stk.pop()
                for v in adj[u]:
                    if rem & (1 << v):
                        rem ^= 1 << v
                        stk.append(v)
            return rem == 0

        ans = 0
        for mask in range(1, 1 << n):
            if (mask & odd_mask).bit_count() % 2 == 0 and connected(mask):
                ans += 1
        return ans

    def evenSumSubgraphs_parity(self, nums: list[int], edges: list[list[int]]) -> int:
        """
        Interview explanation:
        Alternate: compute subset sum parity by XORing nums bits directly.

        Complexity: O((n + m) 2^n) time, O(n + m) space.
        """
        n = len(nums)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        def even(mask: int) -> bool:
            parity = 0
            m = mask
            while m:
                i = (m & -m).bit_length() - 1
                parity ^= nums[i]
                m ^= 1 << i
            return parity == 0

        def connected(mask: int) -> bool:
            start = (mask & -mask).bit_length() - 1
            rem = mask ^ (1 << start)
            stk = [start]
            while stk:
                u = stk.pop()
                for v in adj[u]:
                    if rem & (1 << v):
                        rem ^= 1 << v
                        stk.append(v)
            return rem == 0

        return sum(1 for mask in range(1, 1 << n) if even(mask) and connected(mask))
# @lc code=end
