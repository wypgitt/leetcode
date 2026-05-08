// Translated from 156.binary-tree-upside-down.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=156 lang=python3
// #
// # [156] Binary Tree Upside Down
// #
// # Problem (one level):
// #   Given a node with left child L and right child R, “flip” this triangle so that
// #   L becomes the new root, R becomes L’s new left child, and the old root becomes
// #   L’s new right child.
// #
// # Why iteration along the left spine works:
// #   The guarantee (every right node has a left sibling and no children) means the
// #   tree is effectively a chain along the left edge with optional right “buds”.
// #   Processing from the original root downward is the same as flipping level by
// #   level from top to bottom; each step only needs the previous parent and that
// #   parent’s old right child to wire the new left/right pointers.
// #
// # Variables:
// #   curr          — node we are rewiring this iteration (walking left).
// #   parent        — the node that was above curr in the original tree; becomes
// #                   curr’s new right child after the flip at this step.
// #   parent_right  — the old right child of `parent` (sibling of curr in the
// #                   original tree); becomes curr’s new left child. For the first
// #                   node we process, there is no such sibling yet, so None.
// 
// # @lc code=start
// from typing import Optional
// 
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
//         curr = root
//         parent = None
//         parent_right = None
// 
//         while curr:
//             # Save children before we overwrite pointers.
//             left = curr.left
//             right = curr.right
// 
//             # Apply the upside-down rule for this node:
//             # new left  = old right sibling of the node above (None on first step)
//             # new right = old parent
//             curr.left = parent_right
//             curr.right = parent
// 
//             # Advance: next node down the left spine; carry flip context upward.
//             parent_right = right
//             parent = curr
//             curr = left
// 
//         # Last processed node was the old leftmost node — it is the new root.
//         return parent
// 
// # @lc code=end
// 

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
    TreeNode* upsideDownBinaryTree(TreeNode* root) {
        TreeNode* curr = root;
        TreeNode* parent = nullptr;
        TreeNode* parentRight = nullptr;
        while (curr) {
            TreeNode* left = curr->left;
            TreeNode* right = curr->right;
            curr->left = parentRight;
            curr->right = parent;
            parentRight = right;
            parent = curr;
            curr = left;
        }
        return parent;
    }
};
