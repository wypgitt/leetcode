#
# @lc app=leetcode id=1624 lang=python3
#
# [1624] Largest Substring Between Two Equal Characters
#
# https://leetcode.com/problems/largest-substring-between-two-equal-characters/description/
#
# algorithms
# Easy (68.35%)
# Likes:    1421
# Dislikes: 68
# Total Accepted:    185K
# Total Submissions: 271K
# Testcase Example:  "\"aa\""
#
# Given a string s, return the length of the longest substring between two
# equal characters, excluding the two characters. If there is no such substring
# return -1.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s = "aa"
# Output: 0
# Explanation: The optimal substring here is an empty substring between the two
# 'a's.
#
# Example 2:
#
# Input: s = "abca"
# Output: 2
# Explanation: The optimal substring here is "bc".
#
# Example 3:
#
# Input: s = "cbzxy"
# Output: -1
# Explanation: There are no characters that appear twice in s.
#
# Constraints:
#
# 1 <= s.length <= 300
#
# s contains only lowercase English letters.
#

# @lc code=start
class Solution:
    def maxLengthBetweenEqualCharacters(self, s: str) -> int:
        """
        Interview explanation:
        Max chars strictly between two equal characters = max (last-first-1).

        Algorithm (hash map first/last):
        - Record first index; for each i update ans with i - first[s[i]] - 1.

        Complexity: O(n) time, O(1) alphabet space.
        """
        first = {}
        ans = -1
        for i, ch in enumerate(s):
            if ch in first:
                ans = max(ans, i - first[ch] - 1)
            else:
                first[ch] = i
        return ans

    def maxLengthBetweenEqualCharacters_last(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: store first and last for each char; max last-first-1.

        Algorithm:
        - first/last arrays; scan; compute max over alphabet.

        Complexity: O(n) time, O(1) space.
        """
        first = [-1] * 26
        last = [-1] * 26
        for i, ch in enumerate(s):
            idx = ord(ch) - 97
            if first[idx] == -1:
                first[idx] = i
            last[idx] = i
        ans = -1
        for i in range(26):
            if first[i] != -1 and last[i] > first[i]:
                ans = max(ans, last[i] - first[i] - 1)
        return ans
# @lc code=end
