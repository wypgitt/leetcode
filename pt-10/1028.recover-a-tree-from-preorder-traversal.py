#
# @lc app=leetcode id=1028 lang=python3
#
# [1028] Recover a Tree From Preorder Traversal
#
# https://leetcode.com/problems/recover-a-tree-from-preorder-traversal/description/
#
# algorithms
# Hard (83.21%)
# Likes:    2310
# Dislikes: 70
# Total Accepted:    169K
# Total Submissions: 203K
# Testcase Example:  "\"1-2--3--4-5--6--7\""
#
# We run a preorder depth-first search (DFS) on the root of a binary tree.
#
# At each node in this traversal, we output D dashes (where D is the depth of
# this node), then we output the value of this node. If the depth of a node is
# D, the depth of its immediate child is D + 1. The depth of the root node is
# 0.
#
# If a node has only one child, that child is guaranteed to be the left child.
#
# Given the output traversal of this traversal, recover the tree and return its
# root.
#
# Example 1:
#
# Input: traversal = "1-2--3--4-5--6--7"
# Output: [1,2,5,3,4,6,7]
#
# Example 2:
#
# Input: traversal = "1-2--3---4-5--6---7"
# Output: [1,2,5,3,null,6,null,4,null,7]
#
# Example 3:
#
# Input: traversal = "1-401--349---90--88"
# Output: [1,401,null,349,88,90]
#
# Constraints:
#
# The number of nodes in the original tree is in the range [1, 1000].
#
# 1 <= Node.val <= 10^9
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
    def recoverFromPreorder(self, traversal: str) -> Optional[TreeNode]:
        """
        Interview explanation:
        Preorder with depth encoded by dash count. Parse (depth, value) tokens;
        stack of nodes by depth: pop until stack size == depth, attach as left
        or right child of stack top, then push.

        Algorithm:
        - i=0; while i<len: count dashes → depth; parse number → val
        - While len(stack)>depth: pop
        - Create node; attach to stack[-1]; push node

        Complexity: O(n) time, O(h) space.
        """
        try:
            TreeNode  # type: ignore[name-defined]
        except NameError:

            class TreeNode:  # type: ignore[no-redef]
                def __init__(self, val=0, left=None, right=None):
                    self.val = val
                    self.left = left
                    self.right = right

        stack = []
        i, n = 0, len(traversal)
        while i < n:
            depth = 0
            while i < n and traversal[i] == "-":
                depth += 1
                i += 1
            val = 0
            while i < n and traversal[i].isdigit():
                val = val * 10 + int(traversal[i])
                i += 1
            node = TreeNode(val)
            while len(stack) > depth:
                stack.pop()
            if stack:
                if stack[-1].left is None:
                    stack[-1].left = node
                else:
                    stack[-1].right = node
            stack.append(node)
        return stack[0] if stack else None
# @lc code=end
