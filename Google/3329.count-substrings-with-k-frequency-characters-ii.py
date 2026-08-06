#
# @lc app=leetcode id=3329 lang=python3
#
# [3329] Count Substrings With K-Frequency Characters II
#
# https://leetcode.com/problems/count-substrings-with-k-frequency-characters-ii/description/
#
# algorithms
# Hard (70.28%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    1.1K
# Total Submissions: 1.5K
# Testcase Example:  "\"abacb\"\n2"
#
#
# Given a string s and an integer k, return the total number of substrings
# of s where at least one character appears at least k times.
#
# Example 1:
#
# Input: s = "abacb", k = 2
#
# Output: 4
#
# Explanation:
#
# The valid substrings are:
#
# "aba" (character 'a' appears 2 times).
#
# "abac" (character 'a' appears 2 times).
#
# "abacb" (character 'a' appears 2 times).
#
# "bacb" (character 'b' appears 2 times).
#
# Example 2:
#
# Input: s = "abcde", k = 1
#
# Output: 15
#
# Explanation:
#
# All substrings are valid because every character appears at least once.
#
# Constraints:
#
# 1 <= s.length <= 3 * 10^5
#
# 1 <= k <= s.length
#
# s consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def numberOfSubstrings(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Same as I with larger n: count substrings with some char frequency >= k.

        Algorithm:
        - Two pointers keep a maximal window with all frequencies < k.
        - Valid endings at right contribute `left` substrings.

        Complexity: O(n) time, O(1) space.
        """
        freq = [0] * 26
        left = 0
        ans = 0
        for right, ch in enumerate(s):
            idx = ord(ch) - 97
            freq[idx] += 1
            while freq[idx] >= k:
                freq[ord(s[left]) - 97] -= 1
                left += 1
            ans += left
        return ans
# @lc code=end

