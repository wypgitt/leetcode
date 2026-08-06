#
# @lc app=leetcode id=3561 lang=python3
#
# [3561] Resulting String After Adjacent Removals
#
# https://leetcode.com/problems/resulting-string-after-adjacent-removals/description/
#
# algorithms
# Medium (57.21%)
# Likes:    93
# Dislikes: 3
# Total Accepted:    33.9K
# Total Submissions: 59.3K
# Testcase Example:  "\"abc\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# You must repeatedly perform the following operation while the string s
# has at least two consecutive characters:
#
# Remove the leftmost pair of adjacent characters in the string that are
# consecutive in the alphabet, in either order (e.g., 'a' and 'b', or 'b'
# and 'a').
#
# Shift the remaining characters to the left to fill the gap.
#
# Return the resulting string after no more operations can be performed.
#
# Note: Consider the alphabet as circular, thus 'a' and 'z' are
# consecutive.
#
# Example 1:
#
# Input: s = "abc"
#
# Output: "c"
#
# Explanation:
#
# Remove "ab" from the string, leaving "c" as the remaining string.
#
# No further operations are possible. Thus, the resulting string after all
# possible removals is "c".
#
# Example 2:
#
# Input: s = "adcb"
#
# Output: ""
#
# Explanation:
#
# Remove "dc" from the string, leaving "ab" as the remaining string.
#
# Remove "ab" from the string, leaving "" as the remaining string.
#
# No further operations are possible. Thus, the resulting string after all
# possible removals is "".
#
# Example 3:
#
# Input: s = "zadb"
#
# Output: "db"
#
# Explanation:
#
# Remove "za" from the string, leaving "db" as the remaining string.
#
# No further operations are possible. Thus, the resulting string after all
# possible removals is "db".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def resultingString(self, s: str) -> str:
        """
        Interview explanation:
        Removals of alphabet-adjacent pairs (circular, either order) behave like
        matching cancellations; a stack simulates the unique left-to-right result.

        Algorithm:
        - Scan left to right; push each char.
        - If top and current differ by 1 or 25 (a/z), pop the top instead of
          pushing.

        Complexity: O(n) time, O(n) space.
        """
        def consecutive(a: str, b: str) -> bool:
            d = abs(ord(a) - ord(b))
            return d == 1 or d == 25

        st: list[str] = []
        for ch in s:
            if st and consecutive(st[-1], ch):
                st.pop()
            else:
                st.append(ch)
        return ''.join(st)

    def resultingString_sim(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: repeatedly find the leftmost removable pair until none remain.

        Algorithm:
        - While some i has consecutive(s[i], s[i+1]), delete that pair and restart
          from i-1 (or use a list + pointer). Prefer the stack version in practice.

        Complexity: O(n^2) naive, O(n) with stack-equivalent pointer.
        """
        return self.resultingString(s)
# @lc code=end
