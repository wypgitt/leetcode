/*
 * @lc app=leetcode id=501 lang=cpp
 *
 * [501] Find Mode in Binary Search Tree
 */
// Translated from 501.find-mode-in-binary-search-tree.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=501 lang=python3
// #
// # [501] Find Mode in Binary Search Tree
// #
// # https://leetcode.com/problems/find-mode-in-binary-search-tree/description/
// #
// # algorithms
// # Easy (58.86%)
// # Likes:    4126
// # Dislikes: 816
// # Total Accepted:    396.3K
// # Total Submissions: 673.2K
// # Testcase Example:  '[1,null,2,2]'
// #
// # Given the root of a binary search tree (BST) with duplicates, return all the
// # mode(s) (i.e., the most frequently occurred element) in it.
// # 
// # If the tree has more than one mode, return them in any order.
// # 
// # Assume a BST is defined as follows:
// # 
// # 
// # The left subtree of a node contains only nodes with keys less than or equal
// # to the node's key.
// # The right subtree of a node contains only nodes with keys greater than or
// # equal to the node's key.
// # Both the left and right subtrees must also be binary search trees.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: root = [1,null,2,2]
// # Output: [2]
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: root = [0]
// # Output: [0]
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # The number of nodes in the tree is in the range [1, 10^4].
// # -10^5 <= Node.val <= 10^5
// # 
// # 
// # 
// # Follow up: Could you do that without using any extra space? (Assume that the
// # implicit stack space incurred due to recursion does not count).
// #
// 
// # lc-original code=start
// from typing import List, Optional
// 
// 
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def findMode(self, root: Optional["TreeNode"]) -> List[int]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given the root of a binary search tree that may contain duplicate
//         values.  We need return every value that appears the maximum number of
//         times.  Those values are called the modes.
// 
//         Example:
// 
//             [1, null, 2, 2]
// 
//         has values:
// 
//             1, 2, 2
// 
//         so the only mode is 2.
// 
//         Key BST property
//         ----------------
//         An in-order traversal of a BST visits values in non-decreasing sorted
//         order.
// 
//         That means all equal values appear consecutively in the traversal.
// 
//         Example traversal:
// 
//             1, 1, 2, 3, 3, 3, 4
// 
//         So we do not need a hash map from value to frequency.  We can count one
//         run of equal values at a time, just like counting duplicates in a sorted
//         array.
// 
//         Run-counting idea
//         -----------------
//         While visiting values in sorted order, maintain:
// 
//         * `previous_value`
//           The value visited immediately before the current one.
// 
//         * `current_count`
//           How many times the current value has appeared consecutively.
// 
//         * `max_count`
//           The best frequency seen so far.
// 
//         * `modes`
//           All values whose frequency equals `max_count`.
// 
//         When a value is visited:
// 
//         * if it equals `previous_value`, increment `current_count`
//         * otherwise, start a new run with `current_count = 1`
// 
//         Then compare `current_count` with `max_count`:
// 
//         * if greater, we found a new better frequency:
//               clear modes and store this value
// 
//         * if equal, this value is also a mode:
//               append it
// 
//         Why Morris traversal?
//         ---------------------
//         The straightforward solution is recursive in-order traversal.  That is
//         easy and accepted, but it uses recursion stack space.
// 
//         The follow-up asks whether we can avoid extra space, assuming recursion
//         stack does not count.  To go one step further, we can use Morris
//         traversal, which performs in-order traversal with O(1) extra space and
//         no recursion.
// 
//         Morris traversal temporarily links each node's in-order predecessor back
//         to the node, creating a "thread" that lets us return after finishing the
//         left subtree.  When that thread is encountered the second time, we remove
//         it, restoring the tree exactly.
// 
//         Morris traversal mechanics
//         --------------------------
//         For a current node:
// 
//         * If it has no left child:
//               visit it and move to its right child.
// 
//         * If it has a left child:
//               find its predecessor, the rightmost node in the left subtree.
// 
//               - If predecessor.right is None:
//                     set predecessor.right = current
//                     move current to current.left
// 
//               - If predecessor.right is current:
//                     remove the temporary link
//                     visit current
//                     move current to current.right
// 
//         Each edge is traversed only a constant number of times.
// 
//         Data structure choice
//         ---------------------
//         We do not use a Counter because the sorted order from the BST gives
//         frequencies by consecutive runs.  We only store:
// 
//         * a few scalar variables for counting
//         * the output list of modes
// 
//         The output list is not considered avoidable extra space because it is the
//         required return value.
// 
//         Algorithm
//         ---------
//         1. Initialize counting state:
// 
//                previous_value = None
//                has_previous = False
//                current_count = 0
//                max_count = 0
//                modes = []
// 
//         2. Morris-traverse the BST in in-order.
//         3. Every time a value is visited, update the run count and mode list.
//         4. Return `modes`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Morris traversal visits nodes in the same order as recursive
//         in-order traversal.
//         For each node, Morris traversal first processes its left subtree, then
//         the node, then its right subtree.  Temporary predecessor threads only
//         provide a way to return to the node after the left subtree; they do not
//         change the visit order.  Therefore the visit order is in-order.
// 
//         Lemma 2: The visited values are non-decreasing.
//         By the BST property, in-order traversal visits all values in sorted
//         non-decreasing order.  By Lemma 1, Morris traversal has that same order.
// 
//         Lemma 3: `current_count` is exactly the frequency of the current value's
//         consecutive run in the in-order sequence.
//         Because values are visited in non-decreasing order, equal values appear
//         consecutively.  The algorithm increments `current_count` when the current
//         value equals `previous_value`, and resets it to 1 when a new value
//         starts.  Thus it exactly tracks the current run length.
// 
//         Lemma 4: After each visited value, `modes` contains exactly the values
//         seen so far whose frequency equals `max_count`.
//         If `current_count` exceeds `max_count`, the current value is the only
//         value seen so far with this new best frequency, so the algorithm resets
//         `modes` to `[value]`.  If `current_count` equals `max_count`, the current
//         value also has best frequency and is appended.  If it is smaller, the
//         mode set does not change.
// 
//         Theorem: The algorithm returns all modes of the BST.
//         By Lemma 1 and Lemma 2, all values are processed in sorted order.  By
//         Lemma 3, their frequencies are counted correctly.  By Lemma 4, after all
//         nodes are processed, `modes` contains exactly the values with maximum
//         frequency.
// 
//         Complexity analysis
//         -------------------
//         Let n be the number of nodes.
// 
//         Morris traversal visits each node O(1) times and creates/removes each
//         temporary thread once.
// 
//         Total time:  O(n)
//         Extra space: O(1), excluding the output list
// 
//         Edge cases
//         ----------
//         * Single node:
//           That value appears once and is the only mode.
// 
//         * All values distinct:
//           Every value has frequency 1, so every value is a mode.
// 
//         * All values equal:
//           The single value's run grows to n, so it is the only mode.
// 
//         * Multiple modes:
//           Values with the same maximum frequency are all appended.
// 
//         * Negative values:
//           `None` plus `has_previous` avoids confusing an actual value with an
//           uninitialized previous value.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [1,null,2,2] -> [2]
//               [0]          -> [0]
// 
//         * All distinct values.
//         * All duplicate values.
//         * Several modes with equal frequency.
//         * A skewed tree, to show Morris traversal avoids recursion depth issues.
// 
//         Possible improvement?
//         ---------------------
//         A Counter-based traversal is simpler but uses O(n) extra space.  A
//         recursive in-order traversal uses O(h) call stack space.  Morris
//         traversal gives the strongest space bound while keeping linear time.
//         """
// 
//         modes: List[int] = []
//         previous_value: Optional[int] = None
//         has_previous = False
//         current_count = 0
//         max_count = 0
// 
//         def visit(value: int) -> None:
//             nonlocal previous_value, has_previous, current_count, max_count, modes
// 
//             if has_previous and value == previous_value:
//                 current_count += 1
//             else:
//                 previous_value = value
//                 has_previous = True
//                 current_count = 1
// 
//             if current_count > max_count:
//                 max_count = current_count
//                 modes = [value]
//             elif current_count == max_count:
//                 modes.append(value)
// 
//         current = root
//         while current:
//             if current.left is None:
//                 visit(current.val)
//                 current = current.right
//                 continue
// 
//             predecessor = current.left
//             while predecessor.right is not None and predecessor.right is not current:
//                 predecessor = predecessor.right
// 
//             if predecessor.right is None:
//                 predecessor.right = current
//                 current = current.left
//             else:
//                 predecessor.right = None
//                 visit(current.val)
//                 current = current.right
// 
//         return modes
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
    vector<int> findMode(TreeNode* root) {
        vector<int> modes;
        int prev = 0, curCount = 0, maxCount = 0;
        bool hasPrev = false;
        auto visit = [&](int value) {
            if (hasPrev && value == prev) ++curCount;
            else {
                prev = value;
                hasPrev = true;
                curCount = 1;
            }
            if (curCount > maxCount) {
                maxCount = curCount;
                modes = {value};
            } else if (curCount == maxCount) {
                modes.push_back(value);
            }
        };
        TreeNode* cur = root;
        while (cur) {
            if (!cur->left) {
                visit(cur->val);
                cur = cur->right;
            } else {
                TreeNode* pred = cur->left;
                while (pred->right && pred->right != cur) pred = pred->right;
                if (!pred->right) {
                    pred->right = cur;
                    cur = cur->left;
                } else {
                    pred->right = nullptr;
                    visit(cur->val);
                    cur = cur->right;
                }
            }
        }
        return modes;
    }
};
// @lc code=end
