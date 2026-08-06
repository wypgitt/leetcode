#
# @lc app=leetcode id=1022 lang=python3
#
# [1022] Sum of Root To Leaf Binary Numbers
#
# https://leetcode.com/problems/sum-of-root-to-leaf-binary-numbers/description/
#
# algorithms
# Easy (76.67%)
# Likes:    3810
# Dislikes: 212
# Total Accepted:    368K
# Total Submissions: 480K
# Testcase Example:  "[1,0,1,0,1,0,1]"
#
# You are given the root of a binary tree where each node has a value 0 or 1.
# Each root-to-leaf path represents a binary number starting with the most
# significant bit.
#
# For example, if the path is 0 -> 1 -> 1 -> 0 -> 1, then this could represent
# 01101 in binary, which is 13.
#
# For all leaves in the tree, consider the numbers represented by the path from
# the root to that leaf. Return the sum of these numbers.
#
# The test cases are generated so that the answer fits in a 32-bits integer.
#
# Example 1:
#
# Input: root = [1,0,1,0,1,0,1]
# Output: 22
# Explanation: (100) + (101) + (110) + (111) = 4 + 5 + 6 + 7 = 22
#
# Example 2:
#
# Input: root = [0]
# Output: 0
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 1000].
#
# Node.val is 0 or 1.
#

# @lc code=start
from collections import deque
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def sumRootToLeaf(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Each path forms a binary number; DFS carrying the current value
        (cur = cur*2 + node.val). At leaves add cur to the answer.

        Algorithm:
        - dfs(node, cur): if not node return; cur=cur*2+val
          if leaf: add cur; else recurse children

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode], cur: int) -> None:
            if not node:
                return
            cur = cur * 2 + node.val
            if not node.left and not node.right:
                self.ans += cur
                return
            dfs(node.left, cur)
            dfs(node.right, cur)

        dfs(root, 0)
        return self.ans

    def sumRootToLeaf_bfs(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Alternate classic BFS: queue pairs (node, path_value); at leaves sum.

        Algorithm:
        - q=deque([(root, root.val)]); total=0
        - While q: pop; if leaf total+=val; else push children with val*2+child.val

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return 0
        total = 0
        q = deque([(root, root.val)])
        while q:
            node, val = q.popleft()
            if not node.left and not node.right:
                total += val
                continue
            if node.left:
                q.append((node.left, val * 2 + node.left.val))
            if node.right:
                q.append((node.right, val * 2 + node.right.val))
        return total
# @lc code=end
