#
# @lc app=leetcode id=1522 lang=python3
#
# [1522] Diameter of N-Ary Tree
#
# https://leetcode.com/problems/diameter-of-n-ary-tree/description/
#
# algorithms
# Medium (75.46%)
# Likes:    645
# Dislikes: 10
# Total Accepted:    62.9K
# Total Submissions: 83.3K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
#
# Given a root of an N-ary tree, you need to compute the length of the
# diameter of the tree.
#
# The diameter of an N-ary tree is the length of the longest path between
# any two nodes in the tree. This path may or may not pass through the
# root.
#
# (Nary-Tree input serialization is represented in their level order
# traversal, each group of children is separated by the null value.)
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: 3
# Explanation: Diameter is shown in red color.
#
# Example 2:
#
# Input: root = [1,null,2,null,3,4,null,5,null,6]
# Output: 4
#
# Example 3:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output: 7
#
# Constraints:
#
# The depth of the n-ary tree is less than or equal to 1000.
#
# The total number of nodes is between [1, 10^4].
#
# @lc code=start
from typing import Optional, List

try:
    Node
except NameError:

    class Node:
        def __init__(self, val: int = None, children: Optional[List["Node"]] = None):
            self.val = val
            self.children = children if children is not None else []


class Solution:
    def diameter(self, root: "Node") -> int:
        """
        Interview explanation:
        Premium. Diameter of N-ary tree = longest path (#edges). DFS returns
        height; at each node diameter candidate = sum of top-2 child heights.

        Algorithm:
        - dfs returns max child height+1; update ans with h1+h2.

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: "Node") -> int:
            if not node:
                return 0
            top1 = top2 = 0
            for ch in node.children:
                h = dfs(ch)
                if h > top1:
                    top2, top1 = top1, h
                elif h > top2:
                    top2 = h
            self.ans = max(self.ans, top1 + top2)
            return top1 + 1

        dfs(root)
        return self.ans
# @lc code=end
