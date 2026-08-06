#
# @lc app=leetcode id=1597 lang=python3
#
# [1597] Build Binary Expression Tree From Infix Expression
#
# https://leetcode.com/problems/build-binary-expression-tree-from-infix-expression/description/
#
# algorithms
# Hard (62.92%)
# Likes:    272
# Dislikes: 49
# Total Accepted:    15K
# Total Submissions: 23.9K
# Testcase Example:  "\"3*4-2*5\""
#
#
# A binary expression tree is a kind of binary tree used to represent
# arithmetic expressions. Each node of a binary expression tree has either
# zero or two children. Leaf nodes (nodes with 0 children) correspond to
# operands (numbers), and internal nodes (nodes with 2 children)
# correspond to the operators '+' (addition), '-' (subtraction), '*'
# (multiplication), and '/' (division).
#
# For each internal node with operator o, the infix expression it
# represents is (A o B), where A is the expression the left subtree
# represents and B is the expression the right subtree represents.
#
# You are given a string s, an infix expression containing operands, the
# operators described above, and parentheses '(' and ')'.
#
# Return any valid binary expression tree, whose in-order traversal
# reproduces s after omitting the parenthesis from it.
#
# Please note that order of operations applies in s. That is, expressions
# in parentheses are evaluated first, and multiplication and division
# happen before addition and subtraction.
#
# Operands must also appear in the same order in both s and the in-order
# traversal of the tree.
#
# Example 1:
#
# Input: s = "3*4-2*5"
# Output: [-,*,*,3,4,2,5]
# Explanation: The tree above is the only valid tree whose inorder
# traversal produces s.
#
# Example 2:
#
# Input: s = "2-3/(5*2)+1"
# Output: [+,-,1,2,/,null,null,null,null,3,*,null,null,5,2]
# Explanation: The inorder traversal of the tree above is 2-3/5*2+1 which
# is the same as s without the parenthesis. The tree also produces the
# correct result and its operands are in the same order as they appear in
# s.
# The tree below is also a valid binary expression tree with the same
# inorder traversal as s, but it not a valid answer because it does not
# evaluate to the same value.
#
# The third tree below is also not valid. Although it produces the same
# result and is equivalent to the above trees, its inorder traversal does
# not produce s and its operands are not in the same order as s.
#
# Example 3:
#
# Input: s = "1+2+3+4+5"
# Output: [+,+,5,+,4,null,null,+,3,null,null,1,2]
# Explanation: The tree [+,+,5,+,+,null,null,1,2,3,4] is also one of many
# other valid trees.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of digits and the characters '(', ')', '+', '-', '*', and
# '/'.
#
# Operands in s are exactly 1 digit.
#
# It is guaranteed that s is a valid expression.
#
# @lc code=start
# Definition for a binary tree node.
try:
    Node  # type: ignore[name-defined]
except NameError:

    class Node:  # type: ignore[no-redef]
        def __init__(self, val=" ", left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def expTree(self, s: str) -> "Node":
        """
        Interview explanation:
        Premium. Build expression tree from infix with + - * / and parentheses.
        Shunting-yard / two stacks: operand nodes and operator nodes; pop on
        precedence and ')' to build binary Nodes.

        Algorithm (two stacks):
        - prec: +,- =1; *,/ =2.
        - On digit: push Node(digit). On '(': push. On ')': collapse until '('.
        - On op: while top op has >= precedence, merge; then push op.
        - Merge: right=operands.pop(); left=operands.pop(); op=ops.pop();
          push Node(op,left,right).

        Complexity: O(n) time/space.
        """
        def prec(op: str) -> int:
            return 1 if op in "+-" else 2

        def merge(ops, nodes):
            op = ops.pop()
            r = nodes.pop()
            l = nodes.pop()
            nodes.append(Node(op, l, r))

        ops: list = []
        nodes: list = []
        for ch in s:
            if ch.isdigit():
                nodes.append(Node(ch))
            elif ch == "(":
                ops.append(ch)
            elif ch == ")":
                while ops and ops[-1] != "(":
                    merge(ops, nodes)
                ops.pop()
            else:
                while ops and ops[-1] != "(" and prec(ops[-1]) >= prec(ch):
                    merge(ops, nodes)
                ops.append(ch)
        while ops:
            merge(ops, nodes)
        return nodes[0]
# @lc code=end

