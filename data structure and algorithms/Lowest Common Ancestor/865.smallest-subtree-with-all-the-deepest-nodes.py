#
# @lc app=leetcode id=865 lang=python3
#
# [865] Smallest Subtree with all the Deepest Nodes
#
# https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/description/
#
# algorithms
# Medium (77.68%)
# Likes:    3273
# Dislikes: 404
# Total Accepted:    276K
# Total Submissions: 356K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]"
#
# Given the root of a binary tree, the depth of each node is the shortest
# distance to the root.
#
# Return the smallest subtree such that it contains all the deepest nodes in
# the original tree.
#
# A node is called the deepest if it has the largest depth possible among any
# node in the entire tree.
#
# The subtree of a node is a tree consisting of that node, plus the set of all
# descendants of that node.
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4]
# Output: [2,7,4]
# Explanation: We return the node with value 2, colored in yellow in the
# diagram.
# The nodes coloured in blue are the deepest nodes of the tree.
# Notice that nodes 5, 3 and 2 contain the deepest nodes in the tree but node 2
# is the smallest subtree among them, so we return it.
#
# Example 2:
#
# Input: root = [1]
# Output: [1]
# Explanation: The root is the deepest node in the tree.
#
# Example 3:
#
# Input: root = [0,1,3,null,2]
# Output: [2]
# Explanation: The deepest node in the tree is 2, the valid subtrees are the
# subtrees of nodes 2, 1 and 0 but the subtree of node 2 is the smallest.
#
# Constraints:
#
# The number of nodes in the tree will be in the range [1, 500].
#
# 0 <= Node.val <= 500
#
# The values of the nodes in the tree are unique.
#
# Note: This question is the same as 1123:
# https://leetcode.com/problems/lowest-common-ancestor-of-deepest-leaves/
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
    def subtreeWithAllDeepest(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        LCA of all deepest leaves. One DFS returns (depth, candidate subtree):
        if left/right depths equal, node is answer for that subtree; else take
        the deeper side's candidate.

        Algorithm:
        - dfs(node) -> (depth, subtree). None -> (-1, None).
        - If dl==dr return (dl+1, node); elif dl>dr return (dl+1, left_sub); else right.

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node: Optional[TreeNode]) -> Tuple[int, Optional[TreeNode]]:
            if not node:
                return -1, None
            dl, left = dfs(node.left)
            dr, right = dfs(node.right)
            if dl == dr:
                return dl + 1, node
            if dl > dr:
                return dl + 1, left
            return dr + 1, right

        return dfs(root)[1]

    def subtreeWithAllDeepest_two_pass(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Alternate: find max depth, then find LCA of all nodes at that depth
        (or recurse checking deepest coverage). Same one-pass idea separated.

        Algorithm:
        - First compute depth of each node / max depth.
        - Second find deepest LCA via standard postorder.

        Complexity: O(n) time, O(n) space.
        """
        depth = {}

        def get_depth(node: Optional[TreeNode], d: int) -> None:
            if not node:
                return
            depth[node] = d
            get_depth(node.left, d + 1)
            get_depth(node.right, d + 1)

        get_depth(root, 0)
        max_d = max(depth.values()) if depth else 0

        def lca(node: Optional[TreeNode]) -> Optional[TreeNode]:
            if not node or depth.get(node, -1) == max_d:
                return node
            L, R = lca(node.left), lca(node.right)
            if L and R:
                return node
            return L or R

        return lca(root)
# @lc code=end

