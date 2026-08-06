#
# @lc app=leetcode id=2709 lang=python3
#
# [2709] Greatest Common Divisor Traversal
#

# --- Interview notes (graph model, DSU on primes, complexity, edges, tests) ---
#
# Problem
# Indices i and j are adjacent iff gcd(nums[i], nums[j]) > 1. Determine whether the graph on
# {0..n-1} is connected (every pair reachable by a path).
#
# Why not build edges between all pairs
# n up to 1e5 — O(n^2) edges is impossible. gcd(a,b)>1 iff a and b share a prime factor. So connectivity
# is determined by shared primes — we only need to link numbers that share at least one prime.
#
# Graph reformulation (standard trick)
# Build a bipartite-style union structure:
#   - Left side: index nodes 0 .. n-1.
#   - Right side: one node per possible prime p ∈ [2, max(nums)] (IDs we’ll offset by n).
# Connect index i with every prime p that divides nums[i]. Then two indices share a prime p iff both are
# attached to the same prime node p, hence they lie in the same connected component of this union graph.
# Formally: index i is merged with node (n + p) for each prime p | nums[i]. Transitive closure of unions
# equals connectivity of the original gcd graph.
#
# Prime factors per value
# Precompute distinct prime factors for each x in [1, MX] using trial division up to √x (MX = 1e5 per
# constraints). nums[i] == 1 has no prime factors → that index gets no edges via primes (isolated unless n
# is 1).
#
# Data structures
# - Disjoint Set Union (Union-Find) with path compression + union by size: nearly O(α(N)) per op.
# - Static table `PF[x]` = list of distinct primes dividing x.
#
# Algorithm
# 1. If len(nums) == 1: return True (single vertex is trivially “connected”).
# 2. Let m = max(nums); allocate DSU of size n + m + 1 (index nodes 0..n-1, prime p uses node id n+p).
# 3. For each i, for each prime p in PF[nums[i]], union(i, n + p).
# 4. Return True iff all indices 0..n-1 share one root (e.g. find(0) == find(i) for all i, or count roots).
#
# Time complexity
# - Precompute PF once: O(MX · √MX) ≈ O(MX^1.5) trial division; acceptable for MX = 1e5 at startup / once.
# - Per query / each call: O(n · ω(nums[i])) unions where ω is number of distinct prime factors (small),
#   plus DSU α inverse ackermann — dominated by precompute + O(n log MAX) loose bound.
# Space: O(MX) for PF table + O(n + m) for DSU.
#
# Edge cases
# - nums = [1]: True (one node).
# - nums contains 1 with other values > 1: index with value 1 never unions with primes → cannot leave that
#   component unless n == 1 → typically False (except edge cases where graph still connects via others — but 1
#   shares gcd 1 with everyone, so no edges from that index).
# - nums = [1, 1]: gcd(1,1)=1 → no edge → False.
# - All nums share a prime through a chain (Example 1): DSU merges into one component.
#
# Tests (statement)
# [2,3,6] → True; [3,9,5] → False; [4,3,12,8] → True.
#
# Improvements
# - Linear sieve + smallest prime factor (SPF) array yields faster factorization per nums[i] if many queries.
# - Could lazy-init PF table only if Solution called multiple times — LeetCode calls once per instance.
#
# --- end notes ---

# @lc code=start
from typing import List

_MX = 100_001


def _build_distinct_prime_factors(mx: int) -> List[List[int]]:
    pf: List[List[int]] = [[] for _ in range(mx)]
    for x in range(2, mx):
        v = x
        d = 2
        while d * d <= v:
            if v % d == 0:
                pf[x].append(d)
                while v % d == 0:
                    v //= d
            d += 1
        if v > 1:
            pf[x].append(v)
    return pf


_PF = _build_distinct_prime_factors(_MX)


class _UnionFind:
    __slots__ = ("p", "sz")

    def __init__(self, n: int) -> None:
        """
        Interview explanation:
        Disjoint-set helper for indices and prime nodes.

        Algorithm:
        - Parent and size arrays of length n.

        Complexity: O(n) init.
        """
        self.p = list(range(n))
        self.sz = [1] * n

    def find(self, x: int) -> int:
        """
        Interview explanation:
        Find root with path compression.

        Algorithm:
        - Recursively set parent to root.

        Complexity: Amortized α(n).
        """
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])
        return self.p[x]

    def union(self, a: int, b: int) -> None:
        """
        Interview explanation:
        Union by size.

        Algorithm:
        - Link smaller tree under larger.

        Complexity: Amortized α(n).
        """
        pa, pb = self.find(a), self.find(b)
        if pa == pb:
            return
        if self.sz[pa] < self.sz[pb]:
            pa, pb = pb, pa
        self.p[pb] = pa
        self.sz[pa] += self.sz[pb]


class Solution:
    def canTraverseAllPairs(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Indices are adjacent iff gcd > 1. Decide if the index graph is connected.

        Algorithm:
        - Union each index with nodes for its prime factors (offset by n); check
          all indices share one DSU root. Value 1 has no primes (isolated).

        Complexity: O(MX^1.5) precompute + O(n * ω) unions; O(MX + n) space.
        """
        n = len(nums)
        if n == 1:
            return True
        m = max(nums)
        uf = _UnionFind(n + m + 1)
        for i, x in enumerate(nums):
            for p in _PF[x]:
                uf.union(i, n + p)
        root0 = uf.find(0)
        return all(uf.find(i) == root0 for i in range(1, n))

    def canTraverseAllPairs_uf(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate UF naming for the prime-factor union approach.

        Algorithm:
        - Same DSU on indices + prime nodes.

        Complexity: O(MX^1.5 + n ω) time, O(MX + n) space.
        """
        return self.canTraverseAllPairs(nums)
# @lc code=end
