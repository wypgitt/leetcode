#
# @lc app=leetcode id=1628 lang=python3
#
# [1628] Design an Expression Tree With Evaluate Function
#
# https://leetcode.com/problems/design-an-expression-tree-with-evaluate-function/description/
#
# algorithms
# Medium (82.62%)
# Likes:    547
# Dislikes: 74
# Total Accepted:    30.2K
# Total Submissions: 36.6K
# Testcase Example:  "[\"3\",\"4\",\"+\",\"2\",\"*\",\"7\",\"/\"]"
#
#
# Given the postfix tokens of an arithmetic expression, build and return
# the binary expression tree that represents this expression.
#
# Postfix notation is a notation for writing arithmetic expressions in
# which the operands (numbers) appear before their operators. For example,
# the postfix tokens of the expression 4*(5-(7+2)) are represented in the
# array postfix = ["4","5","7","2","+","-","*"].
#
# The class Node is an interface you should use to implement the binary
# expression tree. The returned tree will be tested using the evaluate
# function, which is supposed to evaluate the tree's value. You should not
# remove the Node class; however, you can modify it as you wish, and you
# can define other classes to implement it if needed.
#
# A binary expression tree is a kind of binary tree used to represent
# arithmetic expressions. Each node of a binary expression tree has either
# zero or two children. Leaf nodes (nodes with 0 children) correspond to
# operands (numbers), and internal nodes (nodes with two children)
# correspond to the operators '+' (addition), '-' (subtraction), '*'
# (multiplication), and '/' (division).
#
# It's guaranteed that no subtree will yield a value that exceeds 10^9 in
# absolute value, and all the operations are valid (i.e., no division by
# zero).
#
# Follow up: Could you design the expression tree such that it is more
# modular? For example, is your design able to support additional
# operators without making changes to your existing evaluate
# implementation?
#
# Example 1:
#
# Input: s = ["3","4","+","2","*","7","/"]
# Output: 2
# Explanation: this expression evaluates to the above binary tree with
# expression ((3+4)*2)/7) = 14/7 = 2.
#
# Example 2:
#
# Input: s = ["4","5","2","7","+","-","*"]
# Output: -16
# Explanation: this expression evaluates to the above binary tree with
# expression 4*(5-(2+7)) = 4*(-4) = -16.
#
# Constraints:
#
# 1 <= s.length < 100
#
# s.length is odd.
#
# s consists of numbers and the characters '+', '-', '*', and '/'.
#
# If s[i] is a number, its integer representation is no more than 10^5.
#
# It is guaranteed that s is a valid expression.
#
# The absolute value of the result and intermediate values will not exceed
# 10^9.
#
# It is guaranteed that no expression will include division by zero.
#
# @lc code=start
from typing import List
from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def evaluate(self) -> int:
        """
        Interview explanation:
        Abstract expression-tree node; subclasses implement evaluate.

        Algorithm:
        - Interface only; concrete nodes store val/children.

        Complexity: n/a.
        """
        raise NotImplementedError


class ValNode(Node):
    def __init__(self, val: int):
        """
        Interview explanation:
        Leaf node holding a numeric operand.

        Algorithm:
        - Store integer value.

        Complexity: O(1).
        """
        self.val = val

    def evaluate(self) -> int:
        """
        Interview explanation:
        Leaf numeric node.

        Algorithm:
        - Return stored integer.

        Complexity: O(1).
        """
        return self.val


class OpNode(Node):
    def __init__(self, op: str, left: Node, right: Node):
        """
        Interview explanation:
        Internal operator node with left/right children.

        Algorithm:
        - Store op and child Node references.

        Complexity: O(1).
        """
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self) -> int:
        """
        Interview explanation:
        Operator node evaluating left/right with + - * / (integer division).

        Algorithm:
        - Recursively evaluate children; apply op.

        Complexity: O(size of subtree).
        """
        l, r = self.left.evaluate(), self.right.evaluate()
        if self.op == "+":
            return l + r
        if self.op == "-":
            return l - r
        if self.op == "*":
            return l * r
        return l // r


class TreeBuilder:
    def buildTree(self, postfix: List[str]) -> "Node":
        """
        Interview explanation:
        Premium design. Build expression tree from postfix tokens using a stack.

        Algorithm (stack):
        - Digit token → ValNode. Operator → pop right,left → OpNode; push.
        - Return final stack top.

        Complexity: O(n) time/space.
        """
        st: List[Node] = []
        for tok in postfix:
            if tok.isdigit():
                st.append(ValNode(int(tok)))
            else:
                r = st.pop()
                l = st.pop()
                st.append(OpNode(tok, l, r))
        return st[-1]


# Your TreeBuilder object will be instantiated and called as such:
# obj = TreeBuilder();
# expTree = obj.buildTree(postfix);
# ans = expTree.evaluate();
# @lc code=end
