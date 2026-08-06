#
# @lc app=leetcode id=257 lang=python3
#
# [257] Binary Tree Paths
#
# https://leetcode.com/problems/binary-tree-paths/description/
#
# algorithms
# Easy (69.11%)
# Likes:    7334
# Dislikes: 355
# Total Accepted:    1.1M
# Total Submissions: 1.5M
# Testcase Example:  "[1,2,3,null,5]"
#
# Given the root of a binary tree, return all root-to-leaf paths in any order.
#
# A leaf is a node with no children.
#
# Example 1:
#
# Input: root = [1,2,3,null,5]
# Output: ["1->2->5","1->3"]
#
# Example 2:
#
# Input: root = [1]
# Output: ["1"]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 100].
#
# -100 <= Node.val <= 100
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
    def binaryTreePaths(self, root: Optional[TreeNode]) -> List[str]:
        """
        Interview explanation:
        DFS from root to each leaf, accumulating node values; at a leaf, join
        the path with "->" and record it.

        Algorithm:
        - DFS(node, path list); append node.val.
        - If leaf, join path into answer; else recurse children.
        - Backtrack by popping.

        Complexity: O(n) time to visit; O(n * h) space for paths output / recursion.
        """
        ans: List[str] = []

        def dfs(node: TreeNode, path: List[str]) -> None:
            path.append(str(node.val))
            if not node.left and not node.right:
                ans.append("->".join(path))
            else:
                if node.left:
                    dfs(node.left, path)
                if node.right:
                    dfs(node.right, path)
            path.pop()

        if root:
            dfs(root, [])
        return ans
# @lc code=end
