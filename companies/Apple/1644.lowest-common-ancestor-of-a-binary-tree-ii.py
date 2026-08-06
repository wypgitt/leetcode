#
# @lc app=leetcode id=1644 lang=python3
#
# [1644] Lowest Common Ancestor of a Binary Tree II
#
# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-ii/description/
#
# algorithms
# Medium (69.73%)
# Likes:    703
# Dislikes: 42
# Total Accepted:    122.3K
# Total Submissions: 175.3K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]\n5\n1"
#
#
# Given the root of a binary tree, return the lowest common ancestor (LCA)
# of two given nodes, p and q. If either node p or q does not exist in the
# tree, return null. All values of the nodes in the tree are unique.
#
# According to the definition of LCA on Wikipedia: "The lowest common
# ancestor of two nodes p and q in a binary tree T is the lowest node that
# has both p and q as descendants (where we allow a node to be a
# descendant of itself)". A descendant of a node x is a node y that is on
# the path from node x to some leaf node.
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
# Output: 3
# Explanation: The LCA of nodes 5 and 1 is 3.
#
# Example 2:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
# Output: 5
# Explanation: The LCA of nodes 5 and 4 is 5. A node can be a descendant
# of itself according to the definition of LCA.
#
# Example 3:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 10
# Output: null
# Explanation: Node 10 does not exist in the tree, so return null.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -10^9 <= Node.val <= 10^9
#
# All Node.val are unique.
#
# p != q
#
# Follow up: Can you find the LCA traversing the tree, without checking
# nodes existence?
#
# @lc code=start
from typing import Optional

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None


class Solution:
    def lowestCommonAncestor(
        self, root: "TreeNode", p: "TreeNode", q: "TreeNode"
    ) -> Optional["TreeNode"]:
        """
        Interview explanation:
        Premium LCA II: p and/or q may not exist; return LCA only if both exist,
        else null. Standard postorder LCA while counting found nodes.

        Algorithm (DFS count):
        - Recurse; found = (node is p/q) + left_found + right_found.
        - When found==2 first time, record node as LCA. Return node if found==2 else None.

        Complexity: O(n) time, O(h) space.
        """
        self.ans = None

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            found = int(node is p or node is q)
            found += dfs(node.left)
            found += dfs(node.right)
            if found == 2 and self.ans is None:
                self.ans = node
            return found

        dfs(root)
        return self.ans

    def lowestCommonAncestor_parent(
        self, root: "TreeNode", p: "TreeNode", q: "TreeNode"
    ) -> Optional["TreeNode"]:
        """
        Interview explanation:
        Alternate: map child→parent while searching for p and q; if either missing
        return None; walk ancestors of p into a set; climb q.

        Algorithm (parent pointers):
        - BFS/DFS build parent and presence; set of p's ancestors; climb q.

        Complexity: O(n) time/space.
        """
        from collections import deque

        parent = {root: None}
        q_nodes = deque([root])
        found_p = found_q = False
        while q_nodes and (not found_p or not found_q):
            node = q_nodes.popleft()
            if node is p:
                found_p = True
            if node is q:
                found_q = True
            if node.left:
                parent[node.left] = node
                q_nodes.append(node.left)
            if node.right:
                parent[node.right] = node
                q_nodes.append(node.right)
        if not found_p or not found_q:
            return None
        ancestors = set()
        while p:
            ancestors.add(p)
            p = parent[p]
        while q not in ancestors:
            q = parent[q]
        return q
# @lc code=end
