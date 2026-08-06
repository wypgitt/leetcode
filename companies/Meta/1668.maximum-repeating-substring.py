#
# @lc app=leetcode id=1668 lang=python3
#
# [1668] Maximum Repeating Substring
#
# https://leetcode.com/problems/maximum-repeating-substring/description/
#
# algorithms
# Easy (42.11%)
# Likes:    843
# Dislikes: 305
# Total Accepted:    117K
# Total Submissions: 279K
# Testcase Example:  "\"ababc\""
#
# For a string sequence, a string word is k-repeating if word concatenated k
# times is a substring of sequence. The word's maximum k-repeating value is the
# highest value k where word is k-repeating in sequence. If word is not a
# substring of sequence, word's maximum k-repeating value is 0.
#
# Given strings sequence and word, return the maximum k-repeating value of word
# in sequence.
#
# Example 1:
#
# Input: sequence = "ababc", word = "ab"
# Output: 2
# Explanation: "abab" is a substring in "ababc".
#
# Example 2:
#
# Input: sequence = "ababc", word = "ba"
# Output: 1
# Explanation: "ba" is a substring in "ababc". "baba" is not a substring in
# "ababc".
#
# Example 3:
#
# Input: sequence = "ababc", word = "ac"
# Output: 0
# Explanation: "ac" is not a substring in "ababc".
#
# Constraints:
#
# 1 <= sequence.length <= 100
#
# 1 <= word.length <= 100
#
# sequence and word contains only lowercase English letters.
#

# @lc code=start
class Solution:
    def maxRepeating(self, sequence: str, word: str) -> int:
        """
        Interview explanation:
        Largest k such that word*k is a substring of sequence. Try k from
        len(seq)//len(word) down, or grow while word*(k+1) in sequence.

        Algorithm:
        - k=0; while word*(k+1) in sequence: k+=1; return k

        Complexity: O(n^2 / m) string checks worst-case, n=|sequence|.
        """
        k = 0
        while word * (k + 1) in sequence:
            k += 1
        return k

    def maxRepeating_kmp(self, sequence: str, word: str) -> int:
        """
        Interview explanation:
        Alternate: build word*max_k and find longest prefix of that which is a
        substring via repeated search / DP matching.

        Algorithm:
        - For each start, count consecutive word matches.

        Complexity: O(n*m) time.
        """
        n, m = len(sequence), len(word)
        if m == 0:
            return 0
        best = 0
        for i in range(n):
            k = 0
            j = i
            while j + m <= n and sequence[j : j + m] == word:
                k += 1
                j += m
            best = max(best, k)
        return best
# @lc code=end
