#
# @lc app=leetcode id=3163 lang=python3
#
# [3163] String Compression III
#
# https://leetcode.com/problems/string-compression-iii/description/
#
# algorithms
# Medium (67.13%)
# Likes:    637
# Dislikes: 54
# Total Accepted:    206.6K
# Total Submissions: 307.7K
# Testcase Example:  "\"abcde\""
#
#
# Given a string word, compress it using the following algorithm:
#
# Begin with an empty string comp. While word is not empty, use the
# following operation:
#
# Remove a maximum length prefix of word made of a single character c
# repeating at most 9 times.
#
# Append the length of the prefix followed by c to comp.
#
# Return the string comp.
#
# Example 1:
#
# Input: word = "abcde"
#
# Output: "1a1b1c1d1e"
#
# Explanation:
#
# Initially, comp = "". Apply the operation 5 times, choosing "a", "b",
# "c", "d", and "e" as the prefix in each operation.
#
# For each prefix, append "1" followed by the character to comp.
#
# Example 2:
#
# Input: word = "aaaaaaaaaaaaaabb"
#
# Output: "9a5a2b"
#
# Explanation:
#
# Initially, comp = "". Apply the operation 3 times, choosing "aaaaaaaaa",
# "aaaaa", and "bb" as the prefix in each operation.
#
# For prefix "aaaaaaaaa", append "9" followed by "a" to comp.
#
# For prefix "aaaaa", append "5" followed by "a" to comp.
#
# For prefix "bb", append "2" followed by "b" to comp.
#
# Constraints:
#
# 1 <= word.length <= 2 * 10^5
#
# word consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def compressedString(self, word: str) -> str:
        """
        Interview explanation:
        Run-length encode, but each run chunk is at most length 9: emit
        digit+char repeatedly until the run is consumed.

        Algorithm:
        - Two pointers / scan: while same char, take min(9, remaining run),
          append str(cnt)+c, advance.

        Complexity: O(n) time, O(n) space for the output.
        """
        parts: list[str] = []
        i, n = 0, len(word)
        while i < n:
            j = i
            while j < n and word[j] == word[i] and j - i < 9:
                j += 1
            parts.append(str(j - i))
            parts.append(word[i])
            i = j
        return "".join(parts)

    def compressedString_groupby(self, word: str) -> str:
        """
        Interview explanation:
        Alternate: group identical characters, then split each group into
        chunks of size at most 9.

        Algorithm:
        - Iterate runs; for length L emit (9,c) floor(L/9) times and a remainder.

        Complexity: O(n) time, O(n) space.
        """
        parts: list[str] = []
        i, n = 0, len(word)
        while i < n:
            j = i
            while j < n and word[j] == word[i]:
                j += 1
            length = j - i
            c = word[i]
            while length > 0:
                take = min(9, length)
                parts.append(str(take))
                parts.append(c)
                length -= take
            i = j
        return "".join(parts)
# @lc code=end
