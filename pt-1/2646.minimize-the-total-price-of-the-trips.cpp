/*
 * @lc app=leetcode id=2646 lang=cpp
 *
 * [2646] Minimize the Total Price of the Trips
 */
// Translated from 2646.minimize-the-total-price-of-the-trips.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2646 lang=python3
// #
// # [2646] Minimize the Total Price of the Trips
// #
// 
// # --- Notes (problem, path counts, tree DP, independence, complexity, edges, interview) ---
// #
// # Problem restatement
// # Undirected tree on n nodes with integer prices price[u]. You are given several trips [start, end];
// # each trip walks along the unique simple path between those endpoints (standard on a tree).
// # For each node u, every time a trip path goes through u, you pay price[u] toward that trip’s
// # contribution — equivalently, total cost equals sum_u price[u] * freq[u], where freq[u] is how
// # many trip-paths include u.
// # Before counting trips, you may choose a set of nodes whose prices are HALVED (integer division)
// # for every traversal payment through them, with the rule that you cannot halve two adjacent nodes.
// # Minimize the resulting total cost over all trips combined.
// #
// # Step 1 — frequency on paths (why not multiply per trip naïvely?)
// # Each trip’s path is unique in a tree. For each [start, end], increment freq[u] by 1 for every u
// # on that path. Implementation: DFS from start toward end by exploring neighbors except parent until
// # hitting end; accumulate visited nodes on the successful branch (short-circuit once end found).
// # Complexity O(sum of path lengths) <= O(n * |trips|) worst case; acceptable for LC constraints.
// # Improvement: LCA + difference-on-tree marks all paths in O((n + |trips|) log n) if paths are long.
// #
// # Step 2 — tree DP after collapsing weights
// # Define weighted cost w[u] = price[u] * freq[u]. Halving u saves w[u] / 2 on payments through u
// # (cost becomes w[u]/2). Adjacent halving forbidden ⇒ chosen halving vertices form an independent
// # set — weighted MIS-style DP on a tree.
// # State: dfs(u, prev, parentHalved) = minimum total downstream contribution for the subtree rooted at
// # u when edge (parent(u), u) is fixed and parentHalved tells whether parent’s price was halved.
// # Transitions at u:
// #   - Always allowed: pay full w[u] at u; children see parentHalved = False.
// #   - If parent was NOT halved, optionally halve u: pay w[u]//2 at u; children must see
// #     parentHalved = True (cannot halve a child if u is halved — equivalent constraint).
// #   - If parent WAS halved, u cannot be halved — only full-price branch.
// # Answer: dfs(root, -1, False). Root 0 after fixing an arbitrary tree orientation.
// #
// # Why this DP is correct
// # On a tree, decisions at children depend only on whether their parent took half pricing — global
// # independence constraint propagates exactly this one bit; subtrees are independent given that bit.
// #
// # Time complexity
// # - Path marking: O(total nodes across all trip paths) <= O(n * |trips|) worst case.
// # - DP: O(n) states with degree-sum work -> O(n).
// #
// # Space complexity
// # - O(n) for graph, freq, recursion stack / memo (e.g. lru_cache depth O(n) worst).
// #
// # Edge cases
// # - freq[u] == 0: node never used by trips — contributes 0 regardless of halving (still consistent).
// # - Single node trips (start == end): path is one node; freq increments correctly via DFS base case.
// # - price halving uses integer division // per statement / examples.
// #
// # Improvements
// # - Binary lifting LCA + difference array for frequencies when paths are long and many trips.
// # - Iterative DP / explicit memo table instead of lru_cache if recursion depth is a concern (convert
// #   tree to rooted order via stack).
// #
// # LeetCode submission
// # Put `from typing import List` and `functools.lru_cache` inside # lc-original code=start.
// #
// # Interview walkthrough
// # 1) Separate “how often each node is paid” from “which nodes we halve”.
// # 2) Recognize independent-set structure on a tree -> parent-state DP.
// # 3) Implement freq then DP; discuss faster freq counting if asked.
// # --- end notes ---
// 
// # lc-original code=start
// import functools
// from typing import List
// 
// 
// class Solution:
//     def minimumTotalPrice(self, n: int, edges: List[List[int]], price: List[int], trips: List[List[int]]) -> int:
//         g = [[] for _ in range(n)]
//         for u, v in edges:
//             g[u].append(v)
//             g[v].append(u)
// 
//         freq = [0] * n
// 
//         def mark_path(start: int, end: int) -> None:
//             path: List[int] = []
// 
//             def dfs(u: int, parent: int) -> bool:
//                 path.append(u)
//                 if u == end:
//                     for x in path:
//                         freq[x] += 1
//                     path.pop()
//                     return True
//                 for v in g[u]:
//                     if v != parent and dfs(v, u):
//                         path.pop()
//                         return True
//                 path.pop()
//                 return False
// 
//             dfs(start, -1)
// 
//         for s, e in trips:
//             mark_path(s, e)
// 
//         @functools.lru_cache(maxsize=None)
//         def dfs(u: int, prev: int, parent_halved: bool) -> int:
//             pay_full = price[u] * freq[u] + sum(
//                 dfs(v, u, False) for v in g[u] if v != prev
//             )
//             if parent_halved:
//                 return pay_full
//             pay_half = (price[u] // 2) * freq[u] + sum(
//                 dfs(v, u, True) for v in g[u] if v != prev
//             )
//             return min(pay_full, pay_half)
// 
//         return dfs(0, -1, False)
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
    int minimumTotalPrice(int n, vector<vector<int>>& edges, vector<int>& price, vector<vector<int>>& trips) {
        vector<vector<int>> g(n);
        for (auto& e : edges) {
            g[e[0]].push_back(e[1]);
            g[e[1]].push_back(e[0]);
        }
        vector<int> freq(n, 0), path;
        function<bool(int, int, int)> mark = [&](int u, int parent, int target) {
            path.push_back(u);
            if (u == target) {
                for (int x : path) ++freq[x];
                path.pop_back();
                return true;
            }
            for (int v : g[u]) if (v != parent && mark(v, u, target)) {
                path.pop_back();
                return true;
            }
            path.pop_back();
            return false;
        };
        for (auto& trip : trips) mark(trip[0], -1, trip[1]);
        function<pair<int, int>(int, int)> dfs = [&](int u, int parent) -> pair<int, int> {
            int full = price[u] * freq[u];
            int half = price[u] / 2 * freq[u];
            for (int v : g[u]) if (v != parent) {
                auto [childFree, childBlocked] = dfs(v, u);
                full += childFree;
                half += childBlocked;
            }
            return {min(full, half), full};
        };
        return dfs(0, -1).first;
    }
};
// @lc code=end
