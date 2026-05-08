// Translated from 3879.maximum-distinct-path-sum-in-a-binary-tree.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3879 lang=python3
// #
// # [3879] Maximum Distinct Path Sum in a Binary Tree
// #
// # https://leetcode.com/problems/maximum-distinct-path-sum-in-a-binary-tree/description/
// #
// # algorithms
// # Medium (57.27%)
// # Likes:    3
// # Dislikes: 2
// # Total Accepted:    328
// # Total Submissions: 572
// # Testcase Example:  '[2,2,1]'
// #
// # You are given the root of a binary tree, where each node contains an integer
// # value.
// # 
// # A valid path in the tree is a sequence of connected nodes such that:
// # 
// # 
// # The path can start and end at any node in the tree.
// # The path does not need to pass through the root.
// # All node values along the path are distinct.
// # 
// # 
// # Return an integer denoting the maximum possible sum of node values among all
// # valid paths.
// # 
// # 
// # Example 1:
// # 
// # 
// # 
// # 
// # Input: root = [2,2,1]
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # The path 2 → 2 is invalid because the value 2 is not distinct.
// # The maximum-sum valid path is 2 → 1, with a sum = 2 + 1 = 3.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # 
// # 
// # Input: root = [1,-2,5,null,null,3,5]
// # 
// # Output: 9
// # 
// # Explanation:
// # 
// # 
// # The path 3 → 5 → 5 is invalid due to duplicate value 5.
// # The maximum-sum valid path is 1 → 5 → 3, with a sum = 1 + 5 + 3 = 9.
// # 
// # 
// # 
// # Example 3:
// # 
// # ​​​​​​​
// # 
// # 
// # Input: root = [4,6,6,null,null,null,9]
// # 
// # Output: 19
// # 
// # Explanation:
// # 
// # 
// # The path 6 → 4 → 6 → 9 is invalid because the value 6 appears more than
// # once.
// # The maximum-sum valid path is 4 → 6 → 9, with a sum = 4 + 6 + 9 = 19.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # The number of nodes in the tree is in the range [1, 1000].
// # -1000 <= Node.val <= 1000​​​​​​​
// # 
// # 
// #
// 
// # @lc code=start
// from typing import Optional
// 
// 
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def maxSum(self, root: Optional["TreeNode"]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given a binary tree.  A valid path:
// 
//         * can start at any node
//         * can end at any node
//         * follows parent-child edges
//         * does not need to pass through the root
//         * must contain distinct node values
// 
//         We need the maximum possible sum among all valid paths.
// 
//         Important details
//         -----------------
//         This is NOT the classic "maximum path sum" problem.  In the classic
//         version, a path can use any values and we usually combine the best
//         downward path from the left and right child.
// 
//         Here, distinct values are required.  That means whether we can extend a
//         path depends on the entire set of values already on the path, not only on
//         the best sum.  Because of that, a simple local tree DP is not enough.
// 
//         Key observation: n is small enough for path enumeration
//         ------------------------------------------------------
//         The tree has at most 1000 nodes.
// 
//         In a tree, there is exactly one simple path between any two nodes.  So if
//         we start a DFS from every node and walk outward without revisiting the
//         parent, we enumerate every possible simple path at least once.  While
//         walking, we keep a set of values already used in the current path.  If a
//         neighbor's value is already in the set, extending to that neighbor would
//         violate the distinct-value condition, so we stop that branch.
// 
//         This direct approach is clear, reliable, and fast enough:
// 
//             1000 starts * up to 1000 visited nodes per start = 1,000,000 visits
// 
//         which is easily acceptable.
// 
//         Why convert the tree to a graph?
//         --------------------------------
//         A path can go:
// 
//         * down from parent to child
//         * up from child to parent
//         * through an ancestor and then down another branch
// 
//         Tree nodes only store child pointers, not parent pointers.  To start a
//         DFS from any node and move in all possible directions, we first convert
//         the tree into an undirected adjacency list.
// 
//         Data structures
//         ---------------
//         * `values[index]`
//           Stores each node's value by compact integer index.
// 
//         * `graph[index]`
//           Stores neighboring node indices.  Since this is a binary tree made
//           undirected, each node has at most three neighbors: left child, right
//           child, and parent.
// 
//         * `used_values`
//           A set of values on the current DFS path.  This lets us test in O(1)
//           average time whether adding the next node would create a duplicate.
// 
//         Algorithm
//         ---------
//         1. Traverse the tree once and assign each TreeNode a compact index.
//         2. Build an undirected adjacency list.
//         3. Initialize `answer` to negative infinity, because node values can be
//            negative and the best path might be a single negative node.
//         4. For every node as a starting point:
//               - start DFS with that node's value in `used_values`
//               - update `answer` with the current path sum
//               - try every neighbor except the node we came from
//               - only continue if the neighbor's value is not in `used_values`
//         5. Return `answer`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Every path explored by the DFS is valid.
//         The DFS moves only along graph edges, which correspond exactly to
//         parent-child tree edges.  It avoids immediately returning to the parent,
//         so each explored sequence is a simple path.  Before adding a neighbor,
//         the DFS checks that the neighbor's value is not already in
//         `used_values`, so all values on the path remain distinct.
// 
//         Lemma 2: Every valid path in the tree is explored by the algorithm.
//         Consider any valid path with endpoints `u` and `v`.  The outer loop
//         eventually starts a DFS from `u`.  In a tree, there is exactly one simple
//         route from `u` to `v`, and that route is the path itself.  Since the path
//         has distinct values, every step along it passes the `used_values` check.
//         Therefore the DFS from `u` explores the full path to `v`.
// 
//         Lemma 3: Whenever a valid path is explored, the algorithm considers its
//         sum for the answer.
//         At every DFS state, `current_sum` is the sum of values on the current
//         path.  The algorithm updates `answer` at every state, so the sum of each
//         explored path is considered.
// 
//         Theorem: The algorithm returns the maximum valid path sum.
//         By Lemma 1, every considered path is valid.  By Lemma 2, every valid path
//         is considered.  By Lemma 3, every considered path's sum is compared into
//         `answer`.  Therefore `answer` is exactly the maximum sum over all valid
//         paths.
// 
//         Complexity analysis
//         -------------------
//         Let n be the number of nodes.
// 
//         Building the graph costs O(n) time and O(n) space.
// 
//         For each starting node, the DFS can visit at most n nodes before either
//         reaching leaves or stopping at duplicate values.  In the worst case, all
//         values are distinct, so each start visits the whole tree.
// 
//         Total time:  O(n^2)
//         Total space: O(n)
// 
//         The O(n) space includes the graph, node values, recursion stack, and
//         current `used_values` set.
// 
//         Why this is acceptable
//         ----------------------
//         With n <= 1000, O(n^2) is at most about one million DFS states, which is
//         comfortably small.  A more complex algorithm would not be worth the
//         added risk for these constraints.
// 
//         Edge cases
//         ----------
//         * Single node:
//           The only valid path is that node, even if its value is negative.
// 
//         * All values equal:
//           No path of length greater than one is valid, so the answer is the
//           maximum single-node value.
// 
//         * Negative values:
//           We cannot initialize answer to 0, because all path sums could be
//           negative.  A path must contain at least one node.
// 
//         * Duplicate values in different branches:
//           A path may include one of them, but not both.
// 
//         * Best path does not pass through the root:
//           Starting DFS from every node naturally covers paths anywhere in the
//           tree.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [2,2,1]                 -> 3
//               [1,-2,5,null,null,3,5]  -> 9
//               [4,6,6,null,null,null,9] -> 19
// 
//         * Single negative node:
//               [-5] -> -5
// 
//         * All equal values:
//               [2,2,2] -> 2
// 
//         * A path crossing through an ancestor:
//               left leaf -> parent -> right leaf
// 
//         * Random small trees:
//           Compare against brute-force enumeration of all node pairs.
// 
//         Possible improvement?
//         ---------------------
//         For much larger trees, we would need a more advanced technique.  Because
//         values are bounded from -1000 to 1000, one could imagine more specialized
//         state compression, but paths in trees with distinct-value constraints are
//         still tricky to merge safely.  For n <= 1000, exhaustive DFS from every
//         start is the best balance of correctness, simplicity, and performance.
//         """
// 
//         node_to_index: dict[object, int] = {}
//         values: list[int] = []
//         graph: list[list[int]] = []
// 
//         def add_node(node: TreeNode) -> int:
//             if node in node_to_index:
//                 return node_to_index[node]
// 
//             index = len(values)
//             node_to_index[node] = index
//             values.append(node.val)
//             graph.append([])
//             return index
// 
//         stack = [root]
//         while stack:
//             node = stack.pop()
//             if node is None:
//                 continue
// 
//             index = add_node(node)
// 
//             if node.left:
//                 left_index = add_node(node.left)
//                 graph[index].append(left_index)
//                 graph[left_index].append(index)
//                 stack.append(node.left)
// 
//             if node.right:
//                 right_index = add_node(node.right)
//                 graph[index].append(right_index)
//                 graph[right_index].append(index)
//                 stack.append(node.right)
// 
//         answer = -10**18
// 
//         def dfs(node: int, parent: int, current_sum: int, used_values: set[int]) -> None:
//             nonlocal answer
// 
//             answer = max(answer, current_sum)
// 
//             for neighbor in graph[node]:
//                 if neighbor == parent:
//                     continue
// 
//                 neighbor_value = values[neighbor]
//                 if neighbor_value in used_values:
//                     continue
// 
//                 used_values.add(neighbor_value)
//                 dfs(neighbor, node, current_sum + neighbor_value, used_values)
//                 used_values.remove(neighbor_value)
// 
//         for start in range(len(values)):
//             dfs(start, -1, values[start], {values[start]})
// 
//         return answer
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
    long long maxSum(TreeNode* root) {
        map<TreeNode*, int> id;
        vector<int> values;
        vector<vector<int>> graph;
        auto add = [&](TreeNode* node) {
            if (id.count(node)) return id[node];
            int idx = values.size();
            id[node] = idx;
            values.push_back(node->val);
            graph.push_back({});
            return idx;
        };
        vector<TreeNode*> st{root};
        while (!st.empty()) {
            TreeNode* node = st.back();
            st.pop_back();
            if (!node) continue;
            int idx = add(node);
            if (node->left) {
                int li = add(node->left);
                graph[idx].push_back(li);
                graph[li].push_back(idx);
                st.push_back(node->left);
            }
            if (node->right) {
                int ri = add(node->right);
                graph[idx].push_back(ri);
                graph[ri].push_back(idx);
                st.push_back(node->right);
            }
        }
        long long ans = LLONG_MIN;
        function<void(int, int, long long, unordered_set<int>&)> dfs = [&](int u, int parent, long long sum, unordered_set<int>& used) {
            ans = max(ans, sum);
            for (int v : graph[u]) {
                if (v == parent || used.count(values[v])) continue;
                used.insert(values[v]);
                dfs(v, u, sum + values[v], used);
                used.erase(values[v]);
            }
        };
        for (int i = 0; i < (int)values.size(); ++i) {
            unordered_set<int> used{values[i]};
            dfs(i, -1, values[i], used);
        }
        return ans;
    }
};
