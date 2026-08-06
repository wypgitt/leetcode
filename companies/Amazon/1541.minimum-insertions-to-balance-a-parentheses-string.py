#
# @lc app=leetcode id=1541 lang=python3
#
# [1541] Minimum Insertions to Balance a Parentheses String
#
# https://leetcode.com/problems/minimum-insertions-to-balance-a-parentheses-string/description/
#
# algorithms
# Medium (53.65%)
# Likes:    1283
# Dislikes: 299
# Total Accepted:    85.4K
# Total Submissions: 159K
# Testcase Example:  "\"(()))\""
#
# Given a parentheses string s containing only the characters '(' and ')'. A
# parentheses string is balanced if:
#
# Any left parenthesis '(' must have a corresponding two consecutive right
# parenthesis '))'.
#
# Left parenthesis '(' must go before the corresponding two consecutive right
# parenthesis '))'.
#
# In other words, we treat '(' as an opening parenthesis and '))' as a closing
# parenthesis.
#
# For example, "())", "())(())))" and "(())())))" are balanced, ")()", "()))"
# and "(()))" are not balanced.
#
# You can insert the characters '(' and ')' at any position of the string to
# balance it if needed.
#
# Return the minimum number of insertions needed to make s balanced.
#
# Example 1:
#
# Input: s = "(()))"
# Output: 1
# Explanation: The second '(' has two matching '))', but the first '(' has only
# ')' matching. We need to add one more ')' at the end of the string to be
# "(())))" which is balanced.
#
# Example 2:
#
# Input: s = "())"
# Output: 0
# Explanation: The string is already balanced.
#
# Example 3:
#
# Input: s = "))())("
# Output: 3
# Explanation: Add '(' to match the first '))', Add '))' to match the last '('.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of '(' and ')' only.
#

# @lc code=start
class Solution:
    def minInsertions(self, s: str) -> int:
        """
        Interview explanation:
        Balance parentheses where ')' must come in pairs: '(' needs '))'.
        Scan with need of closing '))' count; handle single ')' insertions.

        Algorithm:
        - need=0 (number of ')' still needed); ans=0 insertions.
        - On '(': if need odd, insert one ')' (ans++), need--; need+=2.
        - On ')': need--; if need<0: insert '(' (ans++), need=1.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        need = 0  # ')' still required
        for ch in s:
            if ch == "(":
                if need % 2 == 1:
                    ans += 1
                    need -= 1
                need += 2
            else:
                need -= 1
                if need < 0:
                    ans += 1  # insert '('
                    need = 1
        return ans + need
# @lc code=end
