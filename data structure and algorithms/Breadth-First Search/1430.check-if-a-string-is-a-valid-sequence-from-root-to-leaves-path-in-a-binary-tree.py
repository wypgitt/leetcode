#
# @lc app=leetcode id=1430 lang=python3
#
# [1430] Check If a String Is a Valid Sequence from Root to Leaves Path in a Binary Tree
#
# https://leetcode.com/problems/check-if-a-string-is-a-valid-sequence-from-root-to-leaves-path-in-a-binary-tree/description/
#
# algorithms
# Medium (47.55%)
# Likes:    219
# Dislikes: 15
# Total Accepted:    46.7K
# Total Submissions: 98.2K
# Testcase Example:  "[0,1,0,0,1,0,null,null,1,0,0]\n[0,1,0,1]"
#
#
# Given a binary tree where each path going from the root to any leaf form
# a valid sequence, check if a given string is a valid sequence in such
# binary tree.
#
# We get the given string from the concatenation of an array of integers
# arr and the concatenation of all values of the nodes along a path
# results in a sequence in the given binary tree.
#
# Example 1:
#
# Input: root = [0,1,0,0,1,0,null,null,1,0,0], arr = [0,1,0,1]
# Output: true
# Explanation:
# The path 0 -> 1 -> 0 -> 1 is a valid sequence (green color in the
# figure).
# Other valid sequences are:
# 0 -> 1 -> 1 -> 0
# 0 -> 0 -> 0
#
# Example 2:
#
# Input: root = [0,1,0,0,1,0,null,null,1,0,0], arr = [0,0,1]
# Output: false
# Explanation: The path 0 -> 0 -> 1 does not exist, therefore it is not
# even a sequence.
#
# Example 3:
#
# Input: root = [0,1,0,0,1,0,null,null,1,0,0], arr = [0,1,1]
# Output: false
# Explanation: The path 0 -> 1 -> 1 is a sequence, but it is not a valid
# sequence.
#
# Constraints:
#
# 1 <= arr.length <= 5000
#
# 0 <= arr[i] <= 9
#
# Each node's value is between [0 - 9].
#
# @lc code=start
from typing import List, Optional
from collections import deque

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def isValidSequence(self, root: Optional[TreeNode], arr: List[int]) -> bool:
        """
        Interview explanation:
        Premium. Check whether arr is values along some root-to-leaf path.
        DFS matching index into arr; at end of arr must be a leaf.

        Algorithm:
        (DFS)
        - dfs(node, i): False if node None or val!=arr[i]; if i==n-1: leaf;
          else left or right with i+1.

        Complexity: O(n) time, O(h) space.
        """
        n = len(arr)

        def dfs(node: Optional[TreeNode], i: int) -> bool:
            if not node or node.val != arr[i]:
                return False
            if i == n - 1:
                return not node.left and not node.right
            return dfs(node.left, i + 1) or dfs(node.right, i + 1)

        return dfs(root, 0) if root else False

    def isValidSequence_bfs(self, root: Optional[TreeNode], arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate BFS: queue (node, index); same leaf/end conditions.

        Algorithm:
        - BFS pairs; when index==n-1 check leaf.

        Complexity: O(n) time, O(w) space.
        """
        if not root:
            return False
        n = len(arr)
        q = deque([(root, 0)])
        while q:
            node, i = q.popleft()
            if node.val != arr[i]:
                continue
            if i == n - 1:
                if not node.left and not node.right:
                    return True
                continue
            if node.left:
                q.append((node.left, i + 1))
            if node.right:
                q.append((node.right, i + 1))
        return False
# @lc code=end
