#
# @lc app=leetcode id=3973 lang=python3
#
# [3973] Distinct Gate Paths to LCA
#
# https://leetcode.com/problems/distinct-gate-paths-to-lca/description/
#
# algorithms
# Hard (58.04%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    213
# Total Submissions: 367
# Testcase Example:  "3\n[-1,0,0]\n[[1,0,1],[0,1,1],[1,1,0]]\n[[1,0,2,0],[1,1,2,0],[1,0,2,1]]"
#
#
# You are given an undirected tree rooted at node 0 with n nodes numbered
# from 0 to n - 1, represented by an array parent where parent[i] is the
# parent of node i.
#
# Each node i has three types of gates, given in a 2D array gates where
# gates[i] = [red_i, blue_i, white_i] which represents the number of red,
# blue, and white gates at node i.
#
# Red gate: usable only with a red card.
#
# Blue gate: usable only with a blue card.
#
# White gate: usable with either card, but flips the card color when used.
#
# Alice and Bob start at given nodes with either a red or blue card (1 =
# red, 0 = blue). They must independently move upward to their lowest
# common ancestor (LCA).
#
# At each node, a person may move to their parent only if they can use at
# least one gate at that node with their current card. White gates may be
# used any number of times to flip the card color.
#
# Movement rules (one move = from u to parent[u]):
#
# Movement is only upward toward the root.
#
# At node u, pick exactly one specific gate instance. Identical gates are
# treated as separate and counted individually.
#
# If holding a red card: use a red gate to remain red, or a white gate to
# change to blue.
#
# If holding a blue card: use a blue gate to remain blue, or a white gate
# to change to red.
#
# If no usable gate exists at u, the sequence ends.
#
# You are also given a 2D array queries where queries[i] = [aNode_i,
# aCard_i, bNode_i, bCard_i]:
#
# aNode_i, aCard_i: Alice's starting node and card.
#
# bNode_i, bCard_i: Bob's starting node and card.
#
# For each query, count the number of distinct valid ways modulo 10^9 + 7
# for both to reach their LCA.
#
# After computing the result for all queries, return the bitwise XOR of
# those values.
#
# Note:
#
# Two ways are distinct if the set of gates used differs for either Alice
# or Bob.
#
# If any person is already at the LCA, then the number of ways for them is
# 1.
#
# The lowest common ancestor (LCA) is defined between two nodes a and b as
# the lowest node in a tree that has both a and b as descendants (where a
# node is allowed to be a descendant of itself).
#
# Example 1:
#
# Input: n = 3, parent = [-1,0,0], gates = [[1,0,1],[0,1,1],[1,1,0]],
# queries = [[1,0,2,0],[1,1,2,0],[1,0,2,1]]
#
# Output: 1
#
# Explanation:
#
#                         i
#                         Alice
#
#                         [Node, Card]
#                         Bob
#
#                         [Node, Card]
#                         LCA
#                         Alice
#
#                         Path
#                         Bob
#
#                         Path
#                         Alice Ways
#                         Bob Ways
#                         Total Ways
#
#                         0
#                         [1, 0]: Blue
#                         [2, 0]: Blue
#                         0
#                         1 → 0
#                         2 → 0
#                         2 (1 Blue + 1 White at node 1)
#                         1 (1 Blue at node 2)
#                         2 × 1 = 2
#
#                         1
#                         [1, 1]: Red
#                         [2, 0]: Blue
#                         0
#                         1 → 0
#                         2 → 0
#                         1 (1 White at node 1)
#                         1 (1 Blue at node 2)
#                         1 × 1 = 1
#
#                         2
#                         [1, 0]: Blue
#                         [2, 1]: Red
#                         0
#                         1 → 0
#                         2 → 0
#                         2 (1 Blue + 1 White at node 1)
#                         1 (1 Red at node 2)
#                         2 × 1 = 2
#
# Thus, the XOR of all values: 2 XOR 1 XOR 2 = 1.
#
# Example 2:
#
# Input: n = 3, parent = [-1,0,1], gates = [[0,1,2],[1,0,1],[0,0,3]],
# queries = [[2,0,1,0],[2,1,0,0],[1,1,2,1]]
#
# Output: 3
#
# Explanation:
#
#                         i
#                         Alice
#
#                         [Node, Card]
#                         Bob
#
#                         [Node, Card]
#                         LCA
#                         Alice Path
#                         Bob Path
#                         Alice Ways
#                         Bob Ways
#                         Total Ways
#
#                         0
#                         [2, 0]: Blue
#                         [1, 0]: Blue
#                         1
#                         2 → 1
#                         1
#                         3 (3 White at node 2)
#                         1 (no move)
#                         3 × 1 = 3
#
#                         1
#                         [2, 1]: Red
#                         [0, 0]: Blue
#                         0
#                         2 → 1 → 0
#                         0
#                         3 (3 White at node 2) × 1 (1 White at node 1) =
# 3
#                         1 (no move)
#                         3 × 1 = 3
#
#                         2
#                         [1, 1]: Red
#                         [2, 1]: Red
#                         1
#                         1
#                         2 → 1
#                         1 (no move)
#                         3 (3 White at node 2)
#                         1 × 3 = 3
#
# Thus, the XOR of all values: 3 XOR 3 XOR 3 = 3.
#
# Constraints:​​​​​​​
#
# 2 <= n <= 2 * 10^4
#
# n == parent.length == gates.length
#
# parent[0] == -1
#
# 0 <= parent[i] < n for i in [1, n - 1]
#
# gates[i] == [red_i, blue_i, white_i]
#
# 0 <= red_i, blue_i, white_i <= 10
#
# 1 <= queries.length <= 2 * 10^4
#
# queries[i] = [aNode_i, aCard_i, bNode_i, bCard_i]
#
# 0 <= aNode_i, bNode_i <= n - 1
#
# 0 <= aCard_i, bCard_i <= 1
#
# The input is generated such that the array parent represents a valid
# tree.
#

# @lc code=start

class Solution:
    def distinctPaths(
        self, n: int, parent: list[int], gates: list[list[int]], queries: list[list[int]]
    ) -> int:
        """
        Interview explanation:
        Leaving a node with a card color chooses a matching gate and may flip on
        white. Path counts compose as 2x2 matrices; Alice/Bob ways multiply at LCA.

        Algorithm:
        - Gate matrix M[from][to] at each node from (red, blue, white) counts.
        - Binary lifting: ancestors and matrix products for 2^k upward steps.
        - For each query, LCA via lifting; ways(node->LCA) = sum of vector*matrices.
        - XOR all (alice_ways * bob_ways) mod 10^9+7.

        Complexity: O((n + q) log n) time, O(n log n) space.
        """
        MOD = 10**9 + 7
        LOG = max(1, n.bit_length() + 1)
        depth = [0] * n
        up = [[0] * n for _ in range(LOG)]
        children = [[] for _ in range(n)]
        for i in range(1, n):
            children[parent[i]].append(i)
            up[0][i] = parent[i]
        up[0][0] = 0

        def mat_mul(A, B):
            return [
                [
                    (A[0][0] * B[0][0] + A[0][1] * B[1][0]) % MOD,
                    (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % MOD,
                ],
                [
                    (A[1][0] * B[0][0] + A[1][1] * B[1][0]) % MOD,
                    (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % MOD,
                ],
            ]

        def gate_mat(u: int):
            r, b, w = gates[u]
            return [[b % MOD, w % MOD], [w % MOD, r % MOD]]

        mat_jump = [[gate_mat(u) for u in range(n)] for _ in range(LOG)]
        stack = [0]
        while stack:
            u = stack.pop()
            for v in children[u]:
                depth[v] = depth[u] + 1
                stack.append(v)
        for k in range(1, LOG):
            for u in range(n):
                mid = up[k - 1][u]
                up[k][u] = up[k - 1][mid]
                mat_jump[k][u] = mat_mul(mat_jump[k - 1][u], mat_jump[k - 1][mid])

        def lift_ways(u: int, steps: int, card: int) -> int:
            vec = [0, 0]
            vec[card] = 1
            for k in range(LOG):
                if steps >> k & 1:
                    M = mat_jump[k][u]
                    nv = [0, 0]
                    for f in range(2):
                        for t in range(2):
                            nv[t] = (nv[t] + vec[f] * M[f][t]) % MOD
                    vec = nv
                    u = up[k][u]
            return sum(vec) % MOD

        def lca(a: int, b: int) -> int:
            if depth[a] < depth[b]:
                a, b = b, a
            diff = depth[a] - depth[b]
            for k in range(LOG):
                if diff >> k & 1:
                    a = up[k][a]
            if a == b:
                return a
            for k in range(LOG - 1, -1, -1):
                if up[k][a] != up[k][b]:
                    a = up[k][a]
                    b = up[k][b]
            return parent[a]

        def ways_to_lca(node: int, card: int, anc: int) -> int:
            steps = depth[node] - depth[anc]
            if steps == 0:
                return 1
            return lift_ways(node, steps, card)

        xor = 0
        for a_node, a_card, b_node, b_card in queries:
            anc = lca(a_node, b_node)
            wa = ways_to_lca(a_node, a_card, anc)
            wb = ways_to_lca(b_node, b_card, anc)
            xor ^= (wa * wb) % MOD
        return xor
# @lc code=end
