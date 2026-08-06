#
# @lc app=leetcode id=2471 lang=python3
#
# [2471] Minimum Number of Operations to Sort a Binary Tree by Level
#
# https://leetcode.com/problems/minimum-number-of-operations-to-sort-a-binary-tree-by-level/description/
#
# algorithms
# Medium (74.23%)
# Likes:    1265
# Dislikes: 45
# Total Accepted:    116.8K
# Total Submissions: 157.3K
# Testcase Example:  "[1,4,3,7,6,8,5,null,null,null,null,9,null,10]"
#
# You are given the root of a binary tree with unique values.
#
# In one operation, you can choose any two nodes at the same level and swap
# their values.
#
# Return the minimum number of operations needed to make the values at each
# level sorted in a strictly increasing order.
#
# The level of a node is the number of edges along the path between it and the
# root node.
#
#
#
# Example 1:
#
# Input: root = [1,4,3,7,6,8,5,null,null,null,null,9,null,10]
# Output: 3
# Explanation:
# - Swap 4 and 3. The 2^nd level becomes [3,4].
# - Swap 7 and 5. The 3^rd level becomes [5,6,8,7].
# - Swap 8 and 7. The 3^rd level becomes [5,6,7,8].
# We used 3 operations so return 3.
# It can be proven that 3 is the minimum number of operations needed.
#
# Example 2:
#
# Input: root = [1,3,2,7,6,5,4]
# Output: 3
# Explanation:
# - Swap 3 and 2. The 2^nd level becomes [2,3].
# - Swap 7 and 4. The 3^rd level becomes [4,6,5,7].
# - Swap 6 and 5. The 3^rd level becomes [4,5,6,7].
# We used 3 operations so return 3.
# It can be proven that 3 is the minimum number of operations needed.
#
# Example 3:
#
# Input: root = [1,2,3,4,5,6]
# Output: 0
# Explanation: Each level is already sorted in increasing order so return 0.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [1, 10^5].
#
#
# 1 <= Node.val <= 10^5
#
#
# All the values of the tree are unique.
#

# @lc code=start
from typing import Optional
from collections import deque


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minimumOperations(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Min swaps to sort each level of a binary tree into increasing order.

        Algorithm:
        - BFS levels; for each level, count swaps to sort via cycle decomposition
          of the permutation to sorted positions.

        Complexity: O(n log n) time, O(n) space.
        """
        if not root:
            return 0
        ans = 0
        q = deque([root])
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            ordered = sorted(level)
            pos = {v: i for i, v in enumerate(level)}
            for i in range(len(level)):
                while level[i] != ordered[i]:
                    j = pos[ordered[i]]
                    pos[level[i]] = j
                    level[i], level[j] = level[j], level[i]
                    ans += 1
        return ans
# @lc code=end

