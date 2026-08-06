#
# @lc app=leetcode id=1531 lang=python3
#
# [1531] String Compression II
#
# https://leetcode.com/problems/string-compression-ii/description/
#
# algorithms
# Hard (52.2%)
# Likes:    2516
# Dislikes: 221
# Total Accepted:    107K
# Total Submissions: 205K
# Testcase Example:  "\"aaabcccd\""
#
# Run-length encoding is a string compression method that works by replacing
# consecutive identical characters (repeated 2 or more times) with the
# concatenation of the character and the number marking the count of the
# characters (length of the run). For example, to compress the string "aabccc"
# we replace "aa" by "a2" and replace "ccc" by "c3". Thus the compressed string
# becomes "a2bc3".
#
# Notice that in this problem, we are not adding '1' after single characters.
#
# Given a string s and an integer k. You need to delete at most k characters
# from s such that the run-length encoded version of s has minimum length.
#
# Find the minimum length of the run-length encoded version of s after deleting
# at most k characters.
#
# Example 1:
#
# Input: s = "aaabcccd", k = 2
# Output: 4
# Explanation: Compressing s without deleting anything will give us "a3bc3d" of
# length 6. Deleting any of the characters 'a' or 'c' would at most decrease
# the length of the compressed string to 5, for instance delete 2 'a' then we
# will have s = "abcccd" which compressed is abc3d. Therefore, the optimal way
# is to delete 'b' and 'd', then the compressed version of s will be "a3c3" of
# length 4.
#
# Example 2:
#
# Input: s = "aabbaa", k = 2
# Output: 2
# Explanation: If we delete both 'b' characters, the resulting compressed
# string would be "a4" of length 2.
#
# Example 3:
#
# Input: s = "aaaaaaaaaaa", k = 0
# Output: 3
# Explanation: Since k is zero, we cannot delete anything. The compressed
# string is "a11" of length 3.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# 0 <= k <= s.length
#
# s contains only lowercase English letters.
#

# @lc code=start
from functools import lru_cache


class Solution:
    def getLengthOfOptimalCompression(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Delete at most k chars to minimize run-length encoding length.
        DP on (index, last_char, last_count, deletes_left): decide delete or
        keep; when keep, update encoding length if run count hits 1/2/10/100.

        Algorithm:
        - Memo dfs(i, last, cnt, left); delete → dfs(i+1,last,cnt,left-1);
          keep → new_cnt / add cost for length digits.

        Complexity: O(n * 26 * n * k) states bounded carefully; n<=100.
        """
        n = len(s)

        @lru_cache(None)
        def dp(i: int, last: int, cnt: int, left: int) -> int:
            if left < 0:
                return 10**9
            if i == n:
                return 0
            # delete s[i]
            ans = dp(i + 1, last, cnt, left - 1)
            # keep s[i]
            ch = ord(s[i]) - 97
            if ch == last:
                add = 1 if cnt in (1, 9, 99) else 0
                ans = min(ans, add + dp(i + 1, last, cnt + 1, left))
            else:
                ans = min(ans, 1 + dp(i + 1, ch, 1, left))
            return ans

        return dp(0, 26, 0, k)
# @lc code=end
