#
# @lc app=leetcode id=590 lang=python3
#
# [590] N-ary Tree Postorder Traversal
#
# https://leetcode.com/problems/n-ary-tree-postorder-traversal/description/
#
# algorithms
# Easy (81.17%)
# Likes:    2768
# Dislikes: 119
# Total Accepted:    440K
# Total Submissions: 542K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
# Given the root of an n-ary tree, return the postorder traversal of its nodes'
# values.
#
# Nary-Tree input serialization is represented in their level order traversal.
# Each group of children is separated by the null value (See examples)
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: [5,6,3,2,4,1]
#
# Example 2:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output: [2,6,14,11,7,3,12,8,4,13,9,10,5,1]
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
    def postorder(self, root: 'Node') -> List[int]:
        """
        Interview explanation:
        N-ary postorder is children left-to-right then Node. Recursion follows
        that definition.

        Algorithm:
        - Recurse on each child, then append the node's value.

        Complexity: O(n) time, O(h) recursion space.
        """
        ans: List[int] = []

        def dfs(node: Optional['Node']) -> None:
            if not node:
                return
            for child in node.children or []:
                dfs(child)
            ans.append(node.val)

        dfs(root)
        return ans

    def postorderIterative(self, root: 'Node') -> List[int]:
        """
        Interview explanation:
        Classic iterative trick: do a modified preorder (node then children
        left-to-right via pushing left-first so right pops first... actually
        push children left-to-right for reverse preorder node-right-to-left),
        then reverse the result to get children L→R then node.

        Algorithm:
        - Stack DFS: visit node, push children left-to-right.
        - Append values during traversal; reverse at the end.

        Complexity: O(n) time, O(n) stack space.
        """
        if not root:
            return []
        ans: List[int] = []
        stack: List['Node'] = [root]
        while stack:
            node = stack.pop()
            ans.append(node.val)
            for child in node.children or []:
                stack.append(child)
        ans.reverse()
        return ans
# @lc code=end

