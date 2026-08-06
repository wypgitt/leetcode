/*
 * @lc app=leetcode id=2612 lang=cpp
 *
 * [2612] Minimum Reverse Operations
 */
// Translated from 2612.minimum-reverse-operations.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2612 lang=python3
// #
// # [2612] Minimum Reverse Operations
// #
// # --- Notes (problem, graph model, parity / interval, DSU skip, BFS, complexity, edges, interview) ---
// #
// # Problem restatement
// # Length-n binary array (indices 0..n-1). Exactly one position `p` is 1; all others 0.
// # One operation: choose any contiguous subarray of length exactly `k` and reverse it (the single 1
// # moves with its element). After each operation, the 1 must NOT lie on any index in `banned`.
// # For every index `i`, compute the minimum number of operations to have the 1 at `i`, or -1 if
// # impossible. Return an array of length n (answer[p] is always 0).
// #
// # Graph modeling
// # Positions 0..n-1 are states. An undirected edge connects u and v if one reverse of length k can
// # send the 1 from u to v in one step (and v to u), while the landing position is not banned.
// # All edges have weight 1 -> shortest path = minimum operations -> BFS from source `p`.
// #
// # Neighbor formula (reverse window [l, l+k-1] containing u)
// # After reversing, index u maps to v = l + (l+k-1) - u = 2l + k - 1 - u.
// # For fixed u and k, as l runs over integers such that 0 <= l <= n-k and l <= u <= l+k-1,
// # we get l in [max(0,u-k+1), min(u, n-k)], and v = 2l + k - 1 - u steps by 2 when l increases by 1.
// # So from u you can reach a contiguous range of candidate indices [L, R] that share the same
// # parity pattern (step size 2 in index space).
// #
// # Reachable interval endpoints (equivalent forms appear in editorials)
// # With walkccc / kamyu notation:
// #   L = max(u - k + 1, k - 1 - u)
// #   R = min(u + k - 1, n - 1 - (u - (n - k)))
// # Any valid destination index v in one move lies in [L, R] with v ≡ L (mod 2).
// #
// # Why not naive BFS?
// # A single u may have Theta(k) neighbors; dense edges make O(n*k) BFS too slow for large n.
// # All neighbors in one move form an arithmetic progression with step 2 inside [L,R]. We must
// # enumerate unvisited positions in that range quickly — either:
// #   (A) Two ordered sets keyed by parity -> bisect/range delete -> O(log n) per operation, or
// #   (B) Disjoint-set “union with next index” + jump pointers -> amortized near O(1) per position.
// #
// # Algorithm implemented — BFS + Union-Find skip (kamyu / editorial O(n α(n)))
// # Maintain DSU over indices 0..n+1 with auxiliary array `right` merged on union:
// #   Initially right[i] = i. Idea: indices with same parity link by union(i, i+2); after visiting
// #   index x we union(x, x+2) so future iterations skip over filled positions along that parity chain.
// # When expanding BFS layer from u:
// #   Compute [L, R] for one-step reachable indices (same parity as L).
// #   Let x = find_first_available(L) implemented as uf.right_set(L) (depends on DSU state).
// #   While x <= R: relax x (if not banned, set answer and push to next layer); ALWAYS union(x, x+2)
// #   to remove x from future scans; then x <- uf.right_set(x).
// # Start: union(p, p+2) once so the starting slot is skipped like visited along its parity chain.
// #
// # Banned indices
// # Never enqueue them as destinations; still union past them when scanning so we do not stall on
// # forbidden cells (kamyu always unions each x encountered in [L,R], but only pushes when not banned).
// #
// # Time complexity
// # - Each index is processed / skipped at most once per parity chain logic -> O(n α(n)) DSU work
// #   plus O(n) BFS layers overall -> ~O(n α(n)) ≈ O(n) practically.
// #
// # Space complexity
// # - O(n) for DSU parent/rank/right, answer array, banned flags, queue.
// #
// # Alternative
// # - SortedList / TreeSet per parity: O(n log n), only standard library if you simulate with bisect
// #   on sorted arrays is O(n) per delete worst case — not ideal; DSU skip is the LC-friendly choice.
// #
// # Edge cases
// # - k == n: only full-array reverses; limited neighbors.
// # - banned contains almost all indices: many -1 entries.
// # - p banned is impossible per constraints (usually p not in banned).
// #
// # LeetCode submission
// # Imports must be inside # lc-original code=start ... end (otherwise NameError on List at submit).
// #
// # Interview walkthrough
// # 1) Model positions as graph; unweighted shortest path -> BFS.
// # 2) Derive neighbor range [L,R] and step-2 structure from reverse formula.
// # 3) Accelerate range relaxation with DSU skip list or balanced sets.
// # 4) Complexity and parity bookkeeping.
// # --- end notes ---
// 
// # lc-original code=start
// from typing import List
// 
// 
// class _UnionFind:
//     """DSU with merged `right` jump — see header notes."""
// 
//     __slots__ = ("parent", "rank", "right")
// 
//     def __init__(self, n: int) -> None:
//         self.parent = list(range(n))
//         self.rank = [0] * n
//         self.right = list(range(n))
// 
//     def find(self, x: int) -> int:
//         stk = []
//         while self.parent[x] != x:
//             stk.append(x)
//             x = self.parent[x]
//         while stk:
//             self.parent[stk.pop()] = x
//         return x
// 
//     def union(self, x: int, y: int) -> bool:
//         px, py = self.find(x), self.find(y)
//         if px == py:
//             return False
//         if self.rank[px] > self.rank[py]:
//             px, py = py, px
//         self.parent[px] = py
//         if self.rank[px] == self.rank[py]:
//             self.rank[py] += 1
//         self.right[py] = max(self.right[px], self.right[py])
//         return True
// 
//     def right_set(self, x: int) -> int:
//         return self.right[self.find(x)]
// 
// 
// class Solution:
//     def minReverseOperations(self, n: int, p: int, banned: List[int], k: int) -> List[int]:
//         banned_on = [False] * n
//         for i in banned:
//             banned_on[i] = True
// 
//         ans = [-1] * n
//         ans[p] = 0
// 
//         uf = _UnionFind(n + 2)
//         uf.union(p, p + 2)
// 
//         q = [p]
//         step = 1
//         while q:
//             nxt: List[int] = []
//             for u in q:
//                 left = max(u - k + 1, k - 1 - u)
//                 right = min(u + k - 1, n - 1 - (u - (n - k)))
//                 x = uf.right_set(left)
//                 while x <= right:
//                     if not banned_on[x]:
//                         ans[x] = step
//                         nxt.append(x)
//                     uf.union(x, x + 2)
//                     x = uf.right_set(x)
//             q = nxt
//             step += 1
// 
//         return ans
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

class _UnionFind {
    vector<int> parent, rankv, rightmost;

public:
    _UnionFind(int n) : parent(n), rankv(n), rightmost(n) {
        iota(parent.begin(), parent.end(), 0);
        iota(rightmost.begin(), rightmost.end(), 0);
    }
    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }
    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rankv[px] > rankv[py]) swap(px, py);
        parent[px] = py;
        if (rankv[px] == rankv[py]) ++rankv[py];
        rightmost[py] = max(rightmost[px], rightmost[py]);
        return true;
    }
    int right_set(int x) { return rightmost[find(x)]; }
};

class Solution {
public:
    vector<int> minReverseOperations(int n, int p, vector<int>& banned, int k) {
        vector<int> bannedOn(n, 0), ans(n, -1);
        for (int x : banned) bannedOn[x] = 1;
        ans[p] = 0;
        _UnionFind uf(n + 2);
        uf.unite(p, p + 2);
        vector<int> q{p};
        for (int step = 1; !q.empty(); ++step) {
            vector<int> nxt;
            for (int u : q) {
                int left = max(u - k + 1, k - 1 - u);
                int right = min(u + k - 1, n - 1 - (u - (n - k)));
                int x = uf.right_set(left);
                while (x <= right) {
                    if (!bannedOn[x]) {
                        ans[x] = step;
                        nxt.push_back(x);
                    }
                    uf.unite(x, x + 2);
                    x = uf.right_set(x);
                }
            }
            q.swap(nxt);
        }
        return ans;
    }
};
// @lc code=end
