// Translated from binary_tree_upside_down.py.
// Original Python source and explanation are preserved below as comments.
// # LeetCode 156. Binary Tree Upside Down
// # https://leetcode.com/problems/binary-tree-upside-down/
// 
// 
// class TreeNode:
//     def __init__(self, val=0, left=None, right=None):
//         self.val = val
//         self.left = left
//         self.right = right
// 
// 
// class Solution:
//     def upsideDownBinaryTree(self, root: TreeNode | None) -> TreeNode | None:
//         curr = root
//         parent = None
//         parent_right = None  # old right sibling of `parent` → becomes new left child
// 
//         while curr:
//             left = curr.left
//             right = curr.right
// 
//             curr.left = parent_right
//             curr.right = parent
// 
//             parent_right = right
//             parent = curr
//             curr = left
// 
//         return parent
// 
// 
// # Alternative: recursive (O(h) stack space)
// class SolutionRecursive:
//     def upsideDownBinaryTree(self, root: TreeNode | None) -> TreeNode | None:
//         if not root or not root.left:
//             return root
// 
//         new_root = self.upsideDownBinaryTree(root.left)
// 
//         root.left.left = root.right
//         root.left.right = root
//         root.left = None
//         root.right = None
// 
//         return new_root

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

#ifndef LOCAL_LEETCODE_STUBS
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int val = 0, TreeNode* left = nullptr, TreeNode* right = nullptr) : val(val), left(left), right(right) {}
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

class SolutionRecursive {
public:
    TreeNode* upsideDownBinaryTree(TreeNode* root) {
        if (!root || !root->left) return root;
        TreeNode* newRoot = upsideDownBinaryTree(root->left);
        root->left->left = root->right;
        root->left->right = root;
        root->left = nullptr;
        root->right = nullptr;
        return newRoot;
    }
};
