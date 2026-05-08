// Translated from 3772.maximum-subgraph-score-in-a-tree.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3772 lang=python3
// #
// # [3772] Maximum Subgraph Score in a Tree
// #
// # https://leetcode.com/problems/maximum-subgraph-score-in-a-tree/description/
// #
// # algorithms
// # Hard (70.58%)
// # Likes:    53
// # Dislikes: 3
// # Total Accepted:    5.8K
// # Total Submissions: 8.2K
// # Testcase Example:  '3\n[[0,1],[1,2]]\n[1,0,1]'
// #
// # You are given an undirected tree with n nodes, numbered from 0 to n - 1. It
// # is represented by a 2D integer array edges​​​​​​​ of length n - 1, where
// # edges[i] = [ai, bi] indicates that there is an edge between nodes ai and bi
// # in the tree.
// # 
// # You are also given an integer array good of length n, where good[i] is 1 if
// # the i^th node is good, and 0 if it is bad.
// # 
// # Define the score of a subgraph as the number of good nodes minus the number
// # of bad nodes in that subgraph.
// # 
// # For each node i, find the maximum possible score among all connected
// # subgraphs that contain node i.
// # 
// # Return an array of n integers where the i^th element is the maximum score for
// # node i.
// # 
// # A subgraph is a graph whose vertices and edges are subsets of the original
// # graph.
// # 
// # A connected subgraph is a subgraph in which every pair of its vertices is
// # reachable from one another using only its edges.
// # 
// # 
// # Example 1:
// # 
// # 
// # 
// # 
// # Input: n = 3, edges = [[0,1],[1,2]], good = [1,0,1]
// # 
// # Output: [1,1,1]
// # 
// # Explanation:
// # 
// # 
// # Green nodes are good and red nodes are bad.
// # For each node, the best connected subgraph containing it is the whole tree,
// # which has 2 good nodes and 1 bad node, resulting in a score of 1.
// # Other connected subgraphs containing a node may have the same score.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # 
// # 
// # Input: n = 5, edges = [[1,0],[1,2],[1,3],[3,4]], good = [0,1,0,1,1]
// # 
// # Output: [2,3,2,3,3]
// # 
// # Explanation:
// # 
// # 
// # Node 0: The best connected subgraph consists of nodes 0, 1, 3, 4, which has 3
// # good nodes and 1 bad node, resulting in a score of 3 - 1 = 2.
// # Nodes 1, 3, and 4: The best connected subgraph consists of nodes 1, 3, 4,
// # which has 3 good nodes, resulting in a score of 3.
// # Node 2: The best connected subgraph consists of nodes 1, 2, 3, 4, which has 3
// # good nodes and 1 bad node, resulting in a score of 3 - 1 = 2.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # 
// # 
// # Input: n = 2, edges = [[0,1]], good = [0,0]
// # 
// # Output: [-1,-1]
// # 
// # Explanation:
// # 
// # For each node, including the other node only adds another bad node, so the
// # best score for both nodes is -1.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 2 <= n <= 10^5
// # edges.length == n - 1
// # edges[i] = [ai, bi]
// # 0 <= ai, bi < n
// # good.length == n
// # 0 <= good[i] <= 1
// # The input is generated such that edges represents a valid tree.
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def maxSubgraphScore(self, n: int, edges: List[List[int]], good: List[int]) -> List[int]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We have a tree.  Each node has score:
// 
//             +1 if good[i] == 1
//             -1 if good[i] == 0
// 
//         For every node `i`, we need the maximum score of any connected subgraph
//         that contains `i`.
// 
//         In a tree, a connected subgraph is just a connected set of nodes, and
//         between any two chosen nodes the path between them must also be chosen.
// 
//         Key observation
//         ---------------
//         Fix a node `u`.  If we choose a connected subgraph containing `u`, then
//         for each neighbor `v` of `u`, we have a choice:
// 
//         * do not take anything from the component on `v`'s side
//         * take a connected piece from that side that attaches through `v`
// 
//         If the best contribution from that side is positive, we should include
//         it.  If it is zero or negative, including it cannot improve the answer.
// 
//         Therefore:
// 
//             answer[u] = weight[u] + sum(max(0, best contribution from each
//                                             neighboring side))
// 
//         This is a rerooting DP problem because every edge has two sides, and
//         every node needs contributions from all neighboring sides.
// 
//         First DP: downward contribution
//         -------------------------------
//         Root the tree at node 0.
// 
//         Define:
// 
//             down[u] = maximum score of a connected subgraph that:
//                       * contains u
//                       * uses only nodes in u's rooted subtree
// 
//         Then:
// 
//             down[u] = weight[u] + sum(max(0, down[child]))
// 
//         Why?
//         A connected subtree-side subgraph containing `u` can independently
//         decide whether to include each child side.  A child side must attach
//         through that child, and its best value is `down[child]`.  We include it
//         only if positive.
// 
//         Second DP: reroot to get full answers
//         -------------------------------------
//         `down[u]` only sees descendants.  For the final answer at `u`, we also
//         need the contribution from the parent side.
// 
//         Let:
// 
//             answer[u] = best score of any connected subgraph in the whole tree
//                         that contains u
// 
//         If we know `answer[parent]`, then the contribution from the parent side
//         to child `u` is:
// 
//             answer[parent] - max(0, down[u])
// 
//         because `answer[parent]` includes:
// 
//             weight[parent]
//             plus positive contributions from all neighbors of parent
// 
//         One of those neighbor contributions might be `max(0, down[u])`, the side
//         going into child `u`.  To get the best connected component on the parent
//         side only, remove that child-side contribution.
// 
//         Then:
// 
//             answer[u] = down[u] + max(0, parent_side_contribution)
// 
//         Equivalently:
// 
//             answer[child] =
//                 down[child]
//                 + max(0, answer[parent] - max(0, down[child]))
// 
//         Data structure choice
//         ---------------------
//         We use:
// 
//         * adjacency list for the tree
//         * arrays `parent`, `order`, `down`, and `answer`
// 
//         We avoid recursive DFS because `n` can be `10^5`, and a chain-shaped
//         tree could exceed Python's recursion depth.  An iterative traversal is
//         safer.
// 
//         Algorithm
//         ---------
//         1. Convert each node to a weight:
// 
//                weight[i] = 1 if good[i] == 1 else -1
// 
//         2. Build the adjacency list.
//         3. Root the tree at 0 with an iterative traversal:
//               * store `parent`
//               * store traversal `order`
// 
//         4. Process nodes in reverse order to compute `down`:
// 
//                down[u] = weight[u] + sum(max(0, down[child]))
// 
//         5. Set:
// 
//                answer[0] = down[0]
// 
//            because root has no parent side.
// 
//         6. Traverse nodes in normal order and push answers to children:
// 
//                parent_side = answer[u] - max(0, down[child])
//                answer[child] = down[child] + max(0, parent_side)
// 
//         Correctness proof
//         -----------------
//         Lemma 1: `down[u]` is the maximum score of a connected subgraph
//         containing `u` using only nodes in `u`'s rooted subtree.
//         Such a subgraph may include any child side, but if it includes a child
//         side, it must include a connected subgraph containing that child.  The
//         best such contribution is `down[child]`.  Positive contributions improve
//         the score; non-positive contributions do not.  Thus the recurrence for
//         `down[u]` is optimal.
// 
//         Lemma 2: For an edge `(u, child)`, the best contribution available to
//         `child` from the `u` side is:
// 
//             answer[u] - max(0, down[child])
// 
//         `answer[u]` is built from `u` plus all positive neighboring side
//         contributions.  The side going into `child` contributes exactly
//         `max(0, down[child])`.  Removing it leaves the best connected component
//         containing `u` that does not use the child's subtree, which is exactly
//         the parent-side contribution for `child`.
// 
//         Lemma 3: `answer[u]` computed by the reroot transition is the maximum
//         score of any connected subgraph in the whole tree containing `u`.
//         The optimal whole-tree subgraph containing `u` consists of `u`'s
//         subtree-side optimum `down[u]` plus, optionally, a positive contribution
//         from the parent side.  By Lemma 2, that parent-side value is computed
//         correctly.  Including it only when positive is optimal.
// 
//         Theorem: The algorithm returns the correct maximum score for every node.
//         Lemma 1 computes all subtree-side optima.  The root answer is `down[0]`
//         because there is no parent side.  Applying Lemma 2 and Lemma 3 along
//         every tree edge computes every other node's whole-tree optimum.
// 
//         Complexity analysis
//         -------------------
//         Building the adjacency list and traversal order is O(n).
//         Each edge is considered a constant number of times.
// 
//         Time:
// 
//             O(n)
// 
//         Space:
// 
//             O(n)
// 
//         for adjacency, parent/order arrays, and DP arrays.
// 
//         Edge cases
//         ----------
//         * All nodes bad:
//           Every node has weight -1.  The best connected subgraph for each node
//           is the node alone, so answers are all -1.
// 
//         * All nodes good:
//           The best connected subgraph for every node is the whole tree, so each
//           answer is n.
// 
//         * Chain tree:
//           Iterative traversal avoids recursion-depth issues.
// 
//         * Star tree:
//           Rerooting handles many child components naturally.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples.
//         * All-good tree.
//         * All-bad tree.
//         * Small trees compared with brute force enumeration of all connected
//           node subsets.
// 
//         Possible improvement
//         --------------------
//         This O(n) rerooting DP is optimal because every node and edge must be
//         inspected.  The main implementation improvement in Python is using
//         iterative traversal instead of recursion for reliability on deep trees.
//         """
// 
//         adjacency = [[] for _ in range(n)]
//         for first, second in edges:
//             adjacency[first].append(second)
//             adjacency[second].append(first)
// 
//         weight = [1 if value == 1 else -1 for value in good]
// 
//         parent = [-1] * n
//         order = [0]
// 
//         for node in order:
//             for neighbor in adjacency[node]:
//                 if neighbor == parent[node]:
//                     continue
// 
//                 parent[neighbor] = node
//                 order.append(neighbor)
// 
//         down = weight[:]
// 
//         for node in reversed(order):
//             for neighbor in adjacency[node]:
//                 if parent[neighbor] == node:
//                     down[node] += max(0, down[neighbor])
// 
//         answer = [0] * n
//         answer[0] = down[0]
// 
//         for node in order:
//             for neighbor in adjacency[node]:
//                 if parent[neighbor] != node:
//                     continue
// 
//                 contribution_without_child = answer[node] - max(0, down[neighbor])
//                 answer[neighbor] = down[neighbor] + max(0, contribution_without_child)
// 
//         return answer
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     def brute_force_max_subgraph_score(
//         test_n: int,
//         test_edges: List[List[int]],
//         test_good: List[int],
//     ) -> List[int]:
//         adjacency = [[False] * test_n for _ in range(test_n)]
//         for first, second in test_edges:
//             adjacency[first][second] = True
//             adjacency[second][first] = True
// 
//         weights = [1 if value == 1 else -1 for value in test_good]
//         best = [-10**9] * test_n
// 
//         for mask in range(1, 1 << test_n):
//             nodes = [index for index in range(test_n) if mask & (1 << index)]
//             seen = {nodes[0]}
//             stack = [nodes[0]]
// 
//             while stack:
//                 node = stack.pop()
//                 for neighbor in nodes:
//                     if neighbor not in seen and adjacency[node][neighbor]:
//                         seen.add(neighbor)
//                         stack.append(neighbor)
// 
//             if len(seen) != len(nodes):
//                 continue
// 
//             score = sum(weights[node] for node in nodes)
//             for node in nodes:
//                 best[node] = max(best[node], score)
// 
//         return best
// 
//     solution = Solution()
// 
//     fixed_tests = [
//         (3, [[0, 1], [1, 2]], [1, 0, 1], [1, 1, 1]),
//         (
//             5,
//             [[1, 0], [1, 2], [1, 3], [3, 4]],
//             [0, 1, 0, 1, 1],
//             [2, 3, 2, 3, 3],
//         ),
//         (2, [[0, 1]], [0, 0], [-1, -1]),
//         (4, [[0, 1], [1, 2], [2, 3]], [1, 1, 1, 1], [4, 4, 4, 4]),
//         (4, [[0, 1], [0, 2], [0, 3]], [0, 0, 0, 0], [-1, -1, -1, -1]),
//     ]
// 
//     for test_n, test_edges, test_good, expected in fixed_tests:
//         assert solution.maxSubgraphScore(test_n, test_edges, test_good) == expected
// 
//     brute_force_cases = [
//         (4, [[0, 1], [1, 2], [1, 3]], [1, 0, 1, 0]),
//         (5, [[0, 1], [0, 2], [2, 3], [2, 4]], [0, 1, 1, 0, 1]),
//         (6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], [1, 0, 0, 1, 1, 0]),
//     ]
// 
//     for test_n, test_edges, test_good in brute_force_cases:
//         expected = brute_force_max_subgraph_score(test_n, test_edges, test_good)
//         assert solution.maxSubgraphScore(test_n, test_edges, test_good) == expected

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
    vector<int> maxSubgraphScore(int n, vector<vector<int>>& edges, vector<int>& good) {
        vector<vector<int>> adj(n);
        for (auto& e : edges) {
            adj[e[0]].push_back(e[1]);
            adj[e[1]].push_back(e[0]);
        }
        vector<int> weight(n), parent(n, -1), order{0};
        for (int i = 0; i < n; ++i) weight[i] = good[i] == 1 ? 1 : -1;
        for (int node : order) for (int nei : adj[node]) if (nei != parent[node]) {
            parent[nei] = node;
            order.push_back(nei);
        }
        vector<int> down = weight;
        for (int idx = n - 1; idx >= 0; --idx) {
            int node = order[idx];
            for (int nei : adj[node]) if (parent[nei] == node) down[node] += max(0, down[nei]);
        }
        vector<int> ans(n);
        ans[0] = down[0];
        for (int node : order) for (int nei : adj[node]) if (parent[nei] == node) {
            int without = ans[node] - max(0, down[nei]);
            ans[nei] = down[nei] + max(0, without);
        }
        return ans;
    }
};
