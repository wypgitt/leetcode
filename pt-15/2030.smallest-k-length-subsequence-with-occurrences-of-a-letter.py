#
# @lc app=leetcode id=2030 lang=python3
#
# [2030] Smallest K-Length Subsequence With Occurrences of a Letter
#
# https://leetcode.com/problems/smallest-k-length-subsequence-with-occurrences-of-a-letter/description/
#
# algorithms
# Hard (39.88%)
# Likes:    518
# Dislikes: 15
# Total Accepted:    11.9K
# Total Submissions: 29.8K
# Testcase Example:  "\"leet\"\n3\n\"e\"\n1"
#
# You are given a string s, an integer k, a letter letter, and an integer
# repetition.
#
# Return the lexicographically smallest subsequence of s of length k that has
# the letter letter appear at least repetition times. The test cases are
# generated so that the letter appears in s at least repetition times.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
# A string a is lexicographically smaller than a string b if in the first
# position where a and b differ, string a has a letter that appears earlier in
# the alphabet than the corresponding letter in b.
#
#
#
# Example 1:
#
# Input: s = "leet", k = 3, letter = "e", repetition = 1
# Output: "eet"
# Explanation: There are four subsequences of length 3 that have the letter 'e'
# appear at least 1 time:
# - "lee" (from "leet")
# - "let" (from "leet")
# - "let" (from "leet")
# - "eet" (from "leet")
# The lexicographically smallest subsequence among them is "eet".
#
# Example 2:
#
# Input: s = "leetcode", k = 4, letter = "e", repetition = 2
# Output: "ecde"
# Explanation: "ecde" is the lexicographically smallest subsequence of length 4
# that has the letter "e" appear at least 2 times.
#
# Example 3:
#
# Input: s = "bb", k = 2, letter = "b", repetition = 2
# Output: "bb"
# Explanation: "bb" is the only subsequence of length 2 that has the letter "b"
# appear at least 2 times.
#
#
#
# Constraints:
#
#
# 1 <= repetition <= k <= s.length <= 5 * 10^4
#
#
# s consists of lowercase English letters.
#
#
# letter is a lowercase English letter, and appears in s at least repetition
# times.
#

# @lc code=start
class Solution:
    def smallestSubsequence(self, s: str, k: int, letter: str, repetition: int) -> str:
        """
        Interview explanation:
        Lex-smallest subsequence of length k containing `letter` at least
        `repetition` times.

        Algorithm:
        - Monotonic increasing stack with constraints: enough remaining length
          to fill k, and enough letters left (in stack + remaining suffix) to
          meet repetition; skip non-letters when slots must be reserved.

        Complexity: O(n) time, O(k) space.
        """
        n = len(s)
        remain_letter = s.count(letter)
        stack = []
        used_letter = 0
        for i, ch in enumerate(s):
            while (
                stack
                and stack[-1] > ch
                and len(stack) - 1 + (n - i) >= k
            ):
                if stack[-1] == letter:
                    if used_letter - 1 + remain_letter < repetition:
                        break
                    used_letter -= 1
                stack.pop()
            if len(stack) < k:
                need = repetition - used_letter
                slots_after = k - len(stack) - 1
                if ch == letter:
                    stack.append(ch)
                    used_letter += 1
                elif slots_after >= need:
                    stack.append(ch)
            if ch == letter:
                remain_letter -= 1
        return ''.join(stack)
# @lc code=end
