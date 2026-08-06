#
# @lc app=leetcode id=508 lang=python3
#
# [508] Most Frequent Subtree Sum
#
# https://leetcode.com/problems/most-frequent-subtree-sum/description/
#
# algorithms
# Medium (69.54%)
# Likes:    2386
# Dislikes: 338
# Total Accepted:    181K
# Total Submissions: 261K
# Testcase Example:  "[5,2,-3]"
#
# Given the root of a binary tree, return the most frequent subtree sum. If
# there is a tie, return all the values with the highest frequency in any
# order.
#
# The subtree sum of a node is defined as the sum of all the node values formed
# by the subtree rooted at that node (including the node itself).
#
# Example 1:
#
# Input: root = [5,2,-3]
# Output: [2,-3,4]
#
# Example 2:
#
# Input: root = [5,2,-5]
# Output: [2]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -10^5 <= Node.val <= 10^5
#

# @lc code=start
from collections import Counter
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
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def findFrequentTreeSum(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Postorder: subtree sum = val + left + right. Count frequencies of all
        subtree sums; return those with maximum frequency.

        Algorithm:
        - DFS returns sum; Counter[sum]++.
        - maxf = max frequency; return all sums with count == maxf.

        Complexity: O(n) time, O(n) space.
        """
        count: Counter = Counter()

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            s = node.val + dfs(node.left) + dfs(node.right)
            count[s] += 1
            return s

        dfs(root)
        if not count:
            return []
        maxf = max(count.values())
        return [s for s, f in count.items() if f == maxf]
# @lc code=end
