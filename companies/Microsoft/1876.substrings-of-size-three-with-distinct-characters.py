#
# @lc app=leetcode id=1876 lang=python3
#
# [1876] Substrings of Size Three with Distinct Characters
#
# https://leetcode.com/problems/substrings-of-size-three-with-distinct-characters/description/
#
# algorithms
# Easy (76.98%)
# Likes:    1724
# Dislikes: 58
# Total Accepted:    232K
# Total Submissions: 302K
# Testcase Example:  "\"xyzzaz\""
#
# A string is good if there are no repeated characters.
#
# Given a string s, return the number of good substrings of length three in s.
#
# Note that if there are multiple occurrences of the same substring, every
# occurrence should be counted.
#
# A substring is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: s = "xyzzaz"
# Output: 1
# Explanation: There are 4 substrings of size 3: "xyz", "yzz", "zza", and
# "zaz".
# The only good substring of length 3 is "xyz".
#
# Example 2:
#
# Input: s = "aababcabc"
# Output: 4
# Explanation: There are 7 substrings of size 3: "aab", "aba", "bab", "abc",
# "bca", "cab", and "abc".
# The good substrings are "abc", "bca", "cab", and "abc".
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def countGoodSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Count length-3 substrings with all distinct characters.

        Algorithm:
        - For i in 0..n-3: if len(set(s[i:i+3]))==3: count++.

        Complexity: O(n) time, O(1) space.
        """
        return sum(1 for i in range(len(s) - 2) if len(set(s[i : i + 3])) == 3)

    def countGoodSubstrings_direct(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: compare three chars without building a set.

        Algorithm:
        - a!=b and b!=c and a!=c for each window.

        Complexity: O(n) time.
        """
        ans = 0
        for i in range(len(s) - 2):
            a, b, c = s[i], s[i + 1], s[i + 2]
            if a != b and b != c and a != c:
                ans += 1
        return ans
# @lc code=end
