/*
 * @lc app=leetcode id=3812 lang=cpp
 *
 * [3812] Minimum Edge Toggles on a Tree
 */
// Translated from 3812.minimum-edge-toggles-on-a-tree.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3812 lang=python3
// #
// # [3812] Minimum Edge Toggles on a Tree
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given a tree with n nodes and n - 1 indexed edges.
// #
// # Each node has an initial binary color start[i] and desired color target[i].
// #
// # One operation chooses an edge and toggles both endpoints of that edge.
// # We need to return edge indices that transform start into target.
// #
// # Among all valid sequences with minimum possible length, return the edge
// # indices in increasing order.
// #
// # If impossible, return [-1].
// #
// #
// # Convert colors to mismatch bits
// # Define:
// #   need[i] = 1 if start[i] != target[i], else 0
// #
// # A node with need[i] = 1 must be toggled an odd number of times.
// # A node with need[i] = 0 must be toggled an even number of times.
// #
// # Toggling an edge flips need at both endpoints. Our goal is to make every
// # need[i] become 0.
// #
// # So the problem becomes:
// #   choose a set of edges such that each node has incident chosen-edge parity
// #   equal to need[i].
// #
// # This is parity matching on a tree.
// #
// #
// # Important invariant: total parity
// # Every edge operation flips exactly two nodes, so the number of mismatched nodes
// # changes parity by an even amount.
// #
// # Therefore, if the number of need=1 nodes is odd, the transformation is
// # impossible.
// #
// # On a tree, if the number of mismatches is even, a solution always exists and
// # is unique.
// #
// #
// # Rooted-tree greedy
// # Root the tree at node 0.
// #
// # Consider a non-root node u. The only edge connecting u's entire subtree to the
// # rest of the tree is the edge between u and parent[u].
// #
// # After we finish deciding all edges strictly inside u's subtree, if u still has
// # need[u] = 1, there is exactly one remaining way to fix u:
// #   toggle the parent edge.
// #
// # That operation fixes u and flips parent[u].
// #
// # So we process nodes in postorder, from leaves up to the root:
// #
// #   for node u except root:
// #       if need[u] == 1:
// #           choose edge(parent[u], u)
// #           need[u] ^= 1       # becomes 0
// #           need[parent[u]] ^= 1
// #
// # After all non-root nodes are processed, every non-root node is fixed. If the
// # root is also fixed, we have a valid solution. Otherwise impossible.
// #
// #
// # Why the solution is minimum
// # For every non-root node u, once all child subtrees are processed, if need[u] is
// # 1, the parent edge is forced. There is no alternative edge left that can affect
// # u without disturbing already-fixed descendants.
// #
// # Thus every chosen edge is necessary. Since the forced choices produce the
// # unique feasible edge set, it is automatically minimum.
// #
// #
// # Why output sorted edge indices?
// # The statement asks: among all valid sequences with minimum possible length,
// # return the edge indices in increasing order.
// #
// # Edge toggles commute because toggling is XOR/parity-based. The order of
// # operations does not change the final colors. So after finding the required set
// # of edges, we sort their indices before returning.
// #
// #
// # Data structures
// #
// # 1. adjacency list with edge indices
// #    graph[u] contains (v, edge_index). This lets us traverse the tree and know
// #    which original edge index connects a child to its parent.
// #
// # 2. parent arrays
// #    parent[node] and parent_edge[node] store the rooted tree structure.
// #
// # 3. order list
// #    A BFS/DFS order from root. Reversing it gives postorder-like processing:
// #    children before parents.
// #
// # 4. need list
// #    Mutable mismatch bits. Toggling an edge just XORs two entries.
// #
// # We use iterative traversal, not recursion, because n can be 10^5 and a chain
// # tree could exceed Python's recursion limit.
// #
// #
// # Walkthrough of the code
// # 1. Build graph with edge indices.
// # 2. Root the tree at 0 using an iterative traversal.
// # 3. Build need[i] = start[i] XOR target[i].
// # 4. Traverse nodes in reversed order, skipping root.
// # 5. If need[node] is 1:
// #      - append parent_edge[node]
// #      - flip need[node]
// #      - flip need[parent[node]]
// # 6. If need[0] is 1, return [-1].
// # 7. Sort chosen edge indices and return them.
// #
// #
// # Correctness proof
// #
// # Lemma 1: If the number of mismatched nodes is odd, no solution exists.
// # Proof:
// # Each operation toggles exactly two nodes, so it changes the count of mismatched
// # nodes by -2, 0, or +2. The parity of the mismatch count never changes. The
// # target state has 0 mismatches, which is even. Therefore an odd initial mismatch
// # count is impossible.
// #
// # Lemma 2: During postorder processing, when a non-root node u is considered,
// # all edges inside u's child subtrees have already been decided, and the only
// # undecided edge that can still affect u is the edge to parent[u].
// # Proof:
// # Children are processed before u. After a child subtree is processed, changing
// # any edge inside it would disturb already-fixed nodes. In a tree, u has exactly
// # one edge to the outside of its rooted subtree: the parent edge. Therefore only
// # that edge remains available to affect u.
// #
// # Lemma 3: The algorithm's decision at each non-root node is forced in every
// # valid solution.
// # Proof:
// # By Lemma 2, if need[u] = 1, the parent edge must be toggled to fix u. If
// # need[u] = 0, toggling the parent edge would make u incorrect, so it must not
// # be toggled.
// #
// # Lemma 4: After processing all non-root nodes, every non-root node is fixed.
// # Proof:
// # When each non-root node u is processed, the algorithm either toggles its
// # parent edge if needed or leaves it alone if already correct. After that point,
// # no later operation can affect u because only ancestor parent edges may still be
// # considered, and those do not touch u. Thus u remains fixed.
// #
// # Theorem: If the algorithm returns a list of edges, that list is a minimum valid
// # solution. If it returns [-1], no solution exists.
// # Proof:
// # By Lemma 4, all non-root nodes are fixed after processing. If the root is also
// # fixed, the selected edges transform start into target. By Lemma 3, every edge
// # decision is forced in any valid solution, so no shorter valid solution exists.
// # If the root remains mismatched, there is no parent edge left to affect it, so
// # no solution exists.
// #
// #
// # Complexity analysis
// #
// # Let n be the number of nodes.
// #
// # Time:
// #   - Build graph: O(n)
// #   - Root traversal: O(n)
// #   - Postorder processing: O(n)
// #   - Sorting the answer: O(a log a), where a is the number of chosen edges
// #     and a <= n - 1
// #
// # Overall time complexity: O(n log n) because of the required sorted output.
// # If output order did not need sorting, the algorithm would be O(n).
// #
// # Space:
// #   - graph, parent arrays, order, need, answer: O(n)
// # Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      n = 3, edges = [[0,1],[1,2]], start = "010", target = "100"
// #      output [0]
// #
// # 2. Example 2:
// #      larger tree where several forced edges are needed -> [1,2,5]
// #
// # 3. Impossible parity:
// #      n = 2, start = "00", target = "01" -> [-1]
// #
// # 4. Already equal:
// #      start == target -> []
// #
// # 5. Chain tree:
// #      Verifies iterative traversal and postorder logic.
// #
// # 6. Random brute force for small n:
// #      Try every edge subset and compare the minimum sorted subset with this
// #      forced tree solution.
// #
// #
// # Edge cases
// #
// # - No toggles needed: return an empty list.
// # - Odd number of mismatches: impossible.
// # - Root can become fixed only indirectly through child edges; final root check
// #   is necessary.
// # - Edge indices must be original input indices.
// #
// #
// # Possible improvements
// #
// # - We can skip the initial odd-parity check because the final root check catches
// #   impossibility. Keeping the parity explanation is useful for interviews.
// # - If sorted output were not required, we could return edges in postorder and
// #   avoid sorting.
// # - This is equivalent to solving a linear system over GF(2), but the tree
// #   structure makes the forced postorder solution much simpler.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def minimumFlips(
//         self, n: int, edges: List[List[int]], start: str, target: str
//     ) -> List[int]:
//         graph = [[] for _ in range(n)]
//         for idx, (u, v) in enumerate(edges):
//             graph[u].append((v, idx))
//             graph[v].append((u, idx))
// 
//         parent = [-1] * n
//         parent_edge = [-1] * n
//         order = [0]
// 
//         for node in order:
//             for nei, edge_idx in graph[node]:
//                 if nei == parent[node]:
//                     continue
//                 parent[nei] = node
//                 parent_edge[nei] = edge_idx
//                 order.append(nei)
// 
//         need = [int(a != b) for a, b in zip(start, target)]
//         answer = []
// 
//         for node in reversed(order[1:]):
//             if need[node]:
//                 answer.append(parent_edge[node])
//                 need[node] ^= 1
//                 need[parent[node]] ^= 1
// 
//         if need[0]:
//             return [-1]
// 
//         answer.sort()
//         return answer
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
    vector<int> minimumFlips(int n, vector<vector<int>>& edges, string start, string target) {
        vector<vector<pair<int, int>>> g(n);
        for (int i = 0; i < (int)edges.size(); ++i) {
            int u = edges[i][0], v = edges[i][1];
            g[u].push_back({v, i});
            g[v].push_back({u, i});
        }
        vector<int> parent(n, -1), parentEdge(n, -1), order{0};
        for (int node : order) for (auto [nei, ei] : g[node]) if (nei != parent[node]) {
            parent[nei] = node;
            parentEdge[nei] = ei;
            order.push_back(nei);
        }
        vector<int> need(n);
        for (int i = 0; i < n; ++i) need[i] = start[i] != target[i];
        vector<int> ans;
        for (int idx = n - 1; idx >= 1; --idx) {
            int node = order[idx];
            if (need[node]) {
                ans.push_back(parentEdge[node]);
                need[node] ^= 1;
                need[parent[node]] ^= 1;
            }
        }
        if (need[0]) return {-1};
        sort(ans.begin(), ans.end());
        return ans;
    }
};
// @lc code=end
