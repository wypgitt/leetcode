#
# @lc app=leetcode id=1038 lang=python3
#
# [1038] Binary Search Tree to Greater Sum Tree
#
# https://leetcode.com/problems/binary-search-tree-to-greater-sum-tree/description/
#
# algorithms
# Medium (88.36%)
# Likes:    4572
# Dislikes: 169
# Total Accepted:    344.4K
# Total Submissions: 389.8K
# Testcase Example:  '[4,1,6,0,2,5,7,null,null,null,3,null,null,null,8]'
#
# Given the root of a Binary Search Tree (BST), convert it to a Greater Tree
# such that every key of the original BST is changed to the original key plus
# the sum of all keys greater than the original key in BST.
# 
# As a reminder, a binary search tree is a tree that satisfies these
# constraints:
# 
# 
# The left subtree of a node contains only nodes with keys less than the node's
# key.
# The right subtree of a node contains only nodes with keys greater than the
# node's key.
# Both the left and right subtrees must also be binary search trees.
# 
# 
# 
# Example 1:
# 
# 
# Input: root = [4,1,6,0,2,5,7,null,null,null,3,null,null,null,8]
# Output: [30,36,21,36,35,26,15,null,null,null,33,null,null,null,8]
# 
# 
# Example 2:
# 
# 
# Input: root = [0,null,1]
# Output: [1,null,1]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 100].
# 0 <= Node.val <= 100
# All the values in the tree are unique.
# 
# 
# 
# Note: This question is the same as 538:
# https://leetcode.com/problems/convert-bst-to-greater-tree/
# 
#

# @lc code=start
from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def bstToGst(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        running_sum = 0

        def reverse_inorder(node: Optional[TreeNode]) -> None:
            nonlocal running_sum
            if not node:
                return

            reverse_inorder(node.right)
            running_sum += node.val
            node.val = running_sum
            reverse_inorder(node.left)

        reverse_inorder(root)
        return root
# @lc code=end

"""
Interview Explanation

Core idea:
An inorder traversal of a BST visits values in ascending order. A reverse
inorder traversal visits values in descending order, which is exactly the order
needed to maintain the sum of all greater-or-equal values seen so far.

Algorithm:
1. Traverse right subtree first.
2. Add the current node's original value to running_sum.
3. Replace node.val with running_sum.
4. Traverse the left subtree.

Data structure choice:
The recursion stack follows the BST structure. A list of values would work,
but it would use extra memory and require a second pass.

Correctness:
When reverse inorder reaches a node, every node with a greater value has
already been visited and added to running_sum, while no smaller value has been
visited yet. Adding the current value makes running_sum equal to current value
plus all greater values, which is precisely the Greater Sum Tree value.

Complexity:
Each node is visited once, so time is O(n). Recursion uses O(h) stack space,
where h is the tree height.

Tests and edge cases:
- Single node: value stays the same.
- Right-skewed BST: traversal processes from largest back to root.
- Left-skewed BST: running sum accumulates as recursion unwinds.
- Value 0 is handled like any other value.
"""
