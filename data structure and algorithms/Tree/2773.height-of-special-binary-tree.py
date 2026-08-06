#
# @lc app=leetcode id=2773 lang=python3
#
# [2773] Height of Special Binary Tree
#
# https://leetcode.com/problems/height-of-special-binary-tree/description/
#
# algorithms
# Medium (74.83%)
# Likes:    18
# Dislikes: 43
# Total Accepted:    1.5K
# Total Submissions: 2K
# Testcase Example:  "[1,2,3,null,null,4,5]"
#
#
# You are given a root, which is the root of a special binary tree with n
# nodes. The nodes of the special binary tree are numbered from 1 to n.
# Suppose the tree has k leaves in the following order: b_1 <_ b_2 < ... <
# b_k.
#
# The leaves of this tree have a special property! That is, for every leaf
# b_i, the following conditions hold:
#
# The right child of b_i is b_i + 1 if i < k, and b_1 otherwise.
#
# The left child of b_i is b_i - 1 if i > 1, and b_k otherwise.
#
# Return the height of the given tree.
#
# Note: The height of a binary tree is the length of the longest path from
# the root to any other node.
#
# Example 1:
#
# Input: root = [1,2,3,null,null,4,5]
# Output: 2
# Explanation: The given tree is shown in the following picture. Each
# leaf's left child is the leaf to its left (shown with the blue edges).
# Each leaf's right child is the leaf to its right (shown with the red
# edges). We can see that the graph has a height of 2.
#
# Example 2:
#
# Input: root = [1,2]
# Output: 1
# Explanation: The given tree is shown in the following picture. There is
# only one leaf, so it doesn't have any left or right child. We can see
# that the graph has a height of 1.
#
# Example 3:
#
# Input: root = [1,2,3,null,null,4,null,5,6]
# Output: 3
# Explanation: The given tree is shown in the following picture. Each
# leaf's left child is the leaf to its left (shown with the blue edges).
# Each leaf's right child is the leaf to its right (shown with the red
# edges). We can see that the graph has a height of 3.
#
# Constraints:
#
# n == number of nodes in the tree
#
# 2 <= n <= 10^4
#
# 1 <= node.val <= n
#
# The input is generated such that each node.val is unique.
#
# @lc code=start
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def heightOfTree(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Premium: special binary tree where each leaf's left points to right
        sibling and right to left sibling (cycle markers). Height = longest root
        path (edges), not following sibling back-edges.

        Algorithm:
        - DFS; recurse into left only if left.right != node; into right only if
          right.left != node. Track max depth.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node: Optional[TreeNode], d: int) -> None:
            nonlocal ans
            if not node:
                return
            ans = max(ans, d)
            if node.left and node.left.right is not node:
                dfs(node.left, d + 1)
            if node.right and node.right.left is not node:
                dfs(node.right, d + 1)

        dfs(root, 0)
        return ans
# @lc code=end
