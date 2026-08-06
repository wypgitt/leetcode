#
# @lc app=leetcode id=2265 lang=python3
#
# [2265] Count Nodes Equal to Average of Subtree
#
# https://leetcode.com/problems/count-nodes-equal-to-average-of-subtree/description/
#
# algorithms
# Medium (86.79%)
# Likes:    2376
# Dislikes: 60
# Total Accepted:    203.1K
# Total Submissions: 234K
# Testcase Example:  "[4,8,5,0,1,null,6]"
#
# Given the root of a binary tree, return the number of nodes where the value of
# the node is equal to the average of the values in its subtree.
#
# Note:
#
#
# The average of n elements is the sum of the n elements divided by n and
# rounded down to the nearest integer.
#
#
# A subtree of root is a tree consisting of root and all of its descendants.
#
#
#
# Example 1:
#
# Input: root = [4,8,5,0,1,null,6]
# Output: 5
# Explanation:
# For the node with value 4: The average of its subtree is (4 + 8 + 5 + 0 + 1 +
# 6) / 6 = 24 / 6 = 4.
# For the node with value 5: The average of its subtree is (5 + 6) / 2 = 11 / 2
# = 5.
# For the node with value 0: The average of its subtree is 0 / 1 = 0.
# For the node with value 1: The average of its subtree is 1 / 1 = 1.
# For the node with value 6: The average of its subtree is 6 / 1 = 6.
#
# Example 2:
#
# Input: root = [1]
# Output: 1
# Explanation: For the node with value 1: The average of its subtree is 1 / 1 =
# 1.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [1, 1000].
#
#
# 0 <= Node.val <= 1000
#

# @lc code=start
from typing import Optional, Tuple


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def averageOfSubtree(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Count nodes whose value equals floor(average of its subtree).

        Algorithm:
        - Postorder DFS returns (sum, count); compare root.val to sum//count.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node) -> Tuple[int, int]:
            nonlocal ans
            if not node:
                return 0, 0
            ls, lc = dfs(node.left)
            rs, rc = dfs(node.right)
            total = ls + rs + node.val
            cnt = lc + rc + 1
            if total // cnt == node.val:
                ans += 1
            return total, cnt

        dfs(root)
        return ans

# @lc code=end
