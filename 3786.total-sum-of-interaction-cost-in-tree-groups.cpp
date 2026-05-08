/*
 * @lc app=leetcode id=3786 lang=cpp
 *
 * [3786] Total Sum of Interaction Cost in Tree Groups
 */
// Translated from 3786.total-sum-of-interaction-cost-in-tree-groups.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3786 lang=python3
// #
// # [3786] Total Sum of Interaction Cost in Tree Groups
// #
// # https://leetcode.com/problems/total-sum-of-interaction-cost-in-tree-groups/description/
// #
// # algorithms
// # Hard (54.10%)
// # Likes:    71
// # Dislikes: 4
// # Total Accepted:    7.4K
// # Total Submissions: 13.8K
// # Testcase Example:  '3\n[[0,1],[1,2]]\n[1,1,1]'
// #
// # You are given an integer n and an undirected tree with n nodes numbered from
// # 0 to n - 1. This is represented by a 2D array edges of length n - 1, where
// # edges[i] = [ui, vi] indicates an undirected edge between nodes ui and vi.
// # 
// # You are also given an integer array group of length n, where group[i] denotes
// # the group label assigned to node i.
// # 
// # 
// # Two nodes u and v are considered part of the same group if group[u] ==
// # group[v].
// # The interaction cost between u and v is defined as the number of edges on the
// # unique path connecting them in the tree.
// # 
// # 
// # Return an integer denoting the sum of interaction costs over all unordered
// # pairs (u, v) with u != v such that group[u] == group[v].
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 3, edges = [[0,1],[1,2]], group = [1,1,1]
// # 
// # Output: 4
// # 
// # Explanation:
// # 
// # 
// # 
// # All nodes belong to group 1. The interaction costs between the pairs of nodes
// # are:
// # 
// # 
// # Nodes (0, 1): 1
// # Nodes (1, 2): 1
// # Nodes (0, 2): 2
// # 
// # 
// # Thus, the total interaction cost is 1 + 1 + 2 = 4.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 3, edges = [[0,1],[1,2]], group = [3,2,3]
// # 
// # Output: 2
// # 
// # Explanation:
// # 
// # 
// # Nodes 0 and 2 belong to group 3. The interaction cost between this pair is
// # 2.
// # Node 1 belongs to a different group and forms no valid pair. Therefore, the
// # total interaction cost is 2.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: n = 4, edges = [[0,1],[0,2],[0,3]], group = [1,1,4,4]
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # 
// # Nodes belonging to the same groups and their interaction costs are:
// # 
// # 
// # Group 1: Nodes (0, 1): 1
// # Group 4: Nodes (2, 3): 2
// # 
// # 
// # Thus, the total interaction cost is 1 + 2 = 3.
// # 
// # 
// # Example 4:
// # 
// # 
// # Input: n = 2, edges = [[0,1]], group = [9,8]
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # All nodes belong to different groups and there are no valid pairs. Therefore,
// # the total interaction cost is 0.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 10^5
// # edges.length == n - 1
// # edges[i] = [ui, vi]
// # 0 <= ui, vi <= n - 1
// # group.length == n
// # 1 <= group[i] <= 20
// # The input is generated such that edges represents a valid tree.
// # 
// # 
// #
// 
// # lc-original code=start
// from collections import deque
// from typing import List
// 
// 
// class Solution:
//     def interactionCosts(self, n: int, edges: List[List[int]], group: List[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given a tree with `n` nodes.  Each node has a group label.
// 
//         For every unordered pair of different nodes `(u, v)` with:
// 
//             group[u] == group[v]
// 
//         we add the distance between `u` and `v`, where distance means the number
//         of edges on the unique path between them.
// 
//         Return the total sum.
// 
//         Why not compute every pair directly?
//         ------------------------------------
//         In the worst case, all nodes have the same group.  Then there are:
// 
//             n * (n - 1) / 2
// 
//         valid pairs.  With `n <= 10^5`, checking all pairs is too slow.
// 
//         We need to count distances in aggregate.
// 
//         Key observation: edge contribution
//         ----------------------------------
//         The distance between two nodes is the number of edges on their path.
// 
//         Instead of asking:
// 
//             "For each pair, how many edges are on its path?"
// 
//         flip the counting:
// 
//             "For each edge, how many same-group pairs have a path crossing this
//              edge?"
// 
//         If an edge separates the tree into two sides, then a pair's path crosses
//         that edge exactly when one endpoint is on one side and the other endpoint
//         is on the other side.
// 
//         For a group label `g`:
// 
//             count_on_one_side = x
//             total_count_of_group_g = total[g]
// 
//         Then the number of same-group pairs crossing this edge is:
// 
//             x * (total[g] - x)
// 
//         Every such pair contributes 1 to the total distance for this edge.
// 
//         Summing this over every edge and every group gives the answer.
// 
//         Why root the tree?
//         ------------------
//         Root the tree at node 0.
// 
//         For an edge between a parent and a child, removing that edge splits the
//         tree into:
// 
//         * the child's subtree
//         * the rest of the tree
// 
//         So for each child subtree, if we know how many nodes of every group are
//         inside it, we can compute that edge's contribution immediately.
// 
//         Data structure choice
//         ---------------------
//         Group labels are small:
// 
//             1 <= group[i] <= 20
// 
//         So for each node we store an array of 21 counts:
// 
//             subtree_counts[node][g]
// 
//         meaning:
// 
//             number of nodes with group `g` in this node's rooted subtree
// 
//         We use index 1 through 20 and ignore index 0.  This is simpler and
//         faster than dictionaries because the group-label range is fixed and tiny.
// 
//         We also avoid recursive DFS because `n` can be `10^5`, which can exceed
//         Python's recursion limit.  Instead, we build a parent/order list
//         iteratively and process nodes in reverse order.
// 
//         Algorithm
//         ---------
//         1. Build the adjacency list.
//         2. Count `total[g]`, the total number of nodes in each group.
//         3. Root the tree at 0 using an iterative DFS/BFS:
//               * store each node's parent
//               * store traversal order
//         4. Process nodes in reverse traversal order, so children are processed
//            before parents:
//               a. Start the node's count with its own group.
//               b. Its child counts have already been accumulated into it.
//               c. If this node has a parent, the edge `(parent[node], node)` has
//                  one side equal to this node's subtree.
//               d. For every group `g`, add:
// 
//                      subtree_count[g] * (total[g] - subtree_count[g])
// 
//                  to the answer.
//               e. Add this node's subtree counts into its parent's counts.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For any edge, the number of same-group pairs whose path crosses
//         that edge is:
// 
//             sum over groups g of side_count[g] * (total[g] - side_count[g])
// 
//         Removing the edge splits the tree into two components.  A path crosses
//         the edge exactly when its endpoints are in different components.  For
//         group `g`, there are `side_count[g]` choices on one side and
//         `total[g] - side_count[g]` choices on the other side.  Multiplying counts
//         all same-group pairs crossing that edge for group `g`.
// 
//         Lemma 2: When processing node `u` in reverse traversal order,
//         `subtree_counts[u][g]` equals the number of group-`g` nodes in `u`'s
//         rooted subtree.
//         Reverse order processes every child before its parent.  Each node first
//         contributes its own group count, then all already-computed child subtree
//         counts are added into it.  Therefore the final count at `u` is exactly
//         the count over its whole subtree.
// 
//         Lemma 3: For every non-root node `u`, the algorithm computes the correct
//         contribution of edge `(parent[u], u)`.
//         Removing this edge separates the tree into `u`'s subtree and the rest of
//         the tree.  By Lemma 2, the algorithm knows the exact group counts on the
//         subtree side.  By Lemma 1, the formula used by the algorithm is exactly
//         the number of same-group paths crossing that edge.
// 
//         Theorem: The algorithm returns the total interaction cost over all
//         same-group pairs.
//         The distance of a pair equals the number of edges on its path.  By
//         Lemma 3, each edge contributes exactly the number of same-group pairs
//         whose paths contain it.  Summing over all edges therefore counts each
//         same-group pair once per edge on its path, which is exactly its distance.
// 
//         Complexity analysis
//         -------------------
//         Let `G = 20`, the maximum number of possible groups.
// 
//         Building the tree:
// 
//             O(n)
// 
//         Traversal:
// 
//             O(n)
// 
//         Processing subtree counts:
// 
//             O(n * G)
// 
//         Since `G` is a fixed constant, this is effectively:
// 
//             O(n)
// 
//         Space:
// 
//             O(n * G)
// 
//         for the subtree count table, plus O(n) for adjacency, parent, and order.
// 
//         Edge cases
//         ----------
//         * n = 1:
//           There are no unordered pairs, so the answer is 0.
// 
//         * All nodes have different groups:
//           Every `total[g]` is at most 1, so all edge contributions are zero.
// 
//         * All nodes have the same group:
//           The formula becomes the classic sum of all pairwise tree distances.
// 
//         * Star-shaped tree:
//           Each leaf-subtree count is small, and the formula still works.
// 
//         * Chain-shaped tree:
//           Iterative traversal avoids recursion-depth errors.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               n = 3, path, groups [1,1,1] -> 4
//               n = 3, path, groups [3,2,3] -> 2
//               n = 4, star, groups [1,1,4,4] -> 3
//               n = 2, one edge, groups [9,8] -> 0
// 
//         * Single node.
//         * All groups equal.
//         * All groups different.
//         * Small trees compared against brute-force pair distance computation.
// 
//         Possible improvement
//         --------------------
//         Because there are only 20 group labels, the fixed-array approach is both
//         simple and fast.  If group labels were very large and sparse, we could
//         use dictionaries per subtree, but that would add overhead for this
//         constraint.
//         """
// 
//         if n == 1:
//             return 0
// 
//         adjacency = [[] for _ in range(n)]
//         for first, second in edges:
//             adjacency[first].append(second)
//             adjacency[second].append(first)
// 
//         total = [0] * 21
//         for label in group:
//             total[label] += 1
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
//         subtree_counts = [[0] * 21 for _ in range(n)]
//         answer = 0
// 
//         for node in reversed(order):
//             counts = subtree_counts[node]
//             counts[group[node]] += 1
// 
//             if node != 0:
//                 for label in range(1, 21):
//                     inside = counts[label]
//                     answer += inside * (total[label] - inside)
// 
//                 parent_counts = subtree_counts[parent[node]]
//                 for label in range(1, 21):
//                     parent_counts[label] += counts[label]
// 
//         return answer
// # lc-original code=end
// 
// 
// if __name__ == "__main__":
//     def brute_force_interaction_costs(
//         test_n: int,
//         test_edges: List[List[int]],
//         test_group: List[int],
//     ) -> int:
//         adjacency = [[] for _ in range(test_n)]
//         for first, second in test_edges:
//             adjacency[first].append(second)
//             adjacency[second].append(first)
// 
//         def distance(start: int, target: int) -> int:
//             queue = deque([(start, 0)])
//             seen = {start}
// 
//             while queue:
//                 node, dist = queue.popleft()
//                 if node == target:
//                     return dist
// 
//                 for neighbor in adjacency[node]:
//                     if neighbor not in seen:
//                         seen.add(neighbor)
//                         queue.append((neighbor, dist + 1))
// 
//             raise RuntimeError("tree should be connected")
// 
//         total_cost = 0
//         for first in range(test_n):
//             for second in range(first + 1, test_n):
//                 if test_group[first] == test_group[second]:
//                     total_cost += distance(first, second)
// 
//         return total_cost
// 
//     solution = Solution()
// 
//     fixed_tests = [
//         (3, [[0, 1], [1, 2]], [1, 1, 1], 4),
//         (3, [[0, 1], [1, 2]], [3, 2, 3], 2),
//         (4, [[0, 1], [0, 2], [0, 3]], [1, 1, 4, 4], 3),
//         (2, [[0, 1]], [9, 8], 0),
//         (1, [], [7], 0),
//     ]
// 
//     for test_n, test_edges, test_group, expected in fixed_tests:
//         assert solution.interactionCosts(test_n, test_edges, test_group) == expected
// 
//     brute_force_cases = [
//         (5, [[0, 1], [1, 2], [1, 3], [3, 4]], [1, 2, 1, 2, 1]),
//         (6, [[0, 1], [0, 2], [2, 3], [2, 4], [4, 5]], [5, 5, 5, 6, 6, 5]),
//         (5, [[0, 1], [0, 2], [0, 3], [0, 4]], [1, 2, 3, 4, 5]),
//         (5, [[0, 1], [1, 2], [2, 3], [3, 4]], [1, 1, 1, 1, 1]),
//     ]
// 
//     for test_n, test_edges, test_group in brute_force_cases:
//         expected = brute_force_interaction_costs(test_n, test_edges, test_group)
//         assert solution.interactionCosts(test_n, test_edges, test_group) == expected

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
    long long interactionCosts(int n, vector<vector<int>>& edges, vector<int>& group) {
        if (n == 1) return 0;
        vector<vector<int>> adj(n);
        for (auto& e : edges) {
            adj[e[0]].push_back(e[1]);
            adj[e[1]].push_back(e[0]);
        }
        vector<int> total(21);
        for (int x : group) ++total[x];
        vector<int> parent(n, -1), order{0};
        for (int node : order) for (int nei : adj[node]) if (nei != parent[node]) {
            parent[nei] = node;
            order.push_back(nei);
        }
        vector<array<long long, 21>> sub(n);
        long long ans = 0;
        for (int idx = n - 1; idx >= 0; --idx) {
            int node = order[idx];
            ++sub[node][group[node]];
            if (node != 0) {
                for (int label = 1; label <= 20; ++label) ans += sub[node][label] * (total[label] - sub[node][label]);
                for (int label = 1; label <= 20; ++label) sub[parent[node]][label] += sub[node][label];
            }
        }
        return ans;
    }
};
// @lc code=end
