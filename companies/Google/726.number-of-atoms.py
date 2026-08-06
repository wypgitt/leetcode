#
# @lc app=leetcode id=726 lang=python3
#
# [726] Number of Atoms
#
# https://leetcode.com/problems/number-of-atoms/description/
#
# algorithms
# Hard (65.22%)
# Likes:    1997
# Dislikes: 414
# Total Accepted:    165K
# Total Submissions: 253K
# Testcase Example:  "\"H2O\""
#
# Given a string formula representing a chemical formula, return the count of
# each atom.
#
# The atomic element always starts with an uppercase character, then zero or
# more lowercase letters, representing the name.
#
# One or more digits representing that element's count may follow if the count
# is greater than 1. If the count is 1, no digits will follow.
#
# For example, "H2O" and "H2O2" are possible, but "H1O2" is impossible.
#
# Two formulas are concatenated together to produce another formula.
#
# For example, "H2O2He3Mg4" is also a formula.
#
# A formula placed in parentheses, and a count (optionally added) is also a
# formula.
#
# For example, "(H2O2)" and "(H2O2)3" are formulas.
#
# Return the count of all elements as a string in the following form: the first
# name (in sorted order), followed by its count (if that count is more than 1),
# followed by the second name (in sorted order), followed by its count (if that
# count is more than 1), and so on.
#
# The test cases are generated so that all the values in the output fit in a
# 32-bit integer.
#
# Example 1:
#
# Input: formula = "H2O"
# Output: "H2O"
# Explanation: The count of elements are {'H': 2, 'O': 1}.
#
# Example 2:
#
# Input: formula = "Mg(OH)2"
# Output: "H2MgO2"
# Explanation: The count of elements are {'H': 2, 'Mg': 1, 'O': 2}.
#
# Example 3:
#
# Input: formula = "K4(ON(SO3)2)2"
# Output: "K4N2O14S4"
# Explanation: The count of elements are {'K': 4, 'N': 2, 'O': 14, 'S': 4}.
#
# Constraints:
#
# 1 <= formula.length <= 1000
#
# formula consists of English letters, digits, '(', and ')'.
#
# formula is always valid.
#


# @lc code=start
from collections import Counter


class Solution:
    def countOfAtoms(self, formula: str) -> str:
        """
        Interview explanation:
        Parse nested chemical formula with a stack of counters. On '(', push a
        new counter; on ')', pop and multiply by the following integer, merge
        into the new top. Atoms and counts update the current counter.

        Algorithm:
        - stack = [Counter()]; i = 0
        - If '(': push Counter, i++
        - If ')': pop cnt, read multiplier, add m*cnt into stack.top, i++
        - Else: parse atom name + optional count; stack.top[atom] += count
        - Sort atoms from final Counter and format.

        Complexity: O(n + u log u) time for length n and u unique atoms; O(n) space.
        """
        stack = [Counter()]
        i, n = 0, len(formula)

        def read_num(j: int) -> tuple:
            if j >= n or not formula[j].isdigit():
                return 1, j
            v = 0
            while j < n and formula[j].isdigit():
                v = v * 10 + int(formula[j])
                j += 1
            return v, j

        while i < n:
            if formula[i] == "(":
                stack.append(Counter())
                i += 1
            elif formula[i] == ")":
                top = stack.pop()
                i += 1
                mult, i = read_num(i)
                for atom, c in top.items():
                    stack[-1][atom] += c * mult
            else:
                j = i + 1
                while j < n and formula[j].islower():
                    j += 1
                atom = formula[i:j]
                cnt, i = read_num(j)
                stack[-1][atom] += cnt

        parts = []
        for atom in sorted(stack[-1]):
            c = stack[-1][atom]
            parts.append(atom + (str(c) if c > 1 else ""))
        return "".join(parts)
# @lc code=end

