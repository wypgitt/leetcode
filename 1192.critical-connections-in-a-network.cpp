// Translated from 1192.critical-connections-in-a-network.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1192 lang=python3
// #
// # [1192] Critical Connections In A Network
// #
// 
// # --- Interview notes (bridges, Tarjan DFS, low-link, complexity, multigraph caveat, tests) ---
// #
// # Problem
// # Undirected connected graph on `n` labeled vertices `0 … n-1`. **Critical connections** (bridges) are edges whose removal
// # increases the number of connected components — equivalently, edges that belong to **no** simple cycle.
// #
// # Why Tarjan / DFS low-link (not BFS alone)
// # We need structural information about cycles vs tree edges in a DFS spanning forest. **Discovery times** and **low values**
// # summarize, per subtree, whether there is a back edge to an ancestor — the classical **O(V+E)** bridge algorithm.
// #
// # Definitions (DFS from an arbitrary root)
// # • `disc[u]` — discovery time / preorder stamp when `u` is first visited (1-based counter here).
// # • `low[u]` — minimum discovery time reachable from `u` using **zero or more tree edges down** plus **at most one back edge
// #   up** to an ancestor (standard low-link for undirected bridge detection).
// #
// # Bridge criterion (tree edge u → v, where `v` is a child of `u` in DFS tree)
// # Edge `(u, v)` is a bridge **iff** `low[v] > disc[u]`.
// # Interpretation: everything reachable from `v` without using edge `(u,v)` stays strictly below `u` in DFS order — no back
// # edge from `v`’s subtree hooks to `u` or above. Removing `(u,v)` isolates that subtree.
// #
// # Back edges
// # When exploring `u` and hitting a visited neighbor `w` that is **not** the DFS parent, update `low[u] = min(low[u],
// # disc[w])` (edge to an ancestor or already discovered vertex in undirected graph).
// #
// # Algorithm
// # 1. Build adjacency lists.
// # 2. Run one DFS (or from every unvisited vertex if the graph might be disconnected — still correct).
// # 3. After recursive call returns from child `v`, set `low[u] = min(low[u], low[v])` and test bridge condition.
// #
// # Data structures
// # • **Adjacency list** — `O(V+E)` space, optimal traversal.
// # • **Arrays `disc`, `low`** — `O(V)`.
// # • **Output list** — `O(E)` worst case (at most `V-1` bridges in a tree).
// #
// # Time complexity **O(V + E)** — each vertex and edge examined constant times.
// #
// # Space complexity **O(V + E)** for graph + recursion stack **O(V)** (worst path depth).
// #
// # Multigraph caveat (parallel edges)
// # If two **parallel** edges connect the same endpoints, neither is a bridge; the naive `if v == parent: continue` skips **all**
// # edges to the parent and mis-handles the second parallel edge. Fixes: traverse **edge ids**, or count parent skips.
// # LeetCode inputs are typically **simple** graphs (at most one edge per unordered pair); this solution assumes that.
// #
// # Edge cases
// # • Tree on `n` nodes — every edge is a bridge (`n-1` bridges).
// # • Single cycle — **no** bridges.
// # • `n = 2`, one edge — that edge is critical.
// #
// # Tests (sanity)
// # • `n = 4`, `connections = [[0,1],[1,2],[2,0],[1,3]]` → triangle plus leaf: only **`[1,3]`** is a bridge.
// #
// # Improvements
// # • Iterative DFS if recursion depth exceeds Python limit on very long paths (rare with constraints).
// # • Tarjan also finds articulation points with a small extension — related interview topic.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def criticalConnections(self, n: int, connections: List[List[int]]) -> List[List[int]]:
//         g = [[] for _ in range(n)]
//         for a, b in connections:
//             g[a].append(b)
//             g[b].append(a)
// 
//         disc = [0] * n
//         low = [0] * n
//         t = 1
//         bridges = []
// 
//         def dfs(u: int, parent: int) -> None:
//             nonlocal t
//             disc[u] = low[u] = t
//             t += 1
//             for v in g[u]:
//                 if v == parent:
//                     continue
//                 if disc[v] == 0:
//                     dfs(v, u)
//                     low[u] = min(low[u], low[v])
//                     if low[v] > disc[u]:
//                         bridges.append([min(u, v), max(u, v)])
//                 else:
//                     low[u] = min(low[u], disc[v])
// 
//         for i in range(n):
//             if disc[i] == 0:
//                 dfs(i, -1)
// 
//         return sorted(bridges)
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

class Solution {
public:
    vector<vector<int>> criticalConnections(int n, vector<vector<int>>& connections) {
        vector<vector<int>> g(n);
        for (auto& e : connections) {
            g[e[0]].push_back(e[1]);
            g[e[1]].push_back(e[0]);
        }
        vector<int> disc(n), low(n);
        int timer = 1;
        vector<vector<int>> bridges;
        function<void(int, int)> dfs = [&](int u, int parent) {
            disc[u] = low[u] = timer++;
            for (int v : g[u]) {
                if (v == parent) continue;
                if (!disc[v]) {
                    dfs(v, u);
                    low[u] = min(low[u], low[v]);
                    if (low[v] > disc[u]) bridges.push_back({min(u, v), max(u, v)});
                } else {
                    low[u] = min(low[u], disc[v]);
                }
            }
        };
        for (int i = 0; i < n; ++i) if (!disc[i]) dfs(i, -1);
        sort(bridges.begin(), bridges.end());
        return bridges;
    }
};
