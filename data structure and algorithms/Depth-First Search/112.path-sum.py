#
# @lc app=leetcode id=112 lang=python3
#
# [112] Path Sum
#
# https://leetcode.com/problems/path-sum/description/
#
# algorithms
# Easy (55.44%)
# Likes:    10853
# Dislikes: 1221
# Total Accepted:    2.2M
# Total Submissions: 4.0M
# Testcase Example:  "[5,4,8,11,null,13,4,7,2,null,null,null,1]"
#
# Given the root of a binary tree and an integer targetSum, return true if the
# tree has a root-to-leaf path such that adding up all the values along the
# path equals targetSum.
#
# A leaf is a node with no children.
#
# Example 1:
#
# Input: root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22
# Output: true
# Explanation: The root-to-leaf path with the target sum is shown.
#
# Example 2:
#
# Input: root = [1,2,3], targetSum = 5
# Output: false
# Explanation: There are two root-to-leaf paths in the tree:
# (1 --> 2): The sum is 3.
# (1 --> 3): The sum is 4.
# There is no root-to-leaf path with sum = 5.
#
# Example 3:
#
# Input: root = [], targetSum = 0
# Output: false
# Explanation: Since the tree is empty, there are no root-to-leaf paths.
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 5000].
#
# -1000 <= Node.val <= 1000
#
# -1000 <= targetSum <= 1000
#

# @lc code=start
from typing import List, Optional, Tuple
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        """
        Interview explanation:
        Check whether any root-to-leaf path sums to targetSum. DFS subtracts
        (or accumulates) node values and succeeds only at a true leaf.

        Algorithm:
        - Empty tree -> False.
        - At a leaf, succeed iff remaining equals node.val.
        - Otherwise recurse left/right with remaining - node.val.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return False
        remaining = targetSum - root.val
        if not root.left and not root.right:
            return remaining == 0
        return (
            self.hasPathSum(root.left, remaining)
            or self.hasPathSum(root.right, remaining)
        )

    def hasPathSumIterative(self, root: Optional[TreeNode], targetSum: int) -> bool:
        """
        Interview explanation:
        Iterative DFS with an explicit stack of (node, remaining sum) mirrors
        the recursive approach without call-stack depth concerns.

        Algorithm:
        - Push (root, targetSum - root.val).
        - Pop; if leaf and remaining is 0, return True.
        - Push children with updated remaining.

        Complexity: O(n) time, O(h) stack space.
        """
        if not root:
            return False
        stack: List[Tuple[TreeNode, int]] = [(root, targetSum - root.val)]
        while stack:
            node, remaining = stack.pop()
            if not node.left and not node.right and remaining == 0:
                return True
            if node.left:
                stack.append((node.left, remaining - node.left.val))
            if node.right:
                stack.append((node.right, remaining - node.right.val))
        return False
# @lc code=end
