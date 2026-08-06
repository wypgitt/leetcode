#
# @lc app=leetcode id=1612 lang=python3
#
# [1612] Check If Two Expression Trees are Equivalent
#
# https://leetcode.com/problems/check-if-two-expression-trees-are-equivalent/description/
#
# algorithms
# Medium (71.81%)
# Likes:    146
# Dislikes: 24
# Total Accepted:    8.8K
# Total Submissions: 12.3K
# Testcase Example:  "[x]\n[x]"
#
#
# A binary expression tree is a kind of binary tree used to represent
# arithmetic expressions. Each node of a binary expression tree has either
# zero or two children. Leaf nodes (nodes with 0 children) correspond to
# operands (variables), and internal nodes (nodes with two children)
# correspond to the operators. In this problem, we only consider the '+'
# operator (i.e. addition).
#
# You are given the roots of two binary expression trees, root1 and root2.
# Return true if the two binary expression trees are equivalent.
# Otherwise, return false.
#
# Two binary expression trees are equivalent if they evaluate to the same
# value regardless of what the variables are set to.
#
# Example 1:
#
# Input: root1 = [x], root2 = [x]
# Output: true
#
# Example 2:
#
# Input: root1 = [+,a,+,null,null,b,c], root2 = [+,+,a,b,c]
# Output: true
# Explanation: a + (b + c) == (b + c) + a
#
# Example 3:
#
# Input: root1 = [+,a,+,null,null,b,c], root2 = [+,+,a,b,d]
# Output: false
# Explanation: a + (b + c) != (b + d) + a
#
# Constraints:
#
# The number of nodes in both trees are equal, odd and, in the range [1,
# 4999].
#
# Node.val is '+' or a lower-case English letter.
#
# It's guaranteed that the tree given is a valid binary expression tree.
#
# Follow up: What will you change in your solution if the tree also
# supports the '-' operator (i.e. subtraction)?
#
# @lc code=start
from typing import Optional
from collections import Counter, deque

try:
    Node  # type: ignore[name-defined]
except NameError:

    class Node:  # type: ignore[no-redef]
        def __init__(self, val="", left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def checkEquivalence(self, root1: "Node", root2: "Node") -> bool:
        """
        Interview explanation:
        Premium. Expression trees with + and variables; + is commutative/associative.
        Trees equivalent iff variable multiplicity (counts) match.

        Algorithm (DFS count):
        - DFS each tree: if '+', recurse both; else count variable leaf.
        - Compare Counter maps.

        Complexity: O(n) time/space.
        """
        def count(node: Optional["Node"]) -> Counter:
            c: Counter = Counter()
            if not node:
                return c
            if node.val == "+":
                c += count(node.left)
                c += count(node.right)
            else:
                c[node.val] += 1
            return c

        return count(root1) == count(root2)

    def checkEquivalence_bfs(self, root1: "Node", root2: "Node") -> bool:
        """
        Interview explanation:
        Alternate BFS/stack traversal counting variable leaves the same way.

        Algorithm (iterative stack):
        - Explicit stack; on '+' push children; else increment count[val].

        Complexity: O(n) time/space.
        """
        def count(root: Optional["Node"]) -> Counter:
            c: Counter = Counter()
            if not root:
                return c
            st = [root]
            while st:
                node = st.pop()
                if node.val == "+":
                    if node.left:
                        st.append(node.left)
                    if node.right:
                        st.append(node.right)
                else:
                    c[node.val] += 1
            return c

        return count(root1) == count(root2)
# @lc code=end
