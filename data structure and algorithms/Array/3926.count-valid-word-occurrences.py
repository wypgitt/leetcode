#
# @lc app=leetcode id=3926 lang=python3
#
# [3926] Count Valid Word Occurrences
#
# https://leetcode.com/problems/count-valid-word-occurrences/description/
#
# algorithms
# Medium (48.45%)
# Likes:    49
# Dislikes: 50
# Total Accepted:    23.2K
# Total Submissions: 47.9K
# Testcase Example:  "[\"hello wor\",\"ld hello\"]\n[\"hello\",\"world\",\"wor\"]"
#
#
# You are given an array of strings chunks. Concatenate all strings in
# chunks in order to form a string s.
#
# You are also given an array of strings queries.
#
# A joiner hyphen is a hyphen character '-' in s whose previous and next
# characters both exist and are lowercase English letters.
#
# A word is a maximal substring of s consisting only of lowercase English
# letters and joiner hyphens.
#
# All other characters, including spaces and hyphens that are not joiner
# hyphens, are treated as separators.
#
# Return an integer array ans, where ans[i] is the number of times
# queries[i] appears as a word in s.
#
# Example 1:
#
# Input: chunks = ["hello wor","ld hello"], queries =
# ["hello","world","wor"]
#
# Output: [2,1,0]
#
# Explanation:
#
# After concatenating all strings in chunks, s = "hello world hello".
#
# The words are "hello", "world", and "hello".
#
# The substring "wor" appears inside "world", but it is not a full word.
#
# Example 2:
#
# Input: chunks = ["a-b a--b ","a-","b"], queries = ["a-b","a","b"]
#
# Output: [2,1,1]
#
# Explanation:
#
# After concatenating all strings in chunks, s = "a-b a--b a-b".
#
# In "a-b", the hyphen is a joiner hyphen because it is between two
# lowercase English letters, so "a-b" is one word.
#
# In "a--b", neither hyphen is a joiner hyphen, so it is split into the
# words "a" and "b".
#
# Therefore, the words are "a-b", "a", "b", and "a-b".
#
# Example 3:
#
# Input: chunks = ["-cat dog- mouse"], queries =
# ["cat","dog","mouse","cat-dog"]
#
# Output: [1,1,1,0]
#
# Explanation:
#
# After concatenating all strings in chunks, s = "-cat dog- mouse".
#
# The leading hyphen before "cat" and the trailing hyphen after "dog" are
# not joiner hyphens, so they are separators.
#
# The words are "cat", "dog", and "mouse".
#
# Constraints:
#
# 1 <= chunks.length <= 10^5
#
# 1 <= chunks[i].length <= 10^5
#
# The total length of all strings in chunks does not exceed 10^5.
#
# chunks[i] consists only of lowercase English letters, spaces, and '-'.
#
# 1 <= queries.length <= 10^5
#
# 1 <= queries[i].length <= 10^5
#
# The total length of all strings in queries does not exceed 10^5.
#
# queries[i] consists only of lowercase English letters and '-'.
#
# queries[i] is a valid word: it does not start or end with '-', and it
# does not contain two consecutive hyphens.
#

# @lc code=start

from collections import Counter


class Solution:
    def countWordOccurrences(self, chunks: list[str], queries: list[str]) -> list[int]:
        """
        Interview explanation:
        Concatenate chunks, then extract maximal words where letters and joiner
        hyphens (letter-hyphen-letter) stay inside a word; count query hits.

        Algorithm:
        - Join chunks into s.
        - Scan s: start a word on a letter; extend through letters and joiner '-'.
        - Counter the extracted words; answer each query by lookup.

        Complexity: O(|s| + |queries|) time, O(|s|) space.
        """
        s = "".join(chunks)
        n = len(s)
        words = []
        i = 0
        while i < n:
            if "a" <= s[i] <= "z":
                j = i + 1
                while j < n:
                    if "a" <= s[j] <= "z":
                        j += 1
                    elif (
                        s[j] == "-"
                        and j + 1 < n
                        and "a" <= s[j + 1] <= "z"
                        and "a" <= s[j - 1] <= "z"
                    ):
                        j += 1
                    else:
                        break
                words.append(s[i:j])
                i = j
            else:
                i += 1
        cnt = Counter(words)
        return [cnt[q] for q in queries]
# @lc code=end
