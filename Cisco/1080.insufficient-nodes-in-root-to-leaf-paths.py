#
# @lc app=leetcode id=1080 lang=python3
#
# [1080] Insufficient Nodes in Root to Leaf Paths
#
# https://leetcode.com/problems/insufficient-nodes-in-root-to-leaf-paths/description/
#
# algorithms
# Medium (55.42%)
# Likes:    763
# Dislikes: 751
# Total Accepted:    52.8K
# Total Submissions: 95.3K
# Testcase Example:  "[1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14]"
#
# Given the root of a binary tree and an integer limit, delete all insufficient
# nodes in the tree simultaneously, and return the root of the resulting binary
# tree.
#
# A node is insufficient if every root to leaf path intersecting this node has
# a sum strictly less than limit.
#
# A leaf is a node with no children.
#
# Example 1:
#
# Input: root = [1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14], limit = 1
# Output: [1,2,3,4,null,null,7,8,9,null,14]
#
# Example 2:
#
# Input: root = [5,4,8,11,null,17,4,7,1,null,null,5,3], limit = 22
# Output: [5,4,8,11,null,17,4,7,null,null,null,5]
#
# Example 3:
#
# Input: root = [1,2,-3,-5,null,4,null], limit = -1
# Output: [1,null,-3,4]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 5000].
#
# -10^5 <= Node.val <= 10^5
#
# -10^9 <= limit <= 10^9
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
    def sufficientSubset(self, root: Optional[TreeNode], limit: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        A node is insufficient if every root-to-leaf path through it sums
        < limit. Postorder: prune children first; a leaf survives only if
        path sum ≥ limit; an internal node survives if any child remains.

        Algorithm (DFS prune):
        - dfs(node, path_sum): if leaf, return node if path_sum+val≥limit else None.
        - Recurse left/right with path_sum+val; set children to results.
        - Return None if both children gone (and not leaf case already handled).

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node: Optional[TreeNode], path_sum: int) -> Optional[TreeNode]:
            if not node:
                return None
            path_sum += node.val
            if not node.left and not node.right:
                return node if path_sum >= limit else None
            node.left = dfs(node.left, path_sum)
            node.right = dfs(node.right, path_sum)
            if not node.left and not node.right:
                return None
            return node

        return dfs(root, 0)
# @lc code=end
