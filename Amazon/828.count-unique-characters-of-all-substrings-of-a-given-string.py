#
# @lc app=leetcode id=828 lang=python3
#
# [828] Count Unique Characters of All Substrings of a Given String
#
# https://leetcode.com/problems/count-unique-characters-of-all-substrings-of-a-given-string/description/
#
# algorithms
# Hard (53.88%)
# Likes:    2262
# Dislikes: 260
# Total Accepted:    85.9K
# Total Submissions: 159K
# Testcase Example:  "\"ABC\""
#
# Let's define a function countUniqueChars(s) that returns the number of unique
# characters in s.
#
# For example, calling countUniqueChars(s) if s = "LEETCODE" then "L", "T",
# "C", "O", "D" are the unique characters since they appear only once in s,
# therefore countUniqueChars(s) = 5.
#
# Given a string s, return the sum of countUniqueChars(t) where t is a
# substring of s. The test cases are generated such that the answer fits in a
# 32-bit integer.
#
# Notice that some substrings can be repeated so in this case you have to count
# the repeated ones too.
#
# Example 1:
#
# Input: s = "ABC"
# Output: 10
# Explanation: All possible substrings are: "A","B","C","AB","BC" and "ABC".
# Every substring is composed with only unique letters.
# Sum of lengths of all substring is 1 + 1 + 1 + 2 + 2 + 3 = 10
#
# Example 2:
#
# Input: s = "ABA"
# Output: 8
# Explanation: The same as example 1, except countUniqueChars("ABA") = 1.
#
# Example 3:
#
# Input: s = "LEETCODE"
# Output: 92
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of uppercase English letters only.
#

# @lc code=start

class Solution:
    def uniqueLetterString(self, s: str) -> int:
        """
        Interview explanation:
        Contribution counting: for each index i, character s[i] is unique in
        substrings where it appears once — between previous and next occurrence
        of the same letter. Count = (i-prev)*(next-i).

        Algorithm:
        - For each letter track last two positions; when seeing a new occurrence,
          add contribution of previous; finish with end sentinels.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        # last[c] = (prev_prev, prev) indices of char c
        last = {c: (-1, -1) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        ans = 0
        for i, ch in enumerate(s):
            pprev, prev = last[ch]
            ans += (prev - pprev) * (i - prev)
            last[ch] = (prev, i)
        n = len(s)
        for ch, (pprev, prev) in last.items():
            ans += (prev - pprev) * (n - prev)
        return ans
# @lc code=end
