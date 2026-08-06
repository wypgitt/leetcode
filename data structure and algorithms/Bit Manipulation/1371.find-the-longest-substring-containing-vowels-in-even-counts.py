#
# @lc app=leetcode id=1371 lang=python3
#
# [1371] Find the Longest Substring Containing Vowels in Even Counts
#
# https://leetcode.com/problems/find-the-longest-substring-containing-vowels-in-even-counts/description/
#
# algorithms
# Medium (75.57%)
# Likes:    2586
# Dislikes: 142
# Total Accepted:    143K
# Total Submissions: 190K
# Testcase Example:  "\"eleetminicoworoep\""
#
# Given the string s, return the size of the longest substring containing each
# vowel an even number of times. That is, 'a', 'e', 'i', 'o', and 'u' must
# appear an even number of times.
#
# Example 1:
#
# Input: s = "eleetminicoworoep"
# Output: 13
# Explanation: The longest substring is "leetminicowor" which contains two each
# of the vowels: e, i and o and zero of the vowels: a and u.
#
# Example 2:
#
# Input: s = "leetcodeisgreat"
# Output: 5
# Explanation: The longest substring is "leetc" which contains two e's.
#
# Example 3:
#
# Input: s = "bcbcbc"
# Output: 6
# Explanation: In this case, the given string "bcbcbc" is the longest because
# all vowels: a, e, i, o and u appear zero times.
#
# Constraints:
#
# 1 <= s.length <= 5 x 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start

class Solution:
    def findTheLongestSubstring(self, s: str) -> int:
        """
        Interview explanation:
        Vowels aeiou must each appear even times in the substring. Track a
        5-bit parity mask of vowel counts; longest subarray with XOR=0 between
        prefix masks — first index of each mask gives max length.

        Algorithm:
        - Map aeiou→bits 0..4; mask^=1<<bit for vowels
        - seen[mask]=first index; ans=max(i-seen[mask])

        Complexity: O(n) time, O(1) space (32 masks).
        """
        vowels = {"a": 0, "e": 1, "i": 2, "o": 3, "u": 4}
        seen = {0: -1}
        mask = 0
        ans = 0
        for i, ch in enumerate(s):
            if ch in vowels:
                mask ^= 1 << vowels[ch]
            if mask in seen:
                ans = max(ans, i - seen[mask])
            else:
                seen[mask] = i
        return ans
# @lc code=end
