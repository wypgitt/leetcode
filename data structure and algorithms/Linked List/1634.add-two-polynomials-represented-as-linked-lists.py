#
# @lc app=leetcode id=1634 lang=python3
#
# [1634] Add Two Polynomials Represented as Linked Lists
#
# https://leetcode.com/problems/add-two-polynomials-represented-as-linked-lists/description/
#
# algorithms
# Medium (61.13%)
# Likes:    174
# Dislikes: 14
# Total Accepted:    16.6K
# Total Submissions: 27.1K
# Testcase Example:  "[[1,1]]\n[[1,0]]"
#
#
# A polynomial linked list is a special type of linked list where every
# node represents a term in a polynomial expression.
#
#
#
# Each node has three attributes:
#
#
#
#
#
# coefficient: an integer representing the number multiplier of the term.
# The coefficient of the term 9x^4 is 9.
#
#
# power: an integer representing the exponent. The power of the term 9x^4
# is 4.
#
#
# next: a pointer to the next node in the list, or null if it is the last
# node of the list.
#
#
#
#
#
# For example, the polynomial 5x^3 + 4x - 7 is represented by the
# polynomial linked list illustrated below:
#
#
#
#
#
#
# The polynomial linked list must be in its standard form: the polynomial
# must be in strictly descending order by its power value. Also, terms
# with a coefficient of 0 are omitted.
#
#
#
# Given two polynomial linked list heads, poly1 and poly2, add the
# polynomials together and return the head of the sum of the polynomials.
#
#
#
# PolyNode format:
#
#
#
# The input/output format is as a list of n nodes, where each node is
# represented as its [coefficient, power]. For example, the polynomial
# 5x^3 + 4x - 7 would be represented as: [[5,3],[4,1],[-7,0]].
#
#
#
#
#
# Example 1:
#
#
#
#
#
#
#
# Input: poly1 = [[1,1]], poly2 = [[1,0]]
# Output: [[1,1],[1,0]]
# Explanation: poly1 = x. poly2 = 1. The sum is x + 1.
#
#
#
#
# Example 2:
#
#
#
#
# Input: poly1 = [[2,2],[4,1],[3,0]], poly2 = [[3,2],[-4,1],[-1,0]]
# Output: [[5,2],[2,0]]
# Explanation: poly1 = 2x^2 + 4x + 3. poly2 = 3x^2 - 4x - 1. The sum is
# 5x^2 + 2. Notice that we omit the "0x" term.
#
#
#
#
# Example 3:
#
#
#
#
# Input: poly1 = [[1,2]], poly2 = [[-1,2]]
# Output: []
# Explanation: The sum is 0. We return an empty list.
#
#
#
#
#
#
# Constraints:
#
#
#
#
#
# 0 <= n <= 10^4
#
#
# -10^9 <= PolyNode.coefficient <= 10^9
#
#
# PolyNode.coefficient != 0
#
#
# 0 <= PolyNode.power <= 10^9
#
#
# PolyNode.power > PolyNode.next.power
#
# @lc code=start
from typing import Optional

try:
    PolyNode  # type: ignore[name-defined]
except NameError:

    class PolyNode:  # type: ignore[no-redef]
        def __init__(self, x=0, y=0, next=None):
            self.coefficient = x
            self.power = y
            self.next = next


class Solution:
    def addPoly(self, poly1: "PolyNode", poly2: "PolyNode") -> "PolyNode":
        """
        Interview explanation:
        Premium. Polynomials as linked lists sorted by power descending.
        Merge like merge-two-lists; sum equal powers; skip zero coefficients.

        Algorithm (two-pointer merge):
        - Dummy head; while both: compare powers; append larger or sum equals.
        - Append remainders; return dummy.next.

        Complexity: O(n+m) time, O(1) extra if reuse nodes / O(n+m) new nodes.
        """
        dummy = PolyNode()
        cur = dummy
        p, q = poly1, poly2
        while p and q:
            if p.power > q.power:
                cur.next = PolyNode(p.coefficient, p.power)
                p = p.next
            elif p.power < q.power:
                cur.next = PolyNode(q.coefficient, q.power)
                q = q.next
            else:
                s = p.coefficient + q.coefficient
                if s != 0:
                    cur.next = PolyNode(s, p.power)
                    cur = cur.next
                p = p.next
                q = q.next
                continue
            cur = cur.next
        while p:
            cur.next = PolyNode(p.coefficient, p.power)
            cur = cur.next
            p = p.next
        while q:
            cur.next = PolyNode(q.coefficient, q.power)
            cur = cur.next
            q = q.next
        return dummy.next

    def addPoly_dict(self, poly1: "PolyNode", poly2: "PolyNode") -> "PolyNode":
        """
        Interview explanation:
        Alternate: accumulate coefficients in dict by power; rebuild sorted list.

        Algorithm:
        - Map power→coef from both lists; emit non-zero powers descending.

        Complexity: O((n+m) log (n+m)) time.
        """
        from collections import defaultdict

        coef = defaultdict(int)
        for head in (poly1, poly2):
            while head:
                coef[head.power] += head.coefficient
                head = head.next
        dummy = PolyNode()
        cur = dummy
        for pwr in sorted(coef.keys(), reverse=True):
            if coef[pwr] != 0:
                cur.next = PolyNode(coef[pwr], pwr)
                cur = cur.next
        return dummy.next
# @lc code=end
