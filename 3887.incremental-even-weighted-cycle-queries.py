#
# @lc app=leetcode id=3887 lang=python3
#
# [3887] Incremental Even-Weighted Cycle Queries
#
# --- Notes (problem restatement, parity / GF(2), DSU with XOR, complexity, interview) ---
#
# Problem restatement
# n nodes 0..n-1, initially no edges. Process edges in order: edges[i] = [u, v, w] with
# w in {0, 1}. Add the edge ONLY IF after adding it, EVERY cycle in the graph has EVEN
# total edge-weight sum (sum of w over edges in the cycle is divisible by 2).
# Return how many edges were successfully added.
#
# Why XOR / parity DSU
# For weights in {0, 1}, the sum of weights along any closed walk equals (XOR of edge
# weights along that walk) modulo 2 — because addition mod 2 is XOR for bits.
# "Every cycle has even weight" <=> every cycle has XOR sum 0 (in GF(2)).
#
# Equivalent formulation (potential / bipartite parity)
# Assign each vertex a label b[v] in {0, 1}. For an edge (u, v, w), feasibility requires
# b[u] XOR b[v] = w for ALL edges that remain (consistent labeling). That is exactly the
# constraint system solvable by union-find with XOR-to-parent: maintain XOR distance from
# each node to its DSU root along the spanning forest being built.
#
# Incremental rule for edge (u, v, w)
# Let xor[u] = XOR sum from u to its DSU root after find() with path compression (stored
# cumulatively on the compressed path).
# - If u and v are in DIFFERENT components: merge roots; pick XOR on the new tree edge so
#   the implied XOR along u-v equals w. Standard merge:
#     parent[ru] = rv
#     xor_edge[ru] = xor[u] XOR xor[v] XOR w
#   (ru is the root of u's component before union.)
# - If u and v are in the SAME component: adding (u,v,w) closes a UNIQUE cycle (in the
#   subgraph). Cycle XOR = xor[u] XOR xor[v] XOR w (path u->root + root->v plus new edge).
#   Need xor[u] XOR xor[v] XOR w == 0  <=>  xor[u] XOR xor[v] == w.
#   If equality fails, the new cycle would have odd total weight -> reject edge.
#
# Data structure: Disjoint Set Union (DSU) with XOR parity
# Arrays:
#   p[x]  : parent of x in DSU tree
#   xw[x] : XOR sum from x to p[x] on the DSU tree (before compression it is just w(x,p[x]))
# find(x) with path compression updates xw[x] so after find, xw[x] is XOR from x to root.
#
# Why not plain DSU
# Plain connectivity ignores weights; we must enforce linear equations mod 2 along edges.
#
# Time complexity
# Nearly O(|E| * alpha(n)) where alpha is inverse Ackermann; per edge find/union amortized
# constant for practical sizes. |E| <= 5e4, n <= 5e4 -> fine.
#
# Space complexity
# O(n) for parent and xor arrays.
#
# Edge cases
# - First edges always merge until we start forming cycles.
# - Self-loops not in constraints (u < v given).
# - All edges distinct (statement).
#
# Tests (examples)
# Triangle with third edge w=1: path XOR 0->2 equals 1 XOR 1 = 0; need third == 0 -> fail.
# Third edge w=0: 0 XOR 0 == 0 -> ok.
#
# Possible improvements
# - Union by rank/size keeps trees shallow (same alpha bound); optional micro-optimization.
# - Iterative find if recursion depth worries (n <= 5e4 recursion usually OK in Python with
#   increased limit not needed for shallow trees).
#
# Interview walkthrough
# 1) Restate condition as XOR-consistency / even cycle sums mod 2.
# 2) DSU with parity; same-comp check xor[u]^xor[v]==w; merge with xor on root edge.
# 3) Complexity nearly linear.
# --- end notes ---

# @lc code=start
class DSU:
    """Disjoint-set union with XOR parity to root (GF(2) potentials)."""

    __slots__ = ("p", "xw")

    def __init__(self, n: int):
        self.p = list(range(n))
        self.xw = [0] * n

    def find(self, a: int) -> int:
        if self.p[a] != a:
            orig = self.p[a]
            root = self.find(orig)
            self.xw[a] ^= self.xw[orig]
            self.p[a] = root
        return self.p[a]

    def union(self, u: int, v: int, w: int) -> bool:
        pu, pv = self.find(u), self.find(v)
        xu, xv = self.xw[u], self.xw[v]
        if pu == pv:
            return (xu ^ xv) == w
        self.p[pu] = pv
        self.xw[pu] = xu ^ xv ^ w
        return True


class Solution:
    def numberOfEdgesAdded(self, n: int, edges: list[list[int]]) -> int:
        dsu = DSU(n)
        ans = 0
        for u, v, w in edges:
            if dsu.union(u, v, w):
                ans += 1
        return ans


# @lc code=end
