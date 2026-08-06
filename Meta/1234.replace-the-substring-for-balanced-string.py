#
# @lc app=leetcode id=1234 lang=python3
#
# [1234] Replace the Substring for Balanced String
#
# https://leetcode.com/problems/replace-the-substring-for-balanced-string/description/
#
# algorithms
# Medium (41.24%)
# Likes:    1303
# Dislikes: 227
# Total Accepted:    50.1K
# Total Submissions: 121K
# Testcase Example:  "\"QWER\""
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
# Example 1:
#
# Input: s = "QWER"
# Output: 0
# Explanation: s is already balanced.
#
# Example 2:
#
# Input: s = "QQWE"
# Output: 1
# Explanation: We need to replace a 'Q' to 'R', so that "RQWE" (or "QRWE") is
# balanced.
#
# Example 3:
#
# Input: s = "QQQW"
# Output: 2
# Explanation: We can replace the first "QQ" to "ER".
#
# Constraints:
#
# n == s.length
#
# 4 <= n <= 10^5
#
# n is a multiple of 4.
#
# s contains only 'Q', 'W', 'E', and 'R'.
#


# @lc code=start
from collections import Counter

class Solution:
    def balancedString(self, s: str) -> int:
        """
        Interview explanation:
        String of QWER length n; balanced if each char appears n/4 times.
        Find minimum substring to replace so outside that window each count
        <= n/4. Sliding window: shrink while excess chars covered.

        Algorithm:
        - Count all; need = chars with count > n/4; window covers excess:
          expand right, shrink left while valid; min window length

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        m = n // 4
        cnt = Counter(s)
        if all(v <= m for v in cnt.values()):
            return 0
        ans = n
        left = 0
        for right, ch in enumerate(s):
            cnt[ch] -= 1
            while left <= right and all(v <= m for v in cnt.values()):
                ans = min(ans, right - left + 1)
                cnt[s[left]] += 1
                left += 1
        return ans
# @lc code=end
