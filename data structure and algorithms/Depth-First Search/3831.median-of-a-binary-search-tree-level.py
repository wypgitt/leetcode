#
# @lc app=leetcode id=3831 lang=python3
#
# [3831] Median of a Binary Search Tree Level
#
# https://leetcode.com/problems/median-of-a-binary-search-tree-level/description/
#
# algorithms
# Medium (87.43%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    1.3K
# Total Submissions: 1.5K
# Testcase Example:  "[4,null,5,null,7]\n2"
#
#
# You are given the root of a Binary Search Tree (BST) and an integer
# level.
#
# The root node is at level 0. Each level represents the distance from the
# root.
#
# Return the median value of all node values present at the given level.
# If the level does not exist or contains no nodes, return -1.
#
# The median is defined as the middle element after sorting the values at
# that level in non-decreasing order. If the number of values at that
# level is even, return the upper median (the larger of the two middle
# elements after sorting).
#
# Example 1:
#
# Input: root = [4,null,5,null,7], level = 2
#
# Output: 7
#
# Explanation:
#
# The nodes at level = 2 are [7]. The median value is 7.
#
# Example 2:
#
# Input: root = [6,3,8], level = 1
#
# Output: 8
#
# Explanation:
#
# The nodes at level = 1 are [3, 8]. There are two possible median values,
# so the larger one 8 is the answer.
#
# Example 3:
#
# ​​​​​​​​​​​​​​
#
# Input: root = [2,1], level = 2
#
# Output: -1
#
# Explanation:
#
# There is no node present at level = 2​​​​​​​, so the answer is -1.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 2 * 10^5].
#
# 1 <= Node.val <= 10^6
#
# 0 <= level <= 2 * 10^​​​​​​​5
#

# @lc code=start
from typing import List, Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def levelMedian(self, root: Optional[TreeNode], level: int) -> int:
        """
        Interview explanation:
        Return the upper median of BST node values at a given depth (root = 0).
        Inorder traversal of a BST yields sorted values, so collect that level
        inorder and take the middle (upper when even).

        Algorithm:
        - DFS inorder; append node.val when depth == level.
        - If empty return -1; else return nums[len//2] (upper median).

        Complexity: O(n) time, O(n) space.
        """
        nums: List[int] = []

        def dfs(node: Optional[TreeNode], depth: int) -> None:
            if node is None:
                return
            dfs(node.left, depth + 1)
            if depth == level:
                nums.append(node.val)
            dfs(node.right, depth + 1)

        dfs(root, 0)
        return nums[len(nums) // 2] if nums else -1

    def levelMedian_bfs(self, root: Optional[TreeNode], level: int) -> int:
        """
        Interview explanation:
        Alternate: BFS to the target level, sort values, take upper median.

        Algorithm:
        - Level-order until depth == level; sort collected values.

        Complexity: O(n + w log w) time, O(w) space.
        """
        from collections import deque

        if root is None:
            return -1
        q = deque([root])
        depth = 0
        while q:
            if depth == level:
                vals = sorted(node.val for node in q)
                return vals[len(vals) // 2]
            for _ in range(len(q)):
                node = q.popleft()
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            depth += 1
        return -1
# @lc code=end
