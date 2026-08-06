#
# @lc app=leetcode id=3949 lang=python3
#
# [3949] Subtree Inversion Sum II
#
# https://leetcode.com/problems/subtree-inversion-sum-ii/description/
#
# algorithms
# Hard (71.24%)
# Likes:    1
# Dislikes: 1
# Total Accepted:    265
# Total Submissions: 372
# Testcase Example:  "[[0,1],[0,2],[0,3],[1,4],[1,5]]\n[1,0,-10,3,4,5]\n2"
#
#
# You are given an undirected tree rooted at node 0, with n nodes numbered
# from 0 to n - 1. The tree is represented by a 2D integer array edges of
# length n - 1, where edges[i] = [u_i, v_i] indicates an edge between
# nodes u_i and v_i.
#
# You are also given an integer array nums of length n, where nums[i]
# represents the value at node i, and an integer k.
#
# You may perform inversion operations on a subset of nodes subject to the
# following rules:
#
# Subtree Inversion Operation:
#
# When you invert a node, every value in the subtree rooted at that node
# is multiplied by -1.
#
# Distance Constraint on Inversions:
#
# You may only invert a node if it is “sufficiently far” from any other
# inverted node.
#
# If you invert two nodes a and b, the distance (the number of edges on
# the unique path between them) must be at least k.
#
# Return the maximum possible sum of the tree’s node values after applying
# inversion operations.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2],[0,3],[1,4],[1,5]], nums = [1,0,-10,3,4,5],
# k = 2
#
# Output: 23
#
# Explanation:
#
# After inverting the subtree rooted at node 2, the maximum sum becomes 1
# + 0 + 10 + 3 + 4 + 5 = 23.
#
# Example 2:
#
# Input: edges = [[0,1],[1,2]], nums = [5,-10,-10], k = 1
#
# Output: 25
#
# Explanation:
#
# After inverting the subtree rooted at node 1, the maximum sum becomes 5
# + 10 + 10 = 25.
#
# Example 3:
#
# Input: edges = [[0,1],[0,2]], nums = [1,-5,-6], k = 2
#
# Output: 12
#
# Explanation:
#
# After inverting the subtrees rooted at nodes 1 and 2, nums = [1, 5, 6].
#
# This is valid because nodes 1 and 2 are two edges apart (1 → 0 and 0 →
# 2), which is at least k.
#
# The maximum sum is 1 + 5 + 6 = 12.
#
# Example 4:
#
# Input: edges = [[0,1],[0,2]], nums = [1,-5,-6], k = 3
#
# Output: 10
#
# Explanation:
#
# After inverting the subtree rooted at nodes 0, nums = [-1, 5, 6].
#
# The maximum sum is (-1) + 5 + 6 = 10.
#
# Note that we cannot invert nodes 1 and 2 because their distance is 2 < k
# = 3.
#
# Constraints:
#
# nums.length == n
#
# edges.length == n - 1
#
# 2 <= n <= 5 * 10^4
#
# edges[i].length == 2
#
# 0 <= edges[i][0], edges[i][1] < n
#
# -4 * 10^4 <= nums[i] <= 4 * 10^4
#
# 1 <= k <= 50
#
# It is guaranteed that edges forms a tree.
#

# @lc code=start
from functools import lru_cache


class Solution:
    def subtreeInversionSum(self, edges: list[list[int]], nums: list[int], k: int) -> int:
        """
        Interview explanation:
        Invert subtrees (flip signs) so any two inverted nodes are ≥ k apart;
        maximize the signed sum. Sibling inversions also interact through the LCA.

        Algorithm:
        - Profile DP: for each subtree return best sums keyed by distance from
          the root to the nearest inversion (or none).
        - Invert root of subtree when allowed; else merge child profiles with
          pairwise distance checks (d1+d2 ≥ k).

        Complexity: O(n · k²) time, O(n · k) space.
        """
        n = len(nums)
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        children = [[] for _ in range(n)]
        stack = [(0, -1)]
        while stack:
            u, p = stack.pop()
            for v in g[u]:
                if v != p:
                    children[u].append(v)
                    stack.append((v, u))

        NEG = -10**30

        @lru_cache(None)
        def profile(u: int, ban: int, sign: int) -> tuple:
            res = [NEG] * (k + 2)
            if ban == 0:
                total = -sign * nums[u]
                for v in children[u]:
                    total += max(profile(v, k - 1, -sign))
                res[0] = total
            ch_profs = [profile(v, max(0, ban - 1), sign) for v in children[u]]
            if not ch_profs:
                res[k + 1] = max(res[k + 1], sign * nums[u])
            else:
                cur = {k + 1: sign * nums[u]}
                for prof in ch_profs:
                    nxt = {}
                    for d_ch, add in enumerate(prof):
                        if add <= NEG // 2:
                            continue
                        for m, s in cur.items():
                            if d_ch == k + 1:
                                nxt[m] = max(nxt.get(m, NEG), s + add)
                            else:
                                dist_u = d_ch + 1
                                if m == k + 1:
                                    nxt[dist_u] = max(nxt.get(dist_u, NEG), s + add)
                                elif dist_u + m >= k:
                                    nm = min(m, dist_u)
                                    nxt[nm] = max(nxt.get(nm, NEG), s + add)
                    cur = nxt
                for m, s in cur.items():
                    if m == k + 1:
                        res[k + 1] = max(res[k + 1], s)
                    elif 1 <= m <= k:
                        res[m] = max(res[m], s)
            return tuple(res)

        return max(profile(0, 0, 1))
# @lc code=end
