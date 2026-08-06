#
# @lc app=leetcode id=94 lang=python3
#
# [94] Binary Tree Inorder Traversal
#
# https://leetcode.com/problems/binary-tree-inorder-traversal/description/
#
# algorithms
# Easy (80.46%)
# Likes:    15061
# Dislikes: 907
# Total Accepted:    3.9M
# Total Submissions: 4.8M
# Testcase Example:  "[1,null,2,3]"
#
# Given the root of a binary tree, return the inorder traversal of its nodes'
# values.
#
# Example 1:
#
# Input: root = [1,null,2,3]
#
# Output: [1,3,2]
#
# Explanation:
#
# Example 2:
#
# Input: root = [1,2,3,4,5,null,8,null,null,6,7,9]
#
# Output: [4,2,6,5,7,1,3,9,8]
#
# Explanation:
#
# Example 3:
#
# Input: root = []
#
# Output: []
#
# Example 4:
#
# Input: root = [1]
#
# Output: [1]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 100].
#
# -100 <= Node.val <= 100
#
# Follow up: Recursive solution is trivial, could you do it iteratively?
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
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Inorder is Left -> Node -> Right. Recursion matches that definition
        directly and is the clearest interview starting point.

        Algorithm:
        - Recurse into the left subtree.
        - Visit the current node.
        - Recurse into the right subtree.

        Complexity: O(n) time, O(h) recursion space for tree height h.
        """
        ans: List[int] = []

        def dfs(node: Optional[TreeNode]) -> None:
            if not node:
                return
            dfs(node.left)
            ans.append(node.val)
            dfs(node.right)

        dfs(root)
        return ans

    def inorderTraversalIterative(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Simulate the recursive call stack with an explicit stack so we avoid
        recursion-depth limits while keeping the same Left -> Node -> Right order.

        Algorithm:
        - Walk left, pushing nodes onto the stack.
        - Pop, visit, then move to the right child and repeat.

        Complexity: O(n) time, O(h) stack space.
        """
        ans: List[int] = []
        stack: List[TreeNode] = []
        cur = root
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            ans.append(cur.val)
            cur = cur.right
        return ans

    def inorderTraversalMorris(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Morris traversal threads temporary links from a predecessor to the
        current node so we can traverse inorder with O(1) extra space.

        Algorithm:
        - If there is no left child, visit and go right.
        - Otherwise find the rightmost node in the left subtree (predecessor).
          - If predecessor.right is None, thread it to current and go left.
          - If already threaded, clear the thread, visit current, go right.

        Complexity: O(n) time, O(1) extra space (output excluded; tree briefly mutated).
        """
        ans: List[int] = []
        cur = root
        while cur:
            if not cur.left:
                ans.append(cur.val)
                cur = cur.right
            else:
                pred = cur.left
                while pred.right and pred.right is not cur:
                    pred = pred.right
                if pred.right is None:
                    pred.right = cur
                    cur = cur.left
                else:
                    pred.right = None
                    ans.append(cur.val)
                    cur = cur.right
        return ans
# @lc code=end
