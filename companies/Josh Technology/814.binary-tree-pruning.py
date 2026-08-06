#
# @lc app=leetcode id=814 lang=python3
#
# [814] Binary Tree Pruning
#
# https://leetcode.com/problems/binary-tree-pruning/description/
#
# algorithms
# Medium (72.55%)
# Likes:    4688
# Dislikes: 122
# Total Accepted:    293K
# Total Submissions: 403K
# Testcase Example:  "[1,null,0,0,1]"
#
# Given the root of a binary tree, return the same tree where every subtree (of
# the given tree) not containing a 1 has been removed.
#
# A subtree of a node node is node plus every node that is a descendant of
# node.
#
# Example 1:
#
# Input: root = [1,null,0,0,1]
# Output: [1,null,0,null,1]
# Explanation:
# Only the red nodes satisfy the property "every subtree not containing a 1".
# The diagram on the right represents the answer.
#
# Example 2:
#
# Input: root = [1,0,1,0,0,0,1]
# Output: [1,null,1,null,1]
#
# Example 3:
#
# Input: root = [1,1,0,1,1,0,1,0]
# Output: [1,1,0,1,1,null,1]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 200].
#
# Node.val is either 0 or 1.
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
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def pruneTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Post-order: prune left/right first; delete a node if its subtree has no
        1 (node.val==0 and both children None after prune).

        Algorithm:
        - dfs(node): recurse children; if node is None or (val==0 and no kids)
          return None else return node.

        Complexity: O(n) time, O(h) space.
        """
        if not root:
            return None
        root.left = self.pruneTree(root.left)
        root.right = self.pruneTree(root.right)
        if root.val == 0 and not root.left and not root.right:
            return None
        return root
# @lc code=end
