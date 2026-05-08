/*
 * @lc app=leetcode id=3910 lang=cpp
 *
 * [3910] Count Connected Subgraphs With Even Node Sum
 */
// Translated from 3910.count-connected-subgraphs-with-even-node-sum.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3910 lang=python3
// #
// # [3910] Count Connected Subgraphs With Even Node Sum
// #
// 
// # lc-original code=start
// class Solution:
//     pass
// 
// 
// # lc-original code=end
// 
// #
// # lc-original app=leetcode id=3910 lang=python3
// #
// # [3910] Count Connected Subgraphs with Even Node Sum
// #
// # --- Notes (problem restatement, algorithm, proof sketch, complexity, interview) ---
// #
// # Problem restatement
// # Undirected graph on nodes 0..n-1; nums[i] is 0 or 1 (examples say so; constraints say so).
// # edges lists unique undirected edges [u, v] with u < v.
// # For a non-empty subset S of vertices, take the INDUCED subgraph: keep only vertices in S
// # and only edges with BOTH endpoints in S.
// # Count subsets S such that:
// #   (1) The induced subgraph on S is CONNECTED (single connected component in that subgraph).
// #   (2) Sum of nums[i] over i in S is EVEN.
// #
// # Why bitmask enumeration works here
// # n <= 13  =>  at most 2^13 - 1 = 8191 non-empty subsets. Brute force over subsets is cheap.
// # This is the intended signal: exponential in n is acceptable; do not need a poly-time
// # closed form for general graphs.
// #
// # High-level algorithm
// # For each non-empty bitmask "sub" (bit i = 1 iff vertex i is in S):
// #   A) Parity filter: compute sum of nums[i] on S. If odd, skip (cannot be even sum).
// #   B) Connectivity: check whether the induced subgraph on S is connected.
// # If both pass, count += 1.
// #
// # Checking connectivity on the induced subgraph
// # Build adjacency list g for the full graph once. When exploring from a vertex in S,
// # only follow edges to neighbors that are also in S (still in g, but we restrict moves
// # by membership in S).
// #
// # Bitmask trick for DFS visited state (no separate set per query)
// # Let full_mask m = (1 << n) - 1  (all n low bits set).
// # Initialize vis = m ^ sub (XOR).
// #   - For bits outside S: sub has 0, m has 1  => vis has 1 (treat as "already done")
// #   - For bits inside S:  sub has 1, m has 1  => vis has 0 (unvisited)
// # So vis encodes: outside S is already "satisfied"; inside S is 0 until we DFS there.
// # Run DFS/BFS from ANY one vertex in S. For the standard code, the start vertex is the
// # index of the highest set bit of sub:  sub.bit_length() - 1  (works since sub > 0).
// # When exploring from u, only go to v if g has edge (u,v) AND v is in S.
// # The implementation marks vis |= (1 << v) for visited vertices; nodes outside S start at
// # 1 in vis, so (vis >> v) & 1 == 0 only for unvisited nodes in S.
// # After traversal, if vis == m, every bit is 1: all of S was reached from one start
// #   => induced subgraph is connected. If S splits into 2+ components, some vertex in S
// #   stays 0 in vis  => vis != m.
// #
// # Why start at sub.bit_length() - 1?
// # That is the index of the most significant 1-bit of sub, which is always an element of S.
// # You could also start at the least significant 1-bit: (sub & -sub).bit_length() - 1.
// #
// # Parity of sum (nums are 0/1)
// # Sum is even iff the number of 1-valued nodes in S is even (equivalently XOR of nums in S
// # is 0). You can micro-optimize with XOR instead of sum; sum is clear and fast enough.
// #
// # Time complexity
// # O(2^n * (n + m)) where m = |edges|.
// #   - 2^n subsets (actually 2^n - 1 non-empty).
// #   - Per subset: O(n) to sum values (or O(1) with popcount tricks), then DFS/BFS over
// #     at most the induced edges touching S, worst O(n + m) if we scan adjacency.
// #   - n <= 13 so this is tiny.
// #
// # Space complexity
// # O(n + m) for the adjacency list and recursion stack O(n) in DFS depth.
// #
// # Edge cases
// # - n = 1, nums = [1]: only subset {0}, sum odd -> answer 0 (matches example 2 style).
// # - n = 1, nums = [0]: subset {0}, sum 0 even, single vertex connected -> answer 1.
// # - Empty edge list: only subsets of size 1 can be connected (no edge). Then we need
// #   sum even -> only isolated vertices with nums[i]=0 count (each singleton with value 0).
// # - Disconnected full graph: still enumerate S; induced subgraph must be one connected
// #   piece, so S cannot mix two components without using an edge (there is none).
// #
// # Data structures chosen
// # - Adjacency list: O(n + m) memory, O(degree) local exploration per step.
// # - Integer bitmasks for subset and vis: O(1) space, fast bit ops in Python for n <= 13.
// # - DFS recursion (or explicit stack): fine for n <= 13.
// #
// # Possible improvements (usually unnecessary here)
// # - Precompute popcount of nums-weighted sum via SOS DP / subset iteration order — overkill.
// # - Union-find per subset: rebuilding DSU per subset is heavier than one DFS.
// # - Only enumerate connected sets via generation — complex; brute force wins at n <= 13.
// #
// # How to present in an interview
// # 1) Note n <= 13 -> exponential in n is fine.
// # 2) Enumerate all non-empty S; filter even sum; check induced connectivity from one vertex.
// # 3) Explain the vis = full_mask ^ sub trick OR say "visited set restricted to S".
// # 4) Complexity O(2^n * (n+m)) time, O(n+m) space.
// # --- end notes ---
// 
// # lc-original code=start
// class Solution:
//     def evenSumSubgraphs(self, nums: list[int], edges: list[list[int]]) -> int:
//         n = len(nums)
//         g = [[] for _ in range(n)]
//         for u, v in edges:
//             g[u].append(v)
//             g[v].append(u)
//         full = (1 << n) - 1
//         ans = 0
//         for sub in range(1, full + 1):
//             s = 0
//             for i in range(n):
//                 if sub >> i & 1:
//                     s += nums[i]
//             if s & 1:
//                 continue
//             vis = full ^ sub
// 
//             def dfs(u: int) -> None:
//                 nonlocal vis
//                 vis |= 1 << u
//                 for v in g[u]:
//                     if (vis >> v) & 1 == 0:
//                         dfs(v)
// 
//             dfs(sub.bit_length() - 1)
//             if vis == full:
//                 ans += 1
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

class Solution {
public:
    int evenSumSubgraphs(vector<int>& nums, vector<vector<int>>& edges) {
        int n = nums.size();
        vector<vector<int>> g(n);
        for (auto& e : edges) {
            g[e[0]].push_back(e[1]);
            g[e[1]].push_back(e[0]);
        }
        int full = (1 << n) - 1, ans = 0;
        for (int sub = 1; sub <= full; ++sub) {
            int sum = 0;
            for (int i = 0; i < n; ++i) if ((sub >> i) & 1) sum += nums[i];
            if (sum & 1) continue;
            int vis = full ^ sub;
            function<void(int)> dfs = [&](int u) {
                vis |= 1 << u;
                for (int v : g[u]) if (((vis >> v) & 1) == 0) dfs(v);
            };
            dfs(31 - __builtin_clz(sub));
            if (vis == full) ++ans;
        }
        return ans;
    }
};
// @lc code=end
