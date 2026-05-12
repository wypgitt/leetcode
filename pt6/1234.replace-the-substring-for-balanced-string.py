#
# @lc app=leetcode id=1234 lang=python3
#
# [1234] Replace the Substring for Balanced String
#
# https://leetcode.com/problems/replace-the-substring-for-balanced-string/description/
#
# algorithms
# Medium (40.86%)
# Likes:    1291
# Dislikes: 225
# Total Accepted:    48.3K
# Total Submissions: 118.1K
# Testcase Example:  '"QWER"'
#
# You are given a string s of length n containing only four kinds of
# characters: 'Q', 'W', 'E', and 'R'.
# 
# A string is said to be balanced if each of its characters appears n / 4 times
# where n is the length of the string.
# 
# Return the minimum length of the substring that can be replaced with any
# other string of the same length to make s balanced. If s is already balanced,
# return 0.
# 
# 
# Example 1:
# 
# 
# Input: s = "QWER"
# Output: 0
# Explanation: s is already balanced.
# 
# 
# Example 2:
# 
# 
# Input: s = "QQWE"
# Output: 1
# Explanation: We need to replace a 'Q' to 'R', so that "RQWE" (or "QRWE") is
# balanced.
# 
# 
# Example 3:
# 
# 
# Input: s = "QQQW"
# Output: 2
# Explanation: We can replace the first "QQ" to "ER". 
# 
# 
# 
# Constraints:
# 
# 
# n == s.length
# 4 <= n <= 10^5
# n is a multiple of 4.
# s contains only 'Q', 'W', 'E', and 'R'.
# 
# 
#

# @lc code=start
from collections import Counter


class Solution:
    def balancedString(self, s: str) -> int:
        limit = len(s) // 4
        count = Counter(s)

        if all(count[ch] <= limit for ch in "QWER"):
            return 0

        answer = len(s)
        left = 0

        for right, ch in enumerate(s):
            count[ch] -= 1

            while left <= right and all(count[c] <= limit for c in "QWER"):
                answer = min(answer, right - left + 1)
                count[s[left]] += 1
                left += 1

        return answer
# @lc code=end

# Explanation
# -----------
# A balanced string of length n needs at most n/4 of each character outside the
# replacement window. Count the entire string, then slide a window and subtract
# characters as they enter the window. When every outside count is <= n/4, the
# current window is sufficient to replace, so try shrinking from the left.
#
# This reframes the problem: we do not need to know the replacement content,
# only that the outside part is already not over quota.
#
# The Counter stores outside-window counts. The sliding window gives the
# minimum-length substring satisfying the invariant.
#
# Edge cases: already balanced returns 0; one character heavily over quota;
# repeated shrinking after a valid window ensures minimal length.
#
# Time complexity: O(n), with constant four-character checks.
# Space complexity: O(1).
