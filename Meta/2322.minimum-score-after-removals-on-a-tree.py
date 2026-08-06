#
# @lc app=leetcode id=2322 lang=python3
#
# [2322] Minimum Score After Removals on a Tree
#
# https://leetcode.com/problems/minimum-score-after-removals-on-a-tree/description/
#
# algorithms
# Hard (76.03%)
# Likes:    823
# Dislikes: 47
# Total Accepted:    70.3K
# Total Submissions: 92.4K
# Testcase Example:  "[1,5,5,4,11]\n[[0,1],[1,2],[1,3],[3,4]]"
#
# There is an undirected connected tree with n nodes labeled from 0 to n - 1 and
# n - 1 edges.
#
# You are given a 0-indexed integer array nums of length n where nums[i]
# represents the value of the i^th node. You are also given a 2D integer array
# edges of length n - 1 where edges[i] = [a_i, b_i] indicates that there is an
# edge between nodes a_i and b_i in the tree.
#
# Remove two distinct edges of the tree to form three connected components. For
# a pair of removed edges, the following steps are defined:
#
#
# Get the XOR of all the values of the nodes for each of the three components
# respectively.
#
#
# The difference between the largest XOR value and the smallest XOR value is the
# score of the pair.
#
#
# For example, say the three components have the node values: [4,5,7], [1,9],
# and [3,3,3]. The three XOR values are 4 ^ 5 ^ 7 = 6, 1 ^ 9 = 8, and 3 ^ 3 ^ 3
# = 3. The largest XOR value is 8 and the smallest XOR value is 3. The score is
# then 8 - 3 = 5.
#
# Return the minimum score of any possible pair of edge removals on the given
# tree.
#
#
#
# Example 1:
#
# Input: nums = [1,5,5,4,11], edges = [[0,1],[1,2],[1,3],[3,4]]
# Output: 9
# Explanation: The diagram above shows a way to make a pair of removals.
# - The 1^st component has nodes [1,3,4] with values [5,4,11]. Its XOR value is
# 5 ^ 4 ^ 11 = 10.
# - The 2^nd component has node [0] with value [1]. Its XOR value is 1 = 1.
# - The 3^rd component has node [2] with value [5]. Its XOR value is 5 = 5.
# The score is the difference between the largest and smallest XOR value which
# is 10 - 1 = 9.
# It can be shown that no other pair of removals will obtain a smaller score
# than 9.
#
# Example 2:
#
# Input: nums = [5,5,2,4,4,2], edges = [[0,1],[1,2],[5,2],[4,3],[1,3]]
# Output: 0
# Explanation: The diagram above shows a way to make a pair of removals.
# - The 1^st component has nodes [3,4] with values [4,4]. Its XOR value is 4 ^ 4
# = 0.
# - The 2^nd component has nodes [1,0] with values [5,5]. Its XOR value is 5 ^ 5
# = 0.
# - The 3^rd component has nodes [2,5] with values [2,2]. Its XOR value is 2 ^ 2
# = 0.
# The score is the difference between the largest and smallest XOR value which
# is 0 - 0 = 0.
# We cannot obtain a smaller score than 0.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 3 <= n <= 1000
#
#
# 1 <= nums[i] <= 10^8
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

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def minimumScore(self, nums: List[int], edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Remove two edges from a tree, splitting into 3 components. Score =
        maxXOR - minXOR of the three component XORs. Minimize the score.

        Algorithm:
        - Root the tree; compute subtree XOR and in/out times.
        - Enumerate two edges via node pairs (subtree roots a,b):
          cases: nested vs disjoint; compute three XORs; track min score.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        xor = [0] * n
        tin = [0] * n
        tout = [0] * n
        timer = 0

        def dfs(u: int, p: int) -> None:
            nonlocal timer
            timer += 1
            tin[u] = timer
            xor[u] = nums[u]
            for v in g[u]:
                if v == p:
                    continue
                dfs(v, u)
                xor[u] ^= xor[v]
            tout[u] = timer

        dfs(0, -1)
        total = xor[0]
        ans = 10**18

        def is_ancestor(a: int, b: int) -> bool:
            return tin[a] <= tin[b] <= tout[a]

        # enumerate two distinct non-root nodes as cut roots (edge to parent)
        nodes = list(range(1, n))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                if is_ancestor(a, b):
                    x, y, z = xor[b], xor[a] ^ xor[b], total ^ xor[a]
                elif is_ancestor(b, a):
                    x, y, z = xor[a], xor[b] ^ xor[a], total ^ xor[b]
                else:
                    x, y, z = xor[a], xor[b], total ^ xor[a] ^ xor[b]
                ans = min(ans, max(x, y, z) - min(x, y, z))
        return ans
# @lc code=end
