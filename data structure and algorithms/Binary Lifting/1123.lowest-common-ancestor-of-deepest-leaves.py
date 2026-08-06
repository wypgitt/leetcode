#
# @lc app=leetcode id=1123 lang=python3
#
# [1123] Lowest Common Ancestor of Deepest Leaves
#
# https://leetcode.com/problems/lowest-common-ancestor-of-deepest-leaves/description/
#
# algorithms
# Medium (79.5%)
# Likes:    2703
# Dislikes: 950
# Total Accepted:    256K
# Total Submissions: 323K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]"
#
# Given the root of a binary tree, return the lowest common ancestor of its
# deepest leaves.
#
# Recall that:
#
# The node of a binary tree is a leaf if and only if it has no children
#
# The depth of the root of the tree is 0. if the depth of a node is d, the
# depth of each of its children is d + 1.
#
# The lowest common ancestor of a set S of nodes, is the node A with the
# largest depth such that every node in S is in the subtree with root A.
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4]
# Output: [2,7,4]
# Explanation: We return the node with value 2, colored in yellow in the
# diagram.
# The nodes coloured in blue are the deepest leaf-nodes of the tree.
# Note that nodes 6, 0, and 8 are also leaf nodes, but the depth of them is 2,
# but the depth of nodes 7 and 4 is 3.
#
# Example 2:
#
# Input: root = [1]
# Output: [1]
# Explanation: The root is the deepest node in the tree, and it's the lca of
# itself.
#
# Example 3:
#
# Input: root = [0,1,3,null,2]
# Output: [2]
# Explanation: The deepest leaf node in the tree is 2, the lca of one node is
# itself.
#
# Constraints:
#
# The number of nodes in the tree will be in the range [1, 1000].
#
# 0 <= Node.val <= 1000
#
# The values of the nodes in the tree are unique.
#
# Note: This question is the same as 865:
# https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/
#

# @lc code=start
from typing import Optional, Tuple

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def lcaDeepestLeaves(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        LCA of all deepest leaves. One DFS returns (depth, candidate): if left
        and right depths match, current node is LCA of deepest leaves under it;
        else take the deeper child's candidate.

        Algorithm:
        - dfs(node) -> (depth from node, lca subtree).
        - Equal depths → (d+1, node); else take max side.

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node: Optional[TreeNode]) -> Tuple[int, Optional[TreeNode]]:
            if not node:
                return 0, None
            dl, left = dfs(node.left)
            dr, right = dfs(node.right)
            if dl == dr:
                return dl + 1, node
            if dl > dr:
                return dl + 1, left
            return dr + 1, right

        return dfs(root)[1]
# @lc code=end
