#
# @lc app=leetcode id=1047 lang=python3
#
# [1047] Remove All Adjacent Duplicates In String
#
# https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string/description/
#
# algorithms
# Easy (73.79%)
# Likes:    7164
# Dislikes: 276
# Total Accepted:    929K
# Total Submissions: 1.3M
# Testcase Example:  "\"abbaca\""
#
# You are given a string s consisting of lowercase English letters. A duplicate
# removal consists of choosing two adjacent and equal letters and removing
# them.
#
# We repeatedly make duplicate removals on s until we no longer can.
#
# Return the final string after all such duplicate removals have been made. It
# can be proven that the answer is unique.
#
# Example 1:
#
# Input: s = "abbaca"
# Output: "ca"
# Explanation:
# For example, in "abbaca" we could remove "bb" since the letters are adjacent
# and equal, and this is the only possible move. The result of this move is
# that the string is "aaca", of which only "aa" is possible, so the final
# string is "ca".
#
# Example 2:
#
# Input: s = "azxxzy"
# Output: "ay"
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def removeDuplicates(self, s: str) -> str:
        """
        Interview explanation:
        Stack simulation of adjacent duplicate removal: push char; if top equals
        current, pop (cancel pair); else push. Final stack is the answer.

        Algorithm:
        - For ch in s: if stack and stack[-1]==ch: pop else push
        - Return ''.join(stack)

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        for ch in s:
            if stack and stack[-1] == ch:
                stack.pop()
            else:
                stack.append(ch)
        return "".join(stack)
# @lc code=end
