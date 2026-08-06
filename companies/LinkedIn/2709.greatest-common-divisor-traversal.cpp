/*
 * @lc app=leetcode id=2709 lang=cpp
 *
 * [2709] Greatest Common Divisor Traversal
 */
// Translated from 2709.greatest-common-divisor-traversal.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2709 lang=python3
// #
// # [2709] Greatest Common Divisor Traversal
// #
// 
// # --- Interview notes (graph model, DSU on primes, complexity, edges, tests) ---
// #
// # Problem
// # Indices i and j are adjacent iff gcd(nums[i], nums[j]) > 1. Determine whether the graph on
// # {0..n-1} is connected (every pair reachable by a path).
// #
// # Why not build edges between all pairs
// # n up to 1e5 — O(n^2) edges is impossible. gcd(a,b)>1 iff a and b share a prime factor. So connectivity
// # is determined by shared primes — we only need to link numbers that share at least one prime.
// #
// # Graph reformulation (standard trick)
// # Build a bipartite-style union structure:
// #   - Left side: index nodes 0 .. n-1.
// #   - Right side: one node per possible prime p ∈ [2, max(nums)] (IDs we’ll offset by n).
// # Connect index i with every prime p that divides nums[i]. Then two indices share a prime p iff both are
// # attached to the same prime node p, hence they lie in the same connected component of this union graph.
// # Formally: index i is merged with node (n + p) for each prime p | nums[i]. Transitive closure of unions
// # equals connectivity of the original gcd graph.
// #
// # Prime factors per value
// # Precompute distinct prime factors for each x in [1, MX] using trial division up to √x (MX = 1e5 per
// # constraints). nums[i] == 1 has no prime factors → that index gets no edges via primes (isolated unless n
// # is 1).
// #
// # Data structures
// # - Disjoint Set Union (Union-Find) with path compression + union by size: nearly O(α(N)) per op.
// # - Static table `PF[x]` = list of distinct primes dividing x.
// #
// # Algorithm
// # 1. If len(nums) == 1: return True (single vertex is trivially “connected”).
// # 2. Let m = max(nums); allocate DSU of size n + m + 1 (index nodes 0..n-1, prime p uses node id n+p).
// # 3. For each i, for each prime p in PF[nums[i]], union(i, n + p).
// # 4. Return True iff all indices 0..n-1 share one root (e.g. find(0) == find(i) for all i, or count roots).
// #
// # Time complexity
// # - Precompute PF once: O(MX · √MX) ≈ O(MX^1.5) trial division; acceptable for MX = 1e5 at startup / once.
// # - Per query / each call: O(n · ω(nums[i])) unions where ω is number of distinct prime factors (small),
// #   plus DSU α inverse ackermann — dominated by precompute + O(n log MAX) loose bound.
// # Space: O(MX) for PF table + O(n + m) for DSU.
// #
// # Edge cases
// # - nums = [1]: True (one node).
// # - nums contains 1 with other values > 1: index with value 1 never unions with primes → cannot leave that
// #   component unless n == 1 → typically False (except edge cases where graph still connects via others — but 1
// #   shares gcd 1 with everyone, so no edges from that index).
// # - nums = [1, 1]: gcd(1,1)=1 → no edge → False.
// # - All nums share a prime through a chain (Example 1): DSU merges into one component.
// #
// # Tests (statement)
// # [2,3,6] → True; [3,9,5] → False; [4,3,12,8] → True.
// #
// # Improvements
// # - Linear sieve + smallest prime factor (SPF) array yields faster factorization per nums[i] if many queries.
// # - Could lazy-init PF table only if Solution called multiple times — LeetCode calls once per instance.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from typing import List
// 
// _MX = 100_001  # nums[i] <= 10^5
// 
// 
// def _build_distinct_prime_factors(mx: int) -> List[List[int]]:
//     pf: List[List[int]] = [[] for _ in range(mx)]
//     for x in range(2, mx):
//         v = x
//         d = 2
//         while d * d <= v:
//             if v % d == 0:
//                 pf[x].append(d)
//                 while v % d == 0:
//                     v //= d
//             d += 1
//         if v > 1:
//             pf[x].append(v)
//     return pf
// 
// 
// _PF = _build_distinct_prime_factors(_MX)
// 
// 
// class Solution:
//     def canTraverseAllPairs(self, nums: List[int]) -> bool:
//         n = len(nums)
//         if n == 1:
//             return True
// 
//         m = max(nums)
//         uf = _UnionFind(n + m + 1)
// 
//         for i, x in enumerate(nums):
//             for p in _PF[x]:
//                 uf.union(i, n + p)
// 
//         root0 = uf.find(0)
//         for i in range(1, n):
//             if uf.find(i) != root0:
//                 return False
//         return True
// 
// 
// class _UnionFind:
//     __slots__ = ("p", "sz")
// 
//     def __init__(self, n: int) -> None:
//         self.p = list(range(n))
//         self.sz = [1] * n
// 
//     def find(self, x: int) -> int:
//         if self.p[x] != x:
//             self.p[x] = self.find(self.p[x])
//         return self.p[x]
// 
//     def union(self, a: int, b: int) -> None:
//         pa, pb = self.find(a), self.find(b)
//         if pa == pb:
//             return
//         if self.sz[pa] < self.sz[pb]:
//             pa, pb = pb, pa
//         self.p[pb] = pa
//         self.sz[pa] += self.sz[pb]
// 
// 
// # lc-original code=end

// @lc code=start
#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class DSU {
    vector<int> parent, sz;
public:
    DSU(int n) : parent(n), sz(n, 1) { iota(parent.begin(), parent.end(), 0); }
    int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
    void unite(int a, int b) {
        int pa = find(a), pb = find(b);
        if (pa == pb) return;
        if (sz[pa] < sz[pb]) swap(pa, pb);
        parent[pb] = pa;
        sz[pa] += sz[pb];
    }
};

class Solution {
    vector<int> factors(int x) {
        vector<int> out;
        for (int d = 2; (long long)d * d <= x; ++d) {
            if (x % d == 0) {
                out.push_back(d);
                while (x % d == 0) x /= d;
            }
        }
        if (x > 1) out.push_back(x);
        return out;
    }

public:
    bool canTraverseAllPairs(vector<int>& nums) {
        int n = nums.size();
        if (n == 1) return true;
        int m = *max_element(nums.begin(), nums.end());
        DSU dsu(n + m + 1);
        for (int i = 0; i < n; ++i) for (int p : factors(nums[i])) dsu.unite(i, n + p);
        int root = dsu.find(0);
        for (int i = 1; i < n; ++i) if (dsu.find(i) != root) return false;
        return true;
    }
};
// @lc code=end
