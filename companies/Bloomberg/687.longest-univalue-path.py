#
# @lc app=leetcode id=687 lang=python3
#
# [687] Longest Univalue Path
#
# https://leetcode.com/problems/longest-univalue-path/description/
#
# algorithms
# Medium (44.27%)
# Likes:    4489
# Dislikes: 683
# Total Accepted:    233K
# Total Submissions: 526K
# Testcase Example:  "[5,4,5,1,1,null,5]"
#
# Given the root of a binary tree, return the length of the longest path, where
# each node in the path has the same value. This path may or may not pass
# through the root.
#
# The length of the path between two nodes is represented by the number of
# edges between them.
#
# Example 1:
#
# Input: root = [5,4,5,1,1,null,5]
# Output: 2
# Explanation: The shown image shows that the longest path of the same value
# (i.e. 5).
#
# Example 2:
#
# Input: root = [1,4,5,4,4,null,5]
# Output: 2
# Explanation: The shown image shows that the longest path of the same value
# (i.e. 4).
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# -1000 <= Node.val <= 1000
#
# The depth of the tree will not exceed 1000.
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
    def longestUnivaluePath(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Longest path (edge count) where all nodes share the same value. At each
        node, arrow length down left/right if child matches; path through node
        is left_arrow + right_arrow; return max arrow as chain upward.

        Algorithm:
        - dfs returns longest univalue arrow from node downward.
        - Update global ans with left+right arrows when children match.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node: Optional[TreeNode]) -> int:
            nonlocal ans
            if not node:
                return 0
            left = dfs(node.left)
            right = dfs(node.right)
            left_arrow = left + 1 if node.left and node.left.val == node.val else 0
            right_arrow = right + 1 if node.right and node.right.val == node.val else 0
            ans = max(ans, left_arrow + right_arrow)
            return max(left_arrow, right_arrow)

        dfs(root)
        return ans
# @lc code=end
