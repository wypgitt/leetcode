#
# @lc app=leetcode id=451 lang=python3
#
# [451] Sort Characters By Frequency
#
# https://leetcode.com/problems/sort-characters-by-frequency/description/
#
# algorithms
# Medium (75.66%)
# Likes:    9363
# Dislikes: 338
# Total Accepted:    1.2M
# Total Submissions: 1.6M
# Testcase Example:  "\"tree\""
#
# Given a string s, sort it in decreasing order based on the frequency of the
# characters. The frequency of a character is the number of times it appears in
# the string.
#
# Return the sorted string. If there are multiple answers, return any of them.
#
# Example 1:
#
# Input: s = "tree"
# Output: "eert"
# Explanation: 'e' appears twice while 'r' and 't' both appear once.
# So 'e' must appear before both 'r' and 't'. Therefore "eetr" is also a valid
# answer.
#
# Example 2:
#
# Input: s = "cccaaa"
# Output: "aaaccc"
# Explanation: Both 'c' and 'a' appear three times, so both "cccaaa" and
# "aaaccc" are valid answers.
# Note that "cacaca" is incorrect, as the same characters must be together.
#
# Example 3:
#
# Input: s = "Aabb"
# Output: "bbAa"
# Explanation: "bbaA" is also a valid answer, but "Aabb" is incorrect.
# Note that 'A' and 'a' are treated as two different characters.
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^5
#
# s consists of uppercase and lowercase English letters and digits.
#

# @lc code=start
from collections import Counter
import heapq


class Solution:
    def frequencySort(self, s: str) -> str:
        """
        Interview explanation:
        Bucket by frequency (best linear): count chars, put each char into
        buckets[freq], then emit from highest freq down (char * freq).

        Algorithm:
        - Counter; buckets[0..n] lists of chars.
        - For freq = n..1, for each char in bucket, append char*freq.

        Complexity: O(n) time and space.
        """
        count = Counter(s)
        n = len(s)
        buckets = [[] for _ in range(n + 1)]
        for ch, freq in count.items():
            buckets[freq].append(ch)
        parts = []
        for freq in range(n, 0, -1):
            for ch in buckets[freq]:
                parts.append(ch * freq)
        return "".join(parts)

    def frequencySort_heap(self, s: str) -> str:
        """
        Interview explanation:
        Alternate classic: max-heap (or nlargest) on (freq, char); emit
        char * freq in heap order.

        Algorithm:
        - Counter; heapq.nlargest by frequency; join char*freq.

        Complexity: O(n + k log k) time, O(n) space (k = distinct chars).
        """
        count = Counter(s)
        items = heapq.nlargest(len(count), count.items(), key=lambda x: x[1])
        return "".join(ch * freq for ch, freq in items)
# @lc code=end
