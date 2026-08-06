#
# @lc app=leetcode id=589 lang=python3
#
# [589] N-ary Tree Preorder Traversal
#
# https://leetcode.com/problems/n-ary-tree-preorder-traversal/description/
#
# algorithms
# Easy (76.91%)
# Likes:    3278
# Dislikes: 204
# Total Accepted:    508K
# Total Submissions: 661K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
# Given the root of an n-ary tree, return the preorder traversal of its nodes'
# values.
#
# Nary-Tree input serialization is represented in their level order traversal.
# Each group of children is separated by the null value (See examples)
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: [1,3,5,6,2,4]
#
# Example 2:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output: [1,2,3,6,7,11,14,4,8,12,5,9,13,10]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# 0 <= Node.val <= 10^4
#
# The height of the n-ary tree is less than or equal to 1000.
#
# Follow up: Recursive solution is trivial, could you do it iteratively?
#


# @lc code=start
from typing import List, Optional
"""
# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List['Node']] = None):
        self.val = val
        self.children = children
"""

class Solution:
    def preorder(self, root: 'Node') -> List[int]:
        """
        Interview explanation:
        N-ary preorder is Node then children left-to-right. Recursion matches
        the definition directly.

        Algorithm:
        - Visit root, then recurse on each child in order.

        Complexity: O(n) time, O(h) recursion space.
        """
        ans: List[int] = []

        def dfs(node: Optional['Node']) -> None:
            if not node:
                return
            ans.append(node.val)
            for child in node.children or []:
                dfs(child)

        dfs(root)
        return ans

    def preorderIterative(self, root: 'Node') -> List[int]:
        """
        Interview explanation:
        Iterative preorder with an explicit stack. Push children right-to-left
        so left children are processed first (LIFO).

        Algorithm:
        - Start with root on the stack.
        - Pop, visit, push children in reverse order.

        Complexity: O(n) time, O(n) stack space worst case.
        """
        if not root:
            return []
        ans: List[int] = []
        stack: List['Node'] = [root]
        while stack:
            node = stack.pop()
            ans.append(node.val)
            children = node.children or []
            for child in reversed(children):
                stack.append(child)
        return ans
# @lc code=end

