#
# @lc app=leetcode id=385 lang=python3
#
# [385] Mini Parser
#
# https://leetcode.com/problems/mini-parser/description/
#
# algorithms
# Medium (42.48%)
# Likes:    504
# Dislikes: 1503
# Total Accepted:    74.6K
# Total Submissions: 175.5K
# Testcase Example:  '"324"'
#
# Given a string s represents the serialization of a nested list, implement a
# parser to deserialize it and return the deserialized NestedInteger.
# 
# Each element is either an integer or a list whose elements may also be
# integers or other lists.
# 
# 
# Example 1:
# 
# 
# Input: s = "324"
# Output: 324
# Explanation: You should return a NestedInteger object which contains a single
# integer 324.
# 
# 
# Example 2:
# 
# 
# Input: s = "[123,[456,[789]]]"
# Output: [123,[456,[789]]]
# Explanation: Return a NestedInteger object containing a nested list with 2
# elements:
# 1. An integer containing value 123.
# 2. A nested list containing two elements:
# ⁠   i.  An integer containing value 456.
# ⁠   ii. A nested list with one element:
# ⁠        a. An integer containing value 789
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 5 * 10^4
# s consists of digits, square brackets "[]", negative sign '-', and commas
# ','.
# s is the serialization of valid NestedInteger.
# All the values in the input are in the range [-10^6, 10^6].
# 
# 
#

# @lc code=start
class Solution:
    def deserialize(self, s: str) -> 'NestedInteger':
        if s[0] != '[':
            return NestedInteger(int(s))

        stack = []
        number_start = None
        for i, ch in enumerate(s):
            if ch == '[':
                stack.append(NestedInteger())
            elif ch == ']':
                if number_start is not None:
                    stack[-1].add(NestedInteger(int(s[number_start:i])))
                    number_start = None
                finished = stack.pop()
                if not stack:
                    return finished
                stack[-1].add(finished)
            elif ch == ',':
                if number_start is not None:
                    stack[-1].add(NestedInteger(int(s[number_start:i])))
                    number_start = None
            elif number_start is None:
                number_start = i

        return NestedInteger()
# @lc code=end

"""
Interview explanation:
Parse the string with a stack of currently open NestedInteger lists. Every '[' starts a new list; every ']' closes the current list and attaches it to its parent. A number is read lazily by remembering its start index and converting it only when a comma or closing bracket ends it, which naturally handles negative and multi-digit values.

Data structure: the stack mirrors the nested bracket structure, so the top is always the list receiving the next parsed child.

Edge cases: a plain integer has no outer brackets and is returned immediately; empty lists close without adding a number; negative numbers are included because '-' starts the numeric slice.

Complexity: each character is scanned once, so time is O(n). The stack can hold one object per nesting level, so auxiliary space is O(depth), not counting the required output object tree.
"""
