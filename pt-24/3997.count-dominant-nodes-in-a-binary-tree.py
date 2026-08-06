#
# @lc app=leetcode id=3997 lang=python3
#
# [3997] Count Dominant Nodes in a Binary Tree
#
# https://leetcode.com/problems/count-dominant-nodes-in-a-binary-tree/description/
#
# algorithms
# Medium (72.33%)
# Likes:    38
# Dislikes: 3
# Total Accepted:    37.2K
# Total Submissions: 51.5K
# Testcase Example:  "[5,3,8,2,4,7,1]"
#
#
# You are given the root of a complete binary tree.
#
# A node x is called dominant if its value is equal to the maximum value
# among all nodes in the subtree rooted at x.
#
# Return the number of dominant nodes in the tree.
#
# Example 1:
#
# Input: root = [5,3,8,2,4,7,1]
#
# Output: 5
#
# Explanation:
#
# The leaf nodes with values 2, 4, 7, and 1 are dominant.
#
# The node with value 8 is dominant because its value is the maximum value
# in its subtree [8, 7, 1].
#
# Thus, the answer is 5.
#
# Example 2:
#
# Input: root = [1,2,3,1,2]
#
# Output: 4
#
# Explanation:
#
# The leaf nodes with values 1, 2, and 3 are dominant.
#
# The node with value 2 whose subtree is [2, 1, 2] is dominant because its
# value is the maximum value in its subtree.
#
# Thus, the answer is 4.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^9
#
# The tree is guaranteed to be a complete binary tree.
#

# @lc code=start
from math import inf

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def countDominantNodes(self, root: "TreeNode | None") -> int:
        """
        Interview explanation:
        A node is dominant if its value equals the maximum in its subtree.
        One DFS returns each subtree max and counts nodes equal to that max.

        Algorithm:
        - dfs(node) -> max value in subtree (or -inf for None).
        - After children, mx = max(left, right, node.val); if mx == node.val
          increment answer.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node):
            nonlocal ans
            if node is None:
                return -inf
            mx = max(dfs(node.left), dfs(node.right), node.val)
            if mx == node.val:
                ans += 1
            return mx

        dfs(root)
        return ans
# @lc code=end
