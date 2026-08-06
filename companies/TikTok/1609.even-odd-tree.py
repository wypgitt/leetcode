#
# @lc app=leetcode id=1609 lang=python3
#
# [1609] Even Odd Tree
#
# https://leetcode.com/problems/even-odd-tree/description/
#
# algorithms
# Medium (67.25%)
# Likes:    1904
# Dislikes: 102
# Total Accepted:    199K
# Total Submissions: 296K
# Testcase Example:  "[1,10,4,3,null,7,9,12,8,6,null,null,2]"
#
# A binary tree is named Even-Odd if it meets the following conditions:
#
# The root of the binary tree is at level index 0, its children are at level
# index 1, their children are at level index 2, etc.
#
# For every even-indexed level, all nodes at the level have odd integer values
# in strictly increasing order (from left to right).
#
# For every odd-indexed level, all nodes at the level have even integer values
# in strictly decreasing order (from left to right).
#
# Given the root of a binary tree, return true if the binary tree is Even-Odd,
# otherwise return false.
#
# Example 1:
#
# Input: root = [1,10,4,3,null,7,9,12,8,6,null,null,2]
# Output: true
# Explanation: The node values on each level are:
# Level 0: [1]
# Level 1: [10,4]
# Level 2: [3,7,9]
# Level 3: [12,8,6,2]
# Since levels 0 and 2 are all odd and increasing and levels 1 and 3 are all
# even and decreasing, the tree is Even-Odd.
#
# Example 2:
#
# Input: root = [5,4,2,3,3,7]
# Output: false
# Explanation: The node values on each level are:
# Level 0: [5]
# Level 1: [4,2]
# Level 2: [3,3,7]
# Node values in level 2 must be in strictly increasing order, so the tree is
# not Even-Odd.
#
# Example 3:
#
# Input: root = [5,9,1,3,5,7]
# Output: false
# Explanation: Node values in the level 1 should be even integers.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^6
#

# @lc code=start
from typing import Optional
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
    def isEvenOddTree(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Even levels: odd values strictly increasing; odd levels: even values
        strictly decreasing. BFS level-order is primary.

        Algorithm (BFS):
        - For each level, check parity and monotonicity vs previous value.

        Complexity: O(n) time, O(w) space.
        """
        if not root:
            return True
        q = deque([root])
        level = 0
        while q:
            prev = None
            for _ in range(len(q)):
                node = q.popleft()
                v = node.val
                if level % 2 == 0:
                    if v % 2 == 0 or (prev is not None and v <= prev):
                        return False
                else:
                    if v % 2 == 1 or (prev is not None and v >= prev):
                        return False
                prev = v
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            level += 1
        return True

    def isEvenOddTree_dfs(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Alternate DFS: track last value seen at each depth during left-to-right DFS.

        Algorithm (DFS):
        - last[d] = previous value at depth d; validate parity/order; recurse L then R.

        Complexity: O(n) time, O(h) space.
        """
        last = {}

        def dfs(node: Optional[TreeNode], d: int) -> bool:
            if not node:
                return True
            v = node.val
            if d % 2 == 0:
                if v % 2 == 0:
                    return False
                if d in last and v <= last[d]:
                    return False
            else:
                if v % 2 == 1:
                    return False
                if d in last and v >= last[d]:
                    return False
            last[d] = v
            return dfs(node.left, d + 1) and dfs(node.right, d + 1)

        return dfs(root, 0)
# @lc code=end
