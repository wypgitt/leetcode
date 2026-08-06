#
# @lc app=leetcode id=2743 lang=python3
#
# [2743] Count Substrings Without Repeating Character
#
# https://leetcode.com/problems/count-substrings-without-repeating-character/description/
#
# algorithms
# Medium (75.92%)
# Likes:    98
# Dislikes: 2
# Total Accepted:    9.5K
# Total Submissions: 12.6K
# Testcase Example:  "\"abcd\""
#
#
# You are given a string s consisting only of lowercase English letters.
# We call a substring special if it contains no character which has
# occurred at least twice (in other words, it does not contain a repeating
# character). Your task is to count the number of special substrings. For
# example, in the string "pop", the substring "po" is a special substring,
# however, "pop" is not special (since 'p' has occurred twice).
#
# Return the number of special substrings.
#
# A substring is a contiguous sequence of characters within a string. For
# example, "abc" is a substring of "abcd", but "acd" is not.
#
# Example 1:
#
# Input: s = "abcd"
# Output: 10
# Explanation: Since each character occurs once, every substring is a
# special substring. We have 4 substrings of length one, 3 of length two,
# 2 of length three, and 1 substring of length four. So overall there are
# 4 + 3 + 2 + 1 = 10 special substrings.
#
# Example 2:
#
# Input: s = "ooo"
# Output: 3
# Explanation: Any substring with a length of at least two contains a
# repeating character. So we have to count the number of substrings of
# length one, which is 3.
#
# Example 3:
#
# Input: s = "abab"
# Output: 7
# Explanation: Special substrings are as follows (sorted by their start
# positions):
# Special substrings of length 1: "a", "b", "a", "b"
# Special substrings of length 2: "ab", "ba", "ab"
# And it can be shown that there are no special substrings with a length
# of at least three. So the answer would be 4 + 3 = 7.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters
#
# @lc code=start
from collections import Counter


class Solution:
    def numberOfSpecialSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Count substrings with all unique characters (no repeats).

        Algorithm:
        - Sliding window with char counts; for each right, shrink while duplicate;
          add (right-left+1) substrings ending at right.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        cnt = Counter()
        ans = left = 0
        for right, c in enumerate(s):
            cnt[c] += 1
            while cnt[c] > 1:
                cnt[s[left]] -= 1
                left += 1
            ans += right - left + 1
        return ans

    def numberOfSpecialSubstrings_two_pointers(self, s: str) -> int:
        """
        Interview explanation:
        Alternate naming for the unique-char window count.

        Algorithm:
        - Same two pointers.

        Complexity: O(n) time, O(1) space.
        """
        return self.numberOfSpecialSubstrings(s)
# @lc code=end
