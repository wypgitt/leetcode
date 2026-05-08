// Translated from 3873.maximum-points-activated-with-one-addition.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3873 lang=python3
// #
// # [3873] Maximum Points Activated With One Addition
// #
// 
// # @lc code=start
// class Solution:
//     pass
// 
// 
// # @lc code=end
// 
// #
// # @lc app=leetcode id=3873 lang=python3
// #
// # [3873] Maximum Points Activated with One Addition
// #
// # --- Notes (problem restatement, bipartite graph + DSU, formula, complexity, interview) ---
// #
// # Problem restatement
// # Distinct integer lattice points. Activating a point activates every point sharing its x OR its
// # y coordinate; activation spreads until closure (same row/column connectivity).
// # You may place ONE extra point at any integer (x, y) NOT already in the set. Activation STARTS
// # from this new point. Maximize how many points end up activated (including the new one).
// #
// # Graph model (why union-find)
// # Build a bipartite graph: left nodes = x-values that appear, right nodes = y-values (encoded
// # distinctly). Each input point (x, y) is an edge between node x and node y.
// # Two points lie in the same activation component iff they are connected in this graph (same
// # row/column closure equals connectivity in the bipartite graph built from existing edges).
// #
// # Encoding x and y in one DSU
// # Map each y to y + M for a large constant M so x and y never collide as DSU keys (e.g.
// # M = 3_000_000_000 > coordinate range magnitude per constraints).
// # For each point (x, y): union(x, y + M).
// #
// # Effect of adding one new point (a, b)
// # It adds one new edge between representative of a and representative of b + M. If those were in
// # two different connected components, those components MERGE in the bipartite graph — activation
// # can then spread across both. The maximum achievable size is: pick two disjoint components with
// # sizes A and B (before adding), connect them with the new edge; activated points =
// # A + B + 1 (the +1 is the newly placed point). Greedy optimum uses the two largest components.
// #
// # Answer formula
// # Let component sizes by DSU root (count each original point once via root of its x-node):
// #   answer = (largest size) + (second largest size) + 1
// # If only one nonempty component exists, second largest is 0 -> n + 1 (still place one point).
// #
// # Counting points per component
// # After unions, for each point increment cnt[find(x)] using its x coordinate’s root (same as
// # counting points attached to that bipartite component).
// #
// # Time complexity
// # O(n * alpha(n)) for unions and finds; counting O(n); scanning two largest O(#roots) <= O(n).
// #
// # Space complexity
// # O(n) for DSU maps / arrays in practice (distinct nodes touched).
// #
// # Edge cases
// # - Single point: one component size 1 -> 1 + 0 + 1 = 2.
// # - All points already one component: mx2 = 0 -> n + 1.
// #
// # Tests (examples)
// # Provided examples yield 4, 3, 4 respectively with this construction.
// #
// # Possible improvements
// # - Coordinate compression + array DSU if bounds small (here coordinates sparse/huge — dict DSU
// #   matches editorial).
// # --- end notes ---
// 
// # @lc code=start
// from collections import Counter
// 
// 
// class UnionFind:
//     """Disjoint-set union with dynamic keys (coordinates / shifted y)."""
// 
//     __slots__ = ("p", "size")
// 
//     def __init__(self):
//         self.p: dict[int, int] = {}
//         self.size: dict[int, int] = {}
// 
//     def find(self, x: int) -> int:
//         if x not in self.p:
//             self.p[x] = x
//             self.size[x] = 1
//         if self.p[x] != x:
//             self.p[x] = self.find(self.p[x])
//         return self.p[x]
// 
//     def union(self, a: int, b: int) -> bool:
//         pa, pb = self.find(a), self.find(b)
//         if pa == pb:
//             return False
//         if self.size[pa] > self.size[pb]:
//             self.p[pb] = pa
//             self.size[pa] += self.size[pb]
//         else:
//             self.p[pa] = pb
//             self.size[pb] += self.size[pa]
//         return True
// 
// 
// class Solution:
//     def maxActivated(self, points: list[list[int]]) -> int:
//         uf = UnionFind()
//         m = 3_000_000_000
// 
//         for x, y in points:
//             uf.union(x, y + m)
// 
//         cnt = Counter()
//         for x, _ in points:
//             cnt[uf.find(x)] += 1
// 
//         mx1 = mx2 = 0
//         for v in cnt.values():
//             if mx1 < v:
//                 mx2 = mx1
//                 mx1 = v
//             elif mx2 < v:
//                 mx2 = v
// 
//         return mx1 + mx2 + 1
// 
// 
// # @lc code=end

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

class UnionFind {
public:
    unordered_map<long long, long long> parent, sz;
    long long find(long long x) {
        if (!parent.count(x)) {
            parent[x] = x;
            sz[x] = 1;
        }
        return parent[x] == x ? x : parent[x] = find(parent[x]);
    }
    void unite(long long a, long long b) {
        long long pa = find(a), pb = find(b);
        if (pa == pb) return;
        if (sz[pa] > sz[pb]) {
            parent[pb] = pa;
            sz[pa] += sz[pb];
        } else {
            parent[pa] = pb;
            sz[pb] += sz[pa];
        }
    }
};

class Solution {
public:
    int maxActivated(vector<vector<int>>& points) {
        UnionFind uf;
        const long long M = 3000000000LL;
        for (auto& p : points) uf.unite(p[0], p[1] + M);
        unordered_map<long long, int> cnt;
        for (auto& p : points) ++cnt[uf.find(p[0])];
        int mx1 = 0, mx2 = 0;
        for (auto [_, v] : cnt) {
            if (mx1 < v) mx2 = mx1, mx1 = v;
            else if (mx2 < v) mx2 = v;
        }
        return mx1 + mx2 + 1;
    }
};
