#
# @lc app=leetcode id=1957 lang=python3
#
# [1957] Delete Characters to Make Fancy String
#
# https://leetcode.com/problems/delete-characters-to-make-fancy-string/description/
#
# algorithms
# Easy (73.99%)
# Likes:    1182
# Dislikes: 54
# Total Accepted:    345K
# Total Submissions: 466K
# Testcase Example:  "\"leeetcode\""
#
# A fancy string is a string where no three consecutive characters are equal.
#
# Given a string s, delete the minimum possible number of characters from s to
# make it fancy.
#
# Return the final string after the deletion. It can be shown that the answer
# will always be unique.
#
# Example 1:
#
# Input: s = "leeetcode"
# Output: "leetcode"
# Explanation:
# Remove an 'e' from the first group of 'e's to create "leetcode".
# No three consecutive characters are equal, so return "leetcode".
#
# Example 2:
#
# Input: s = "aaabaaaa"
# Output: "aabaa"
# Explanation:
# Remove an 'a' from the first group of 'a's to create "aabaaaa".
# Remove two 'a's from the second group of 'a's to create "aabaa".
# No three consecutive characters are equal, so return "aabaa".
#
# Example 3:
#
# Input: s = "aab"
# Output: "aab"
# Explanation: No three consecutive characters are equal, so return "aab".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def makeFancyString(self, s: str) -> str:
        """
        Interview explanation:
        Delete minimum chars so no three identical letters are consecutive.
        Keep a char unless the last two kept chars equal it.

        Algorithm:
        - Build list; append c unless out[-1]==out[-2]==c.

        Complexity: O(n) time, O(n) space.
        """
        out = []
        for c in s:
            if len(out) >= 2 and out[-1] == out[-2] == c:
                continue
            out.append(c)
        return "".join(out)

    def makeFancyString_count(self, s: str) -> str:
        """
        Interview explanation:
        Alternate run-length: emit at most 2 of each consecutive run.

        Algorithm:
        - Track run length; append while run <= 2.

        Complexity: O(n) time, O(n) space.
        """
        if not s:
            return s
        out = [s[0]]
        run = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                run += 1
            else:
                run = 1
            if run <= 2:
                out.append(s[i])
        return "".join(out)
# @lc code=end

