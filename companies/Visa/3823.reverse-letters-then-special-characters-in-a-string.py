#
# @lc app=leetcode id=3823 lang=python3
#
# [3823] Reverse Letters Then Special Characters in a String
#
# https://leetcode.com/problems/reverse-letters-then-special-characters-in-a-string/description/
#
# algorithms
# Easy (82.38%)
# Likes:    63
# Dislikes: 4
# Total Accepted:    58.1K
# Total Submissions: 70.5K
# Testcase Example:  "\")ebc#da@f(\""
#
#
# You are given a string s consisting of lowercase English letters and
# special characters.
#
# Your task is to perform these in order:
#
# Reverse the lowercase letters and place them back into the positions
# originally occupied by letters.
#
# Reverse the special characters and place them back into the positions
# originally occupied by special characters.
#
# Return the resulting string after performing the reversals.
#
# Example 1:
#
# Input: s = ")ebc#da@f("
#
# Output: "(fad@cb#e)"
#
# Explanation:
#
# The letters in the string are ['e', 'b', 'c', 'd', 'a', 'f']:
#
# Reversing them gives ['f', 'a', 'd', 'c', 'b', 'e']
#
# s becomes ")fad#cb@e("
#
# ​​​​​​​The special characters in the string are [')', '#', '@', '(']:
#
# Reversing them gives ['(', '@', '#', ')']
#
# s becomes "(fad@cb#e)"
#
# Example 2:
#
# Input: s = "z"
#
# Output: "z"
#
# Explanation:
#
# The string contains only one letter, and reversing it does not change
# the string. There are no special characters.
#
# Example 3:
#
# Input: s = "!@#$%^&*()"
#
# Output: ")(*&^%$#@!"
#
# Explanation:
#
# The string contains no letters. The string contains all special
# characters, so reversing the special characters reverses the whole
# string.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of lowercase English letters and the special characters
# in "!@#$%^&*()".
#

# @lc code=start

class Solution:
    def reverseByType(self, s: str) -> str:
        """
        Interview explanation:
        Reverse letters in letter slots, then reverse specials in special
        slots, independently.

        Algorithm:
        - Collect letters and specials, reverse each list.
        - Rebuild by walking original positions and pulling from the
          matching reversed pool.

        Complexity: O(n) time, O(n) space.
        """
        letters = [c for c in s if c.islower()][::-1]
        specials = [c for c in s if not c.islower()][::-1]
        ans = []
        li = si = 0
        for c in s:
            if c.islower():
                ans.append(letters[li])
                li += 1
            else:
                ans.append(specials[si])
                si += 1
        return "".join(ans)
# @lc code=end
