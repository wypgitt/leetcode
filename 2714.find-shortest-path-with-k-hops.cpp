// Translated from 2714.find-shortest-path-with-k-hops.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=2714 lang=python3
// #
// # [2714] Find Shortest Path with K Hops
// #
// 
// # --- Interview notes (statement, layered graph, Dijkstra, complexity, edges, tests) ---
// #
// # Problem (summary)
// # Undirected weighted connected graph on n nodes (0 .. n-1). You may choose up to k edges on your walk and
// # treat their weights as 0 (each such edge still counts as one step — “hop” here means zeroing that edge’s
// # contribution to cost). Find the minimum total cost of a walk from source s to destination d.
// #
// # Equivalent layered shortest path
// # Expand each vertex u into (k+1) states (u, t) meaning:
// #   “we have arrived at node u having already used exactly t zero-cost edges along the path taken so far.”
// # Transitions from state (u, t) along undirected edge (u, v) with weight w:
// #   (A) Pay the edge: go to (v, t) with added cost w.
// #   (B) If t < k, zero the edge: go to (v, t + 1) with added cost 0.
// # All edge weights in the expanded graph are non-negative → Dijkstra applies on states (u, t).
// #
// # Why not plain Dijkstra on the original graph
// # Original graph does not encode how many free edges remain; that resource couples choices — classic
// # shortest path with a small integer resource → DP dimension or layered graph.
// #
// # Algorithm
// # - Build adjacency lists for the undirected graph.
// # - dist[u][t] = best known cost to reach u with exactly t free edges used (initialize ∞ except dist[s][0]=0).
// # - Priority queue of (cost, u, t); pop smallest; relax neighbors:
// #     nd = cost + w  → relax (v, t)
// #     if t < k: relax (v, t+1) at same cost (hop / zero-weight edge).
// # - Answer = min_t dist[d][t].
// #
// # Data structures
// # - Adjacency list: O(n + |E|).
// # - dist: n × (k+1) table (or sparse map if needed — here explicit table is fine).
// # - Min-heap for Dijkstra.
// #
// # Time complexity
// # States: O(n · k). Each undirected edge examined from each (u,t) at most when that state is finalized —
// # roughly O(|E| · k) relaxations in practice; heap pushes bounded similarly → O(|E| · k · log(n · k)) typical.
// #
// # Space complexity
// # O(n · k + |E|) for distances + graph.
// #
// # Alternatives (interview variants)
// # - Bellman–Ford style: repeat relaxation k+1 rounds on implicit layered edges — O(|E| · k · (k+1)) variants;
// #   Dijkstra preferred when all expanded weights are non-negative (they are).
// # - If k were huge but special structure, other tricks — not needed under usual constraints.
// #
// # Edge cases
// # - s == d: answer 0 (dist[s][0] = 0).
// # - k == 0: ordinary shortest path from s to d.
// # - Using a hop on a zero-weight edge: allowed but never worsens cost.
// #
// # Tests (mental / small)
// # - n=2, edge weight W, k>=1: answer 0 if hop used on that edge.
// # - Line graph with large weights: optimal deployment of k zeros along path — matches brute force on tiny n.
// #
// # Improvements
// # - Early exit when destination extracted with minimal possible layer — optional micro-optimization.
// #
// # --- end notes ---
// 
// # @lc code=start
// import heapq
// from typing import List
// 
// 
// class Solution:
//     def shortestPathWithHops(self, n: int, edges: List[List[int]], s: int, d: int, k: int) -> int:
//         g = [[] for _ in range(n)]
//         for u, v, w in edges:
//             g[u].append((v, w))
//             g[v].append((u, w))
// 
//         inf = 10**18
//         dist = [[inf] * (k + 1) for _ in range(n)]
//         dist[s][0] = 0
//         pq = [(0, s, 0)]
// 
//         while pq:
//             du, u, t = heapq.heappop(pq)
//             if du > dist[u][t]:
//                 continue
//             for v, w in g[u]:
//                 nd = du + w
//                 if nd < dist[v][t]:
//                     dist[v][t] = nd
//                     heapq.heappush(pq, (nd, v, t))
//                 if t < k:
//                     nd = du
//                     if nd < dist[v][t + 1]:
//                         dist[v][t + 1] = nd
//                         heapq.heappush(pq, (nd, v, t + 1))
// 
//         return min(dist[d])
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
    int shortestPathWithHops(int n, vector<vector<int>>& edges, int s, int d, int k) {
        vector<vector<pair<int, int>>> g(n);
        for (auto& e : edges) {
            g[e[0]].push_back({e[1], e[2]});
            g[e[1]].push_back({e[0], e[2]});
        }
        const long long INF = (long long)4e18;
        vector<vector<long long>> dist(n, vector<long long>(k + 1, INF));
        using State = tuple<long long, int, int>;
        priority_queue<State, vector<State>, greater<State>> pq;
        dist[s][0] = 0;
        pq.push({0, s, 0});
        while (!pq.empty()) {
            auto [du, u, used] = pq.top();
            pq.pop();
            if (du > dist[u][used]) continue;
            for (auto [v, w] : g[u]) {
                if (du + w < dist[v][used]) {
                    dist[v][used] = du + w;
                    pq.push({dist[v][used], v, used});
                }
                if (used < k && du < dist[v][used + 1]) {
                    dist[v][used + 1] = du;
                    pq.push({du, v, used + 1});
                }
            }
        }
        return (int)*min_element(dist[d].begin(), dist[d].end());
    }
};
