#
# @lc app=leetcode id=623 lang=python3
#
# [623] Add One Row to Tree
#
# https://leetcode.com/problems/add-one-row-to-tree/description/
#
# algorithms
# Medium (64.12%)
# Likes:    3687
# Dislikes: 271
# Total Accepted:    304.7K
# Total Submissions: 475.1K
# Testcase Example:  '[4,2,6,3,1,5]\n1\n2'
#
# Given the root of a binary tree and two integers val and depth, add a row of
# nodes with value val at the given depth depth.
# 
# Note that the root node is at depth 1.
# 
# The adding rule is:
# 
# 
# Given the integer depth, for each not null tree node cur at the depth depth -
# 1, create two tree nodes with value val as cur's left subtree root and right
# subtree root.
# cur's original left subtree should be the left subtree of the new left
# subtree root.
# cur's original right subtree should be the right subtree of the new right
# subtree root.
# If depth == 1 that means there is no depth depth - 1 at all, then create a
# tree node with value val as the new root of the whole original tree, and the
# original tree is the new root's left subtree.
# 
# 
# 
# Example 1:
# 
# 
# Input: root = [4,2,6,3,1,5], val = 1, depth = 2
# Output: [4,1,1,2,null,null,6,3,1,5]
# 
# 
# Example 2:
# 
# 
# Input: root = [4,2,null,3,1], val = 1, depth = 3
# Output: [4,2,null,1,1,3,null,null,1]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 10^4].
# The depth of the tree is in the range [1, 10^4].
# -100 <= Node.val <= 100
# -10^5 <= val <= 10^5
# 1 <= depth <= the depth of tree + 1
# 
# 
#

# @lc code=start
from collections import deque
from typing import Optional


class Solution:
    def addOneRow(self, root: Optional['TreeNode'], val: int, depth: int) -> Optional['TreeNode']:
        if depth == 1:
            return TreeNode(val, root, None)

        q = deque([root])
        current_depth = 1
        while q and current_depth < depth - 1:
            for _ in range(len(q)):
                node = q.popleft()
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            current_depth += 1

        for node in q:
            old_left, old_right = node.left, node.right
            node.left = TreeNode(val, old_left, None)
            node.right = TreeNode(val, None, old_right)
        return root
# @lc code=end

"""
Interview explanation:
The only nodes that need modification are at depth - 1. BFS reaches that level, then each node receives a new left and right child. The old left subtree becomes the left child of the new left node; the old right subtree becomes the right child of the new right node.

Data structure: a queue supports level-order traversal.

Edge cases: inserting at depth 1 creates a new root. Missing children are preserved as None under the inserted nodes.

Complexity: O(n) time in the worst case to reach the insertion level and O(w) space for the widest BFS level.
"""
