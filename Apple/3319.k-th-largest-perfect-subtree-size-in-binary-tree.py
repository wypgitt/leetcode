#
# @lc app=leetcode id=3319 lang=python3
#
# [3319] K-th Largest Perfect Subtree Size in Binary Tree
#
# https://leetcode.com/problems/k-th-largest-perfect-subtree-size-in-binary-tree/description/
#
# algorithms
# Medium (62.48%)
# Likes:    159
# Dislikes: 15
# Total Accepted:    31K
# Total Submissions: 49.6K
# Testcase Example:  "[5,3,6,5,2,5,7,1,8,null,null,6,8]\n2"
#
#
# You are given the root of a binary tree and an integer k.
#
# Return an integer denoting the size of the k^th largest perfect binary
# subtree, or -1 if it doesn't exist.
#
# A perfect binary tree is a tree where all leaves are on the same level,
# and every parent has two children.
#
# Example 1:
#
# Input: root = [5,3,6,5,2,5,7,1,8,null,null,6,8], k = 2
#
# Output: 3
#
# Explanation:
#
# The roots of the perfect binary subtrees are highlighted in black. Their
# sizes, in non-increasing order are [3, 3, 1, 1, 1, 1, 1, 1].
#
# The 2^nd largest size is 3.
#
# Example 2:
#
# Input: root = [1,2,3,4,5,6,7], k = 1
#
# Output: 7
#
# Explanation:
#
# The sizes of the perfect binary subtrees in non-increasing order are [7,
# 3, 3, 1, 1, 1, 1]. The size of the largest perfect binary subtree is 7.
#
# Example 3:
#
# Input: root = [1,2,3,null,4], k = 3
#
# Output: -1
#
# Explanation:
#
# The sizes of the perfect binary subtrees in non-increasing order are [1,
# 1]. There are fewer than 3 perfect binary subtrees.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 2000].
#
# 1 <= Node.val <= 2000
#
# 1 <= k <= 1024
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
    def kthLargestPerfectSubtree(self, root: Optional[TreeNode], k: int) -> int:
        """
        Interview explanation:
        A perfect subtree has all leaves on one level and every node two children.
        Collect sizes of all perfect subtrees; return the k-th largest.

        Algorithm:
        - DFS returns (is_perfect, height, size).
        - Node is perfect iff both children are perfect with equal height.
        - Sort sizes descending; answer sizes[k-1] or -1.

        Complexity: O(n log n) time for sort, O(n) space.
        """
        sizes: List[int] = []

        def dfs(node: Optional[TreeNode]) -> tuple[bool, int, int]:
            if node is None:
                return True, -1, 0
            lok, lh, ls = dfs(node.left)
            rok, rh, rs = dfs(node.right)
            if lok and rok and lh == rh:
                size = ls + rs + 1
                sizes.append(size)
                return True, lh + 1, size
            return False, 0, 0

        dfs(root)
        sizes.sort(reverse=True)
        return sizes[k - 1] if k <= len(sizes) else -1
# @lc code=end
