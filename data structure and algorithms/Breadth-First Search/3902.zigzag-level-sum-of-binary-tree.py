#
# @lc app=leetcode id=3902 lang=python3
#
# [3902] Zigzag Level Sum of Binary Tree
#
# https://leetcode.com/problems/zigzag-level-sum-of-binary-tree/description/
#
# algorithms
# Medium (70.19%)
# Likes:    5
# Dislikes: 2
# Total Accepted:    492
# Total Submissions: 701
# Testcase Example:  "[5,2,8,1,null,9,6]"
#
#
# You are given the root of a binary tree.
#
# Traverse the tree level by level using a zigzag pattern:
#
# At odd-numbered levels (1-indexed), traverse nodes from left to right.
#
# At even-numbered levels, traverse nodes from right to left.
#
# While traversing a level in the specified direction, process nodes in
# order and stop immediately before the first node that violates the
# condition:
#
# At odd levels: the node does not have a left child.
#
# At even levels: the node does not have a right child.
#
# Only the nodes processed before this stopping condition contribute to
# the level sum.
#
# Return an integer array ans where ans[i] is the sum of the node values
# that are processed at level i + 1.
#
# Example 1:
#
# Input: root = [5,2,8,1,null,9,6]
#
# Output: [5,8,0]
#
# Explanation:
#
# ​​​​​​​
#
# At level 1, nodes are processed left to right. Node 5 is included, thus
# ans[0] = 5.
#
# At level 2, nodes are processed right to left. Node 8 is included, but
# node 2 lacks a right child, so processing stops, thus ans[1] = 8.
#
# At level 3, nodes are processed left to right. The first node 1 lacks a
# left child, so no nodes are included, and ans[2] = 0.
#
# Thus, ans = [5, 8, 0].
#
# Example 2:
#
# Input: root = [1,2,3,4,5,null,7]
#
# Output: [1,5,0]
#
# Explanation:
#
# At level 1, nodes are processed left to right. Node 1 is included, thus
# ans[0] = 1.
#
# At level 2, nodes are processed right to left. Nodes 3 and 2 are
# included since both have right children, thus ans[1] = 3 + 2 = 5.
#
# At level 3, nodes are processed left to right. The first node 4 lacks a
# left child, so no nodes are included, and ans[2] = 0.
#
# Thus, ans = [1, 5, 0].
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# -10^5 <= Node.val <= 10^5
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
    def zigzagLevelSum(self, root: Optional["TreeNode"]) -> list[int]:
        """
        Interview explanation:
        Level-order zigzag: L→R on odd levels, R→L on even. Sum nodes until the
        first that lacks the required child (left on odd, right on even).

        Algorithm:
        - BFS by level; traverse in the level's direction.
        - Stop before the first node missing the required child; sum prior vals.
        - Always append the (possibly zero) level sum, then advance.

        Complexity: O(n) time, O(w) space for level width w.
        """
        if root is None:
            return []

        answer = []
        current = [root]
        level = 1

        while current:
            next_level = []
            for node in current:
                if node.left:
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)

            level_sum = 0
            nodes = current if level % 2 == 1 else reversed(current)

            for node in nodes:
                if level % 2 == 1:
                    if node.left is None:
                        break
                else:
                    if node.right is None:
                        break
                level_sum += node.val

            answer.append(level_sum)
            current = next_level
            level += 1

        return answer
# @lc code=end
