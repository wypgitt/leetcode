// Translated from 2642.design-graph-with-shortest-path-calculator.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=2642 lang=python3
// #
// # [2642] Design Graph With Shortest Path Calculator
// #
// 
// # --- Notes (API, modeling, Dijkstra vs Floyd, heap, complexity, edges, interview) ---
// #
// # Problem / API
// # - Directed weighted graph with n nodes labeled 0 .. n-1.
// # - `Graph(n, edges)` builds initial adjacency from `edges`, each edge `[u, v, w]` meaning u -> v with
// #   nonnegative weight w (LeetCode uses positive costs in examples; Dijkstra requires nonnegative).
// # - `addEdge([u, v, w])` appends another directed edge (parallel edges allowed).
// # - `shortestPath(node1, node2)` returns minimum total edge weight along any directed path from
// #   node1 to node2, or -1 if unreachable. Convention: shortest path from a node to itself is 0.
// #
// # Why Dijkstra on each query?
// # - Edges are appended over time; the graph grows but stays sparse in typical tests.
// # - Running Dijkstra from `node1` whenever `shortestPath` is called costs O((V + E) log V) with a
// #   binary heap — simple, correct for nonnegative weights, no separate update logic when edges are added.
// # - Alternative: maintain all-pairs shortest paths with Floyd–Warshall (O(n^3) setup, O(n^2) per
// #   `addEdge` relaxation, O(1) query). Better only when n is small and queries vastly outnumber adds.
// #
// # Algorithm (Dijkstra)
// # - Single-source shortest paths from `node1`: dist[x] = best known cost to reach x.
// # - Min-heap ordered by tentative distance; pop smallest (lazy deletion when stale entries appear).
// # - Relax outgoing edges (v, w) from u: if dist[u] + w < dist[v], update and push.
// # - Stop early optional when node2 popped — implemented by checking when we extract node2 (first time
// #   is optimal).
// #
// # Data structures
// # - Adjacency list: `list[list[tuple[int,int]]]` — O(V + E) memory, fast iteration of out-edges.
// # - `heapq` min-heap of `(distance, node)` pairs.
// # - `dist` array length n, initialized to +infinity except source 0.
// #
// # Time complexity
// # - `__init__`: O(n + |initial edges|).
// # - `addEdge`: O(1) amortized append.
// # - `shortestPath`: O((V + E') log V) where E' is edges present at query time (standard Dijkstra).
// #
// # Space complexity
// # - O(V + E) for the graph plus O(V) for dist and O(E) heap worst-case — dominated by graph storage.
// #
// # Edge cases
// # - node1 == node2 -> return 0 without searching.
// # - Disconnected target -> heap empties, dist[node2] still inf -> -1.
// # - Multiple edges u -> v: adjacency list keeps all; Dijkstra naturally picks cheapest combination.
// #
// # Improvements / variants
// # - For tiny n and many queries: Floyd–Warshall incremental updates (see editorial).
// # - For integer weights small: Dial’s algorithm (bucket deque) can replace heap.
// # - Early exit: break when popped node == node2 (optional micro-optimization).
// #
// # LeetCode submission
// # Put imports (`heapq`, `math`, `typing.List`) inside # @lc code=start.
// #
// # Interview walkthrough
// # 1) Dynamic graph + shortest path queries -> incremental APSP vs on-demand SSSP.
// # 2) Nonnegative weights -> Dijkstra; cite why not Bellman-Ford here.
// # 3) Adjacency list + heap complexity.
// # 4) Mention Floyd trade-off when interview asks for faster queries at small n.
// # --- end notes ---
// 
// # @lc code=start
// import heapq
// import math
// from typing import List
// 
// 
// class Graph:
//     def __init__(self, n: int, edges: List[List[int]]) -> None:
//         self._n = n
//         self._g: List[List[tuple[int, int]]] = [[] for _ in range(n)]
//         for u, v, w in edges:
//             self._g[u].append((v, w))
// 
//     def addEdge(self, edge: List[int]) -> None:
//         u, v, w = edge
//         self._g[u].append((v, w))
// 
//     def shortestPath(self, node1: int, node2: int) -> int:
//         if node1 == node2:
//             return 0
//         dist = [math.inf] * self._n
//         dist[node1] = 0
//         heap: List[tuple[float, int]] = [(0.0, node1)]
//         while heap:
//             d, u = heapq.heappop(heap)
//             if d > dist[u]:
//                 continue
//             if u == node2:
//                 return int(d)
//             for v, w in self._g[u]:
//                 nd = d + w
//                 if nd < dist[v]:
//                     dist[v] = nd
//                     heapq.heappush(heap, (nd, v))
//         return -1
// 
// 
// # Your Graph object will be instantiated and called as such:
// # obj = Graph(n, edges)
// # obj.addEdge(edge)
// # param_2 = obj.shortestPath(node1,node2)
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

class Graph {
    int n;
    vector<vector<pair<int, int>>> g;

public:
    Graph(int n, vector<vector<int>>& edges) : n(n), g(n) {
        for (auto& e : edges) g[e[0]].push_back({e[1], e[2]});
    }

    void addEdge(vector<int> edge) {
        g[edge[0]].push_back({edge[1], edge[2]});
    }

    int shortestPath(int node1, int node2) {
        if (node1 == node2) return 0;
        const long long INF = (long long)4e18;
        vector<long long> dist(n, INF);
        priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<pair<long long, int>>> pq;
        dist[node1] = 0;
        pq.push({0, node1});
        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            if (d != dist[u]) continue;
            if (u == node2) return (int)d;
            for (auto [v, w] : g[u]) {
                if (d + w < dist[v]) {
                    dist[v] = d + w;
                    pq.push({dist[v], v});
                }
            }
        }
        return -1;
    }
};
