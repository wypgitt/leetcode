#
# @lc app=leetcode id=2645 lang=python3
#
# [2645] Minimum Additions to Make Valid String
#
# https://leetcode.com/problems/minimum-additions-to-make-valid-string/description/
#
# algorithms
# Medium (51.27%)
# Likes:    596
# Dislikes: 29
# Total Accepted:    39.6K
# Total Submissions: 77.2K
# Testcase Example:  "\"b\""
#
# Given a string word to which you can insert letters "a", "b" or "c" anywhere
# and any number of times, return the minimum number of letters that must be
# inserted so that word becomes valid.
#
# A string is called valid if it can be formed by concatenating the string "abc"
# several times.
#
#
#
# Example 1:
#
# Input: word = "b"
# Output: 2
# Explanation: Insert the letter "a" right before "b", and the letter "c" right
# next to "b" to obtain the valid string "abc".
#
# Example 2:
#
# Input: word = "aaa"
# Output: 6
# Explanation: Insert letters "b" and "c" next to each "a" to obtain the valid
# string "abcabcabc".
#
# Example 3:
#
# Input: word = "abc"
# Output: 0
# Explanation: word is already valid. No modifications are needed.
#
#
#
# Constraints:
#
#
# 1 <= word.length <= 50
#
#
# word consists of letters "a", "b" and "c" only.
#

# @lc code=start
class Solution:
    def addMinimum(self, word: str) -> int:
        """
        Interview explanation:
        Make word a concatenation of "abc" by inserting the fewest letters.

        Algorithm:
        - Walk word matching the expected a→b→c cycle; each mismatch inserts
          one char. Finish any open cycle at the end.

        Complexity: O(n) time, O(1) space.
        """
        target = "abc"
        i = ans = expect = 0
        n = len(word)
        while i < n:
            if word[i] == target[expect]:
                i += 1
            else:
                ans += 1
            expect = (expect + 1) % 3
        if expect:
            ans += 3 - expect
        return ans

    def addMinimum_groups(self, word: str) -> int:
        """
        Interview explanation:
        Alternate: count how many "abc" groups are needed; inserts = 3*groups - n.

        Algorithm:
        - Start a new group whenever the next char is not strictly after the
          previous in a→b→c order (i.e. word[i] <= word[i-1]).

        Complexity: O(n) time, O(1) space.
        """
        groups = 1
        for i in range(1, len(word)):
            if word[i] <= word[i - 1]:
                groups += 1
        return groups * 3 - len(word)
# @lc code=end
