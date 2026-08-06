#
# @lc app=leetcode id=652 lang=python3
#
# [652] Find Duplicate Subtrees
#
# https://leetcode.com/problems/find-duplicate-subtrees/description/
#
# algorithms
# Medium (60.81%)
# Likes:    6163
# Dislikes: 508
# Total Accepted:    322K
# Total Submissions: 530K
# Testcase Example:  "[1,2,3,4,null,2,4,null,null,4]"
#
# Given the root of a binary tree, return all duplicate subtrees.
#
# For each kind of duplicate subtrees, you only need to return the root node of
# any one of them.
#
# Two trees are duplicate if they have the same structure with the same node
# values.
#
# Example 1:
#
# Input: root = [1,2,3,4,null,2,4,null,null,4]
# Output: [[2,4],[4]]
#
# Example 2:
#
# Input: root = [2,1,1]
# Output: [[1]]
#
# Example 3:
#
# Input: root = [2,2,2,3,null,3,null]
# Output: [[2,3],[3]]
#
# Constraints:
#
# The number of the nodes in the tree will be in the range [1, 5000]
#
# -200 <= Node.val <= 200
#

# @lc code=start

from collections import defaultdict
from typing import List, Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def findDuplicateSubtrees(
        self, root: Optional[TreeNode]
    ) -> List[Optional[TreeNode]]:
        """
        Interview explanation:
        Serialize each subtree to a string (or id); hash counts; when count
        becomes 2, record the node as a duplicate representative.

        Algorithm:
        - DFS postorder: serial = f"{val},{left},{right}".
        - Map serial -> count; if count == 2: append node.

        Complexity: O(N^2) string concat worst / O(N) with integer ids; O(N) space.
        """
        seen = defaultdict(int)
        ans = []

        def dfs(node):
            if not node:
                return "#"
            serial = f"{node.val},{dfs(node.left)},{dfs(node.right)}"
            seen[serial] += 1
            if seen[serial] == 2:
                ans.append(node)
            return serial

        dfs(root)
        return ans
# @lc code=end
