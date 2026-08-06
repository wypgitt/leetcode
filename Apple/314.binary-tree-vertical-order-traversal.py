#
# @lc app=leetcode id=314 lang=python3
#
# [314] Binary Tree Vertical Order Traversal
#
# https://leetcode.com/problems/binary-tree-vertical-order-traversal/description/
#
# algorithms
# Medium (57.88%)
# Likes:    3472
# Dislikes: 354
# Total Accepted:    600.5K
# Total Submissions: 1M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
#
# Given the root of a binary tree, return the vertical order traversal of
# its nodes' values. (i.e., from top to bottom, column by column).
#
# If two nodes are in the same row and column, the order should be from
# left to right.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: [[9],[3,15],[20],[7]]
#
# Example 2:
#
# Input: root = [3,9,8,4,0,1,7]
# Output: [[4],[9],[3,0,1],[8],[7]]
#
# Example 3:
#
# Input: root =
# [1,2,3,4,10,9,11,null,5,null,null,null,null,null,null,null,6]
# Output: [[4],[2,5],[1,10,9,6],[3],[11]]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 100].
#
# -100 <= Node.val <= 100
#
# @lc code=start
from collections import defaultdict, deque
from typing import List, Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def verticalOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Interview explanation:
        Group nodes by column index (root=0, left-1, right+1). BFS preserves
        row-major top-to-bottom and left-to-right within a column.

        Algorithm:
        - BFS queue of (node, col); append vals into dict[col].
        - Return columns from min_col to max_col.

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return []
        cols = defaultdict(list)
        q = deque([(root, 0)])
        min_c = max_c = 0
        while q:
            node, c = q.popleft()
            cols[c].append(node.val)
            min_c = min(min_c, c)
            max_c = max(max_c, c)
            if node.left:
                q.append((node.left, c - 1))
            if node.right:
                q.append((node.right, c + 1))
        return [cols[c] for c in range(min_c, max_c + 1)]
# @lc code=end

