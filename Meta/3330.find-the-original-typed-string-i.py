#
# @lc app=leetcode id=3330 lang=python3
#
# [3330] Find the Original Typed String I
#
# https://leetcode.com/problems/find-the-original-typed-string-i/description/
#
# algorithms
# Easy (72.10%)
# Likes:    533
# Dislikes: 78
# Total Accepted:    199.8K
# Total Submissions: 277.1K
# Testcase Example:  "\"abbcccc\""
#
#
# Alice is attempting to type a specific string on her computer. However,
# she tends to be clumsy and may press a key for too long, resulting in a
# character being typed multiple times.
#
# Although Alice tried to focus on her typing, she is aware that she may
# still have done this at most once.
#
# You are given a string word, which represents the final output displayed
# on Alice's screen.
#
# Return the total number of possible original strings that Alice might
# have intended to type.
#
# Example 1:
#
# Input: word = "abbcccc"
#
# Output: 5
#
# Explanation:
#
# The possible strings are: "abbcccc", "abbccc", "abbcc", "abbc", and
# "abcccc".
#
# Example 2:
#
# Input: word = "abcd"
#
# Output: 1
#
# Explanation:
#
# The only possible string is "abcd".
#
# Example 3:
#
# Input: word = "aaaa"
#
# Output: 4
#
# Constraints:
#
# 1 <= word.length <= 100
#
# word consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def possibleStringCount(self, word: str) -> int:
        """
        Interview explanation:
        At most one long-press: for each run of identical letters of length L,
        we may shorten it by 1..L-1 (once globally), or leave the string as-is.

        Algorithm:
        - ans = 1 + sum(L - 1 over runs) = 1 + n - (#runs).

        Complexity: O(n) time, O(1) space.
        """
        ans = 1
        for i in range(1, len(word)):
            if word[i] == word[i - 1]:
                ans += 1
        return ans
# @lc code=end

