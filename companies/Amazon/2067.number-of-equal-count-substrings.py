#
# @lc app=leetcode id=2067 lang=python3
#
# [2067] Number of Equal Count Substrings
#
# https://leetcode.com/problems/number-of-equal-count-substrings/description/
#
# algorithms
# Medium (45.59%)
# Likes:    113
# Dislikes: 11
# Total Accepted:    4.2K
# Total Submissions: 9.2K
# Testcase Example:  "\"aaabcbbcc\"\n3"
#
#
# You are given a 0-indexed string s consisting of only lowercase English
# letters, and an integer count. A substring of s is said to be an equal
# count substring if, for each unique letter in the substring, it appears
# exactly count times in the substring.
#
# Return the number of equal count substrings in s.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "aaabcbbcc", count = 3
# Output: 3
# Explanation:
# The substring that starts at index 0 and ends at index 2 is "aaa".
# The letter 'a' in the substring appears exactly 3 times.
# The substring that starts at index 3 and ends at index 8 is "bcbbcc".
# The letters 'b' and 'c' in the substring appear exactly 3 times.
# The substring that starts at index 0 and ends at index 8 is "aaabcbbcc".
# The letters 'a', 'b', and 'c' in the substring appear exactly 3 times.
#
# Example 2:
#
# Input: s = "abcd", count = 2
# Output: 0
# Explanation:
# The number of times each letter appears in s is less than count.
# Therefore, no substrings in s are equal count substrings, so return 0.
#
# Example 3:
#
# Input: s = "a", count = 5
# Output: 0
# Explanation:
# The number of times each letter appears in s is less than count.
# Therefore, no substrings in s are equal count substrings, so return 0
#
# Constraints:
#
# 1 <= s.length <= 3 * 10^4
#
# 1 <= count <= 3 * 10^4
#
# s consists only of lowercase English letters.
#
# @lc code=start
from collections import defaultdict


class Solution:
    def equalCountSubstrings(self, s: str, count: int) -> int:
        """
        Interview explanation:
        Premium. Count substrings where every character that appears does so
        exactly `count` times (different alphabets may appear).

        Algorithm:
        - For unique-char count u=1..26, window length must be u*count; slide
          fixed-size windows and check all present chars have freq==count.

        Complexity: O(26 * n) time, O(1) space.
        """
        n = len(s)
        ans = 0
        for unique in range(1, 27):
            need = unique * count
            if need > n:
                break
            freq = defaultdict(int)
            have = 0  # chars with freq == count
            nonzero = 0
            for i, ch in enumerate(s):
                prev = freq[ch]
                freq[ch] = prev + 1
                if prev == 0:
                    nonzero += 1
                if prev == count:
                    have -= 1
                if freq[ch] == count:
                    have += 1
                if i >= need:
                    left = s[i - need]
                    prev = freq[left]
                    if prev == count:
                        have -= 1
                    freq[left] = prev - 1
                    if prev - 1 == count:
                        have += 1
                    if prev - 1 == 0:
                        nonzero -= 1
                        del freq[left]
                if i + 1 >= need and have == unique == nonzero:
                    ans += 1
        return ans
# @lc code=end
