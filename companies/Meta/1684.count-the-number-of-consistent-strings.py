#
# @lc app=leetcode id=1684 lang=python3
#
# [1684] Count the Number of Consistent Strings
#
# https://leetcode.com/problems/count-the-number-of-consistent-strings/description/
#
# algorithms
# Easy (88.52%)
# Likes:    2292
# Dislikes: 91
# Total Accepted:    454K
# Total Submissions: 513K
# Testcase Example:  "\"ab\""
#
# You are given a string allowed consisting of distinct characters and an array
# of strings words. A string is consistent if all characters in the string
# appear in the string allowed.
#
# Return the number of consistent strings in the array words.
#
# Example 1:
#
# Input: allowed = "ab", words = ["ad","bd","aaab","baa","badab"]
# Output: 2
# Explanation: Strings "aaab" and "baa" are consistent since they only contain
# characters 'a' and 'b'.
#
# Example 2:
#
# Input: allowed = "abc", words = ["a","b","c","ab","ac","bc","abc"]
# Output: 7
# Explanation: All strings are consistent.
#
# Example 3:
#
# Input: allowed = "cad", words = ["cc","acd","b","ba","bac","bad","ac","d"]
# Output: 4
# Explanation: Strings "cc", "acd", "ac", and "d" are consistent.
#
# Constraints:
#
# 1 <= words.length <= 10^4
#
# 1 <= allowed.length <=^ 26
#
# 1 <= words[i].length <= 10
#
# The characters in allowed are distinct.
#
# words[i] and allowed contain only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def countConsistentStrings(self, allowed: str, words: List[str]) -> int:
        """
        Interview explanation:
        Word is consistent if every char is in allowed. Use a set/bitmask of allowed.

        Algorithm:
        - allow=set(allowed); count words where set(w)subseteq allow.

        Complexity: O(total chars) time, O(1) space for alphabet.
        """
        allow = set(allowed)
        return sum(all(c in allow for c in w) for w in words)

    def countConsistentStrings_bitmask(self, allowed: str, words: List[str]) -> int:
        """
        Interview explanation:
        Alternate: bitmasks for allowed and each word; word ok if word_mask ⊆ allow_mask.

        Algorithm:
        - am=bits of allowed; for w: wm|=1<<(c-'a'); count wm&~am==0.

        Complexity: O(total chars) time, O(1) space.
        """
        am = 0
        for c in allowed:
            am |= 1 << (ord(c) - 97)
        ans = 0
        for w in words:
            wm = 0
            for c in w:
                wm |= 1 << (ord(c) - 97)
            if wm & ~am == 0:
                ans += 1
        return ans
# @lc code=end
