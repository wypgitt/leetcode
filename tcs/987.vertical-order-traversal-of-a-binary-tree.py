#
# @lc app=leetcode id=987 lang=python3
#
# [987] Vertical Order Traversal of a Binary Tree
#
# https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/description/
#
# algorithms
# Hard (54.44%)
# Likes:    8785
# Dislikes: 4394
# Total Accepted:    757K
# Total Submissions: 1.4M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given the root of a binary tree, calculate the vertical order traversal of
# the binary tree.
#
# For each node at position (row, col), its left and right children will be at
# positions (row + 1, col - 1) and (row + 1, col + 1) respectively. The root of
# the tree is at (0, 0).
#
# The vertical order traversal of a binary tree is a list of top-to-bottom
# orderings for each column index starting from the leftmost column and ending
# on the rightmost column. There may be multiple nodes in the same row and same
# column. In such a case, sort these nodes by their values.
#
# Return the vertical order traversal of the binary tree.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: [[9],[3,15],[20],[7]]
# Explanation:
# Column -1: Only node 9 is in this column.
# Column 0: Nodes 3 and 15 are in this column in that order from top to bottom.
# Column 1: Only node 20 is in this column.
# Column 2: Only node 7 is in this column.
#
# Example 2:
#
# Input: root = [1,2,3,4,5,6,7]
# Output: [[4],[2],[1,5,6],[3],[7]]
# Explanation:
# Column -2: Only node 4 is in this column.
# Column -1: Only node 2 is in this column.
# Column 0: Nodes 1, 5, and 6 are in this column.
# 1 is at the top, so it comes first.
# 5 and 6 are at the same position (2, 0), so we order them by their value, 5
# before 6.
# Column 1: Only node 3 is in this column.
# Column 2: Only node 7 is in this column.
#
# Example 3:
#
# Input: root = [1,2,3,4,6,5,7]
# Output: [[4],[2],[1,5,6],[3],[7]]
# Explanation:
# This case is the exact same as example 2, but with nodes 5 and 6 swapped.
# Note that the solution remains the same since 5 and 6 are in the same
# location and should be ordered by their values.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 1000].
#
# 0 <= Node.val <= 1000
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
    def verticalTraversal(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Interview explanation:
        Assign each node (row, col); collect (row, val) per column. Sort columns
        left-to-right; within a column sort by row then value.

        Algorithm (DFS):
        - dfs(node, row, col): append (row, val) to buckets[col]; recurse left
          col-1, right col+1.
        - For col in sorted(buckets): sort entries by (row, val); emit values.

        Complexity: O(n log n) time (sort), O(n) space.
        """
        buckets: dict = defaultdict(list)

        def dfs(node: Optional[TreeNode], row: int, col: int) -> None:
            if not node:
                return
            buckets[col].append((row, node.val))
            dfs(node.left, row + 1, col - 1)
            dfs(node.right, row + 1, col + 1)

        dfs(root, 0, 0)
        res: List[List[int]] = []
        for col in sorted(buckets):
            items = sorted(buckets[col])
            res.append([v for _, v in items])
        return res

    def verticalTraversal_bfs(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate BFS: queue (node, row, col); same collect-and-sort by
        (col, row, val).

        Algorithm:
        - BFS enqueue children with updated row/col.
        - Group by col; sort globally by (col, row, val) or per-column.

        Complexity: O(n log n) time, O(n) space.
        """
        if not root:
            return []
        buckets: dict = defaultdict(list)
        q = deque([(root, 0, 0)])
        while q:
            node, row, col = q.popleft()
            buckets[col].append((row, node.val))
            if node.left:
                q.append((node.left, row + 1, col - 1))
            if node.right:
                q.append((node.right, row + 1, col + 1))
        res: List[List[int]] = []
        for col in sorted(buckets):
            items = sorted(buckets[col])
            res.append([v for _, v in items])
        return res
# @lc code=end
