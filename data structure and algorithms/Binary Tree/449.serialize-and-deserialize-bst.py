#
# @lc app=leetcode id=449 lang=python3
#
# [449] Serialize and Deserialize BST
#
# https://leetcode.com/problems/serialize-and-deserialize-bst/description/
#
# algorithms
# Medium (59.88%)
# Likes:    3611
# Dislikes: 180
# Total Accepted:    283K
# Total Submissions: 472K
# Testcase Example:  "[2,1,3]"
#
# Serialization is converting a data structure or object into a sequence of
# bits so that it can be stored in a file or memory buffer, or transmitted
# across a network connection link to be reconstructed later in the same or
# another computer environment.
#
# Design an algorithm to serialize and deserialize a binary search tree. There
# is no restriction on how your serialization/deserialization algorithm should
# work. You need to ensure that a binary search tree can be serialized to a
# string, and this string can be deserialized to the original tree structure.
#
# The encoded string should be as compact as possible.
#
# Example 1:
#
# Input: root = [2,1,3]
# Output: [2,1,3]
#
# Example 2:
#
# Input: root = []
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# 0 <= Node.val <= 10^4
#
# The input tree is guaranteed to be a binary search tree.
#

# @lc code=start
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

try:
    TreeNode  # type: ignore[name-defined]
except NameError:
    class TreeNode:
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None


class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        """
        Interview explanation:
        BST preorder (root-left-right) is enough to rebuild uniquely: values
        alone define structure via BST bounds. No null markers needed — more
        compact than general binary-tree serialization.

        Algorithm:
        - Preorder DFS; append node.val for each visit; join with commas.

        Complexity: O(n) time and space.
        """
        vals = []

        def preorder(node: Optional[TreeNode]) -> None:
            if not node:
                return
            vals.append(str(node.val))
            preorder(node.left)
            preorder(node.right)

        preorder(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """
        Interview explanation:
        Rebuild BST from preorder by consuming values that fall inside
        (lo, hi) bounds. First value is root; left subtree takes vals < root;
        right takes vals > root.

        Algorithm:
        - Parse ints; recursive build(lo, hi) takes next val if lo < val < hi.
        - Left: build(lo, val); right: build(val, hi).

        Complexity: O(n) time and space.
        """
        if not data:
            return None
        vals = list(map(int, data.split(",")))
        i = 0

        def build(lo: float, hi: float) -> Optional[TreeNode]:
            nonlocal i
            if i == len(vals) or not (lo < vals[i] < hi):
                return None
            val = vals[i]
            i += 1
            node = TreeNode(val)
            node.left = build(lo, val)
            node.right = build(val, hi)
            return node

        return build(float("-inf"), float("inf"))


# Your Codec object will be instantiated and called as such:
# ser = Codec()
# deser = Codec()
# tree = ser.serialize(root)
# ans = deser.deserialize(tree)
# return ans
# @lc code=end
