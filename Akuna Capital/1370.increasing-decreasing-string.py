#
# @lc app=leetcode id=1370 lang=python3
#
# [1370] Increasing Decreasing String
#
# https://leetcode.com/problems/increasing-decreasing-string/description/
#
# algorithms
# Easy (77.31%)
# Likes:    848
# Dislikes: 879
# Total Accepted:    102K
# Total Submissions: 132K
# Testcase Example:  "\"aaaabbbbcccc\""
#
# You are given a string s. Reorder the string using the following algorithm:
#
# Remove the smallest character from s and append it to the result.
#
# Remove the smallest character from s that is greater than the last appended
# character, and append it to the result.
#
# Repeat step 2 until no more characters can be removed.
#
# Remove the largest character from s and append it to the result.
#
# Remove the largest character from s that is smaller than the last appended
# character, and append it to the result.
#
# Repeat step 5 until no more characters can be removed.
#
# Repeat steps 1 through 6 until all characters from s have been removed.
#
# If the smallest or largest character appears more than once, you may choose
# any occurrence to append to the result.
#
# Return the resulting string after reordering s using this algorithm.
#
# Example 1:
#
# Input: s = "aaaabbbbcccc"
# Output: "abccbaabccba"
# Explanation: After steps 1, 2 and 3 of the first iteration, result = "abc"
# After steps 4, 5 and 6 of the first iteration, result = "abccba"
# First iteration is done. Now s = "aabbcc" and we go back to step 1
# After steps 1, 2 and 3 of the second iteration, result = "abccbaabc"
# After steps 4, 5 and 6 of the second iteration, result = "abccbaabccba"
#
# Example 2:
#
# Input: s = "rat"
# Output: "art"
# Explanation: The word "rat" becomes "art" after re-ordering it with the
# mentioned algorithm.
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of only lowercase English letters.
#

# @lc code=start

from collections import Counter


class Solution:
    def sortString(self, s: str) -> str:
        """
        Interview explanation:
        Repeatedly append smallest remaining char, then ascending unused,
        then largest, then descending unused, until empty.

        Algorithm:
        - Counter of letters; while remaining: sweep a→z then z→a taking one each

        Complexity: O(n) time (26 passes * n/26), O(1) extra for alphabet.
        """
        cnt = Counter(s)
        ans = []
        while len(ans) < len(s):
            for c in range(ord("a"), ord("z") + 1):
                ch = chr(c)
                if cnt[ch]:
                    ans.append(ch)
                    cnt[ch] -= 1
            for c in range(ord("z"), ord("a") - 1, -1):
                ch = chr(c)
                if cnt[ch]:
                    ans.append(ch)
                    cnt[ch] -= 1
        return "".join(ans)
# @lc code=end
