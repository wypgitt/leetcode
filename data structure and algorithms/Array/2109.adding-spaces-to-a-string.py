#
# @lc app=leetcode id=2109 lang=python3
#
# [2109] Adding Spaces to a String
#
# https://leetcode.com/problems/adding-spaces-to-a-string/description/
#
# algorithms
# Medium (71.84%)
# Likes:    1132
# Dislikes: 113
# Total Accepted:    230K
# Total Submissions: 320.1K
# Testcase Example:  "\"LeetcodeHelpsMeLearn\"\n[8,13,15]"
#
# You are given a 0-indexed string s and a 0-indexed integer array spaces that
# describes the indices in the original string where spaces will be added. Each
# space should be inserted before the character at the given index.
#
#
# For example, given s = "EnjoyYourCoffee" and spaces = [5, 9], we place spaces
# before 'Y' and 'C', which are at indices 5 and 9 respectively. Thus, we obtain
# "Enjoy Your Coffee".
#
# Return the modified string after the spaces have been added.
#
#
#
# Example 1:
#
# Input: s = "LeetcodeHelpsMeLearn", spaces = [8,13,15]
# Output: "Leetcode Helps Me Learn"
# Explanation:
# The indices 8, 13, and 15 correspond to the underlined characters in
# "LeetcodeHelpsMeLearn".
# We then place spaces before those characters.
#
# Example 2:
#
# Input: s = "icodeinpython", spaces = [1,5,7,9]
# Output: "i code in py thon"
# Explanation:
# The indices 1, 5, 7, and 9 correspond to the underlined characters in
# "icodeinpython".
# We then place spaces before those characters.
#
# Example 3:
#
# Input: s = "spacing", spaces = [0,1,2,3,4,5,6]
# Output: " s p a c i n g"
# Explanation:
# We are also able to place spaces before the first character of the string.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 3 * 10^5
#
#
# s consists only of lowercase and uppercase English letters.
#
#
# 1 <= spaces.length <= 3 * 10^5
#
#
# 0 <= spaces[i] <= s.length - 1
#
#
# All the values of spaces are strictly increasing.
#


# @lc code=start
from typing import List


class Solution:
    def addSpaces(self, s: str, spaces: List[int]) -> str:
        """
        Interview explanation:
        Insert a space before each index in spaces (0-indexed into original s).

        Algorithm:
        - Two pointers / walk s; when index hits next space, append ' '.

        Complexity: O(n + m) time, O(n + m) space for output.
        """
        out = []
        j = 0
        m = len(spaces)
        for i, ch in enumerate(s):
            if j < m and i == spaces[j]:
                out.append(' ')
                j += 1
            out.append(ch)
        return ''.join(out)
# @lc code=end

