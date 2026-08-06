#
# @lc app=leetcode id=938 lang=python3
#
# [938] Range Sum of BST
#
# https://leetcode.com/problems/range-sum-of-bst/description/
#
# algorithms
# Easy (87.62%)
# Likes:    7288
# Dislikes: 389
# Total Accepted:    1.4M
# Total Submissions: 1.6M
# Testcase Example:  "[10,5,15,3,7,null,18]"
#
# Given the root node of a binary search tree and two integers low and high,
# return the sum of values of all nodes with a value in the inclusive range
# [low, high].
#
# Example 1:
#
# Input: root = [10,5,15,3,7,null,18], low = 7, high = 15
# Output: 32
# Explanation: Nodes 7, 10, and 15 are in the range [7, 15]. 7 + 10 + 15 = 32.
#
# Example 2:
#
# Input: root = [10,5,15,3,7,13,18,1,null,6], low = 6, high = 10
# Output: 23
# Explanation: Nodes 6, 7, and 10 are in the range [6, 10]. 6 + 7 + 10 = 23.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 2 * 10^4].
#
# 1 <= Node.val <= 10^5
#
# 1 <= low <= high <= 10^5
#
# All Node.val are unique.
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
    def rangeSumBST(self, root: Optional[TreeNode], low: int, high: int) -> int:
        """
        Interview explanation:
        BST pruning DFS: skip left subtree if node.val < low; skip right if
        node.val > high; add node when in [low, high].

        Algorithm (DFS):
        - dfs(node): if not node return 0
        - if val < low: return dfs(right)
        - if val > high: return dfs(left)
        - return val + dfs(left) + dfs(right)

        Complexity: O(n) time, O(h) space.
        """
        if not root:
            return 0
        if root.val < low:
            return self.rangeSumBST(root.right, low, high)
        if root.val > high:
            return self.rangeSumBST(root.left, low, high)
        return (
            root.val
            + self.rangeSumBST(root.left, low, high)
            + self.rangeSumBST(root.right, low, high)
        )

    def rangeSumBST_bfs(self, root: Optional[TreeNode], low: int, high: int) -> int:
        """
        Interview explanation:
        Alternate: iterative BFS/stack traversal with the same BST pruning.

        Algorithm (BFS/iterative):
        - queue/stack with root; while: pop; if in range add; push pruned children

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return 0
        ans = 0
        q = deque([root])
        while q:
            node = q.popleft()
            if node.val < low:
                if node.right:
                    q.append(node.right)
            elif node.val > high:
                if node.left:
                    q.append(node.left)
            else:
                ans += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return ans
# @lc code=end

