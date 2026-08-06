#
# @lc app=leetcode id=545 lang=python3
#
# [545] Boundary of Binary Tree
#
# https://leetcode.com/problems/boundary-of-binary-tree/description/
#
# algorithms
# Medium (48.17%)
# Likes:    1422
# Dislikes: 2354
# Total Accepted:    178.3K
# Total Submissions: 370.2K
# Testcase Example:  "[1,null,2,3,4]"
#
#
# The boundary of a binary tree is the concatenation of the root, the left
# boundary, the leaves ordered from left-to-right, and the reverse order
# of the right boundary.
#
# The left boundary is the set of nodes defined by the following:
#
# The root node's left child is in the left boundary. If the root does not
# have a left child, then the left boundary is empty.
#
# If a node is in the left boundary and has a left child, then the left
# child is in the left boundary.
#
# If a node is in the left boundary, has no left child, but has a right
# child, then the right child is in the left boundary.
#
# The leftmost leaf is not in the left boundary.
#
# The right boundary is similar to the left boundary, except it is the
# right side of the root's right subtree. Again, the leaf is not part of
# the right boundary, and the right boundary is empty if the root does not
# have a right child.
#
# The leaves are nodes that do not have any children. For this problem,
# the root is not a leaf.
#
# Given the root of a binary tree, return the values of its boundary.
#
# Example 1:
#
# Input: root = [1,null,2,3,4]
# Output: [1,3,4,2]
# Explanation:
# - The left boundary is empty because the root does not have a left
# child.
# - The right boundary follows the path starting from the root's right
# child 2 -> 4.
#   4 is a leaf, so the right boundary is [2].
# - The leaves from left to right are [3,4].
# Concatenating everything results in [1] + [] + [3,4] + [2] = [1,3,4,2].
#
# Example 2:
#
# Input: root = [1,2,3,4,5,6,null,null,null,7,8,9,10]
# Output: [1,2,4,7,8,9,10,6,3]
# Explanation:
# - The left boundary follows the path starting from the root's left child
# 2 -> 4.
#   4 is a leaf, so the left boundary is [2].
# - The right boundary follows the path starting from the root's right
# child 3 -> 6 -> 10.
#   10 is a leaf, so the right boundary is [3,6], and in reverse order is
# [6,3].
# - The leaves from left to right are [4,7,8,9,10].
# Concatenating everything results in [1] + [2] + [4,7,8,9,10] + [6,3] =
# [1,2,4,7,8,9,10,6,3].
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -1000 <= Node.val <= 1000
#
# @lc code=start
from typing import List, Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def boundaryOfBinaryTree(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Anti-clockwise boundary = root + left boundary (no leaves) + all leaves
        left-to-right + right boundary bottom-up (no leaves). Handle missing
        sides carefully so root/leaves are not duplicated.

        Algorithm:
        - Collect left edge (prefer left child, else right) excluding leaves.
        - DFS collect leaves.
        - Collect right edge similarly into a stack, reverse when appending.
        - Concatenate: [root] + left + leaves + right (skip root if leaf-only).

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return []

        def is_leaf(node: TreeNode) -> bool:
            return not node.left and not node.right

        def left_boundary(node: Optional[TreeNode]) -> List[int]:
            res = []
            while node:
                if not is_leaf(node):
                    res.append(node.val)
                node = node.left if node.left else node.right
            return res

        def right_boundary(node: Optional[TreeNode]) -> List[int]:
            res = []
            while node:
                if not is_leaf(node):
                    res.append(node.val)
                node = node.right if node.right else node.left
            return res[::-1]

        def leaves(node: Optional[TreeNode], res: List[int]) -> None:
            if not node:
                return
            if is_leaf(node):
                res.append(node.val)
                return
            leaves(node.left, res)
            leaves(node.right, res)

        if is_leaf(root):
            return [root.val]

        leaf_vals: List[int] = []
        leaves(root, leaf_vals)
        left = left_boundary(root.left)
        right = right_boundary(root.right)
        return [root.val] + left + leaf_vals + right
# @lc code=end

