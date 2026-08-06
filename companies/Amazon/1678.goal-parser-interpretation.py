#
# @lc app=leetcode id=1678 lang=python3
#
# [1678] Goal Parser Interpretation
#
# https://leetcode.com/problems/goal-parser-interpretation/description/
#
# algorithms
# Easy (88.15%)
# Likes:    1696
# Dislikes: 95
# Total Accepted:    337K
# Total Submissions: 382K
# Testcase Example:  "\"G()(al)\""
#
# You own a Goal Parser that can interpret a string command. The command
# consists of an alphabet of "G", "()" and/or "(al)" in some order. The Goal
# Parser will interpret "G" as the string "G", "()" as the string "o", and
# "(al)" as the string "al". The interpreted strings are then concatenated in
# the original order.
#
# Given the string command, return the Goal Parser's interpretation of command.
#
# Example 1:
#
# Input: command = "G()(al)"
# Output: "Goal"
# Explanation: The Goal Parser interprets the command as follows:
# G -> G
# () -> o
# (al) -> al
# The final concatenated result is "Goal".
#
# Example 2:
#
# Input: command = "G()()()()(al)"
# Output: "Gooooal"
#
# Example 3:
#
# Input: command = "(al)G(al)()()G"
# Output: "alGalooG"
#
# Constraints:
#
# 1 <= command.length <= 100
#
# command consists of "G", "()", and/or "(al)" in some order.
#

# @lc code=start
class Solution:
    def interpret(self, command: str) -> str:
        """
        Interview explanation:
        Goal parser: "G"→G, "()"→o, "(al)"→al. Replace in order or scan with index.

        Algorithm (replace):
        - command.replace('()','o').replace('(al)','al')

        Complexity: O(n) time, O(n) space.
        """
        return command.replace("()", "o").replace("(al)", "al")

    def interpret_scan(self, command: str) -> str:
        """
        Interview explanation:
        Alternate: single pass index scan without chained replace.

        Algorithm:
        - i=0; while i<n: if G append G; elif () skip 2 append o; else skip 4 append al.

        Complexity: O(n) time, O(n) space.
        """
        out = []
        i = 0
        n = len(command)
        while i < n:
            if command[i] == "G":
                out.append("G")
                i += 1
            elif command[i : i + 2] == "()":
                out.append("o")
                i += 2
            else:
                out.append("al")
                i += 4
        return "".join(out)
# @lc code=end
