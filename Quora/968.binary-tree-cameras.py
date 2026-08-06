#
# @lc app=leetcode id=968 lang=python3
#
# [968] Binary Tree Cameras
#
# https://leetcode.com/problems/binary-tree-cameras/description/
#
# algorithms
# Hard (48.05%)
# Likes:    5699
# Dislikes: 91
# Total Accepted:    196K
# Total Submissions: 408K
# Testcase Example:  "[0,0,null,0,0]"
#
# You are given the root of a binary tree. We install cameras on the tree nodes
# where each camera at a node can monitor its parent, itself, and its immediate
# children.
#
# Return the minimum number of cameras needed to monitor all nodes of the tree.
#
# Example 1:
#
# Input: root = [0,0,null,0,0]
# Output: 1
# Explanation: One camera is enough to monitor all nodes if placed as shown.
#
# Example 2:
#
# Input: root = [0,0,null,0,null,0,null,null,0]
# Output: 2
# Explanation: At least two cameras are needed to monitor all nodes of the
# tree. The above image shows one of the valid configurations of camera
# placement.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 1000].
#
# Node.val == 0
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
    def minCameraCover(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Greedy postorder DFS with 3 states: 0 = needs camera from parent,
        1 = has camera, 2 = covered without camera. Place camera at a node if
        any child needs coverage; root needing coverage gets a camera.

        Algorithm (greedy DFS):
        - dfs(node) → state
        - If child returns 0: place camera here (ans++); return 1
        - If child returns 1: return 2 (covered)
        - Else return 0 (need cover)
        - If root state 0: ans++

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return 2
            left = dfs(node.left)
            right = dfs(node.right)
            if left == 0 or right == 0:
                self.ans += 1
                return 1
            if left == 1 or right == 1:
                return 2
            return 0

        if dfs(root) == 0:
            self.ans += 1
        return self.ans
# @lc code=end

