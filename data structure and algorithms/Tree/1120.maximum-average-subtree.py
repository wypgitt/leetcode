#
# @lc app=leetcode id=1120 lang=python3
#
# [1120] Maximum Average Subtree
#
# https://leetcode.com/problems/maximum-average-subtree/description/
#
# algorithms
# Medium (66.97%)
# Likes:    858
# Dislikes: 36
# Total Accepted:    74.5K
# Total Submissions: 111.2K
# Testcase Example:  "[5,6,1]"
#
#
# Given the root of a binary tree, return the maximum average value of a
# subtree of that tree. Answers within 10^-5 of the actual answer will be
# accepted.
#
# A subtree of a tree is any node of that tree plus all its descendants.
#
# The average value of a tree is the sum of its values, divided by the
# number of nodes.
#
# Example 1:
#
# Input: root = [5,6,1]
# Output: 6.00000
# Explanation:
# For the node with value = 5 we have an average of (5 + 6 + 1) / 3 = 4.
# For the node with value = 6 we have an average of 6 / 1 = 6.
# For the node with value = 1 we have an average of 1 / 1 = 1.
# So the answer is 6 which is the maximum.
#
# Example 2:
#
# Input: root = [0,null,1]
# Output: 1.00000
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 0 <= Node.val <= 10^5
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
    def maximumAverageSubtree(self, root: Optional[TreeNode]) -> float:
        """
        Interview explanation:
        Premium. Maximum average value of any subtree. Postorder DFS returns
        (sum, count) for each subtree; track global max of sum/count.

        Algorithm (DFS):
        - dfs(node) → (sum, count); update ans with sum/count.
        - Combine left+right+node.val / counts.

        Complexity: O(n) time, O(h) space.
        """
        self.ans = float("-inf")

        def dfs(node: Optional[TreeNode]):
            if not node:
                return 0, 0
            ls, lc = dfs(node.left)
            rs, rc = dfs(node.right)
            total = ls + rs + node.val
            cnt = lc + rc + 1
            self.ans = max(self.ans, total / cnt)
            return total, cnt

        dfs(root)
        return self.ans
# @lc code=end
