#
# @lc app=leetcode id=3884 lang=python3
#
# [3884] First Matching Character From Both Ends
#
# https://leetcode.com/problems/first-matching-character-from-both-ends/description/
#
# algorithms
# Easy (82.20%)
# Likes:    35
# Dislikes: 0
# Total Accepted:    60.3K
# Total Submissions: 73.4K
# Testcase Example:  "\"abcacbd\""
#
#
# You are given a string s of length n consisting of lowercase English
# letters.
#
# Return the smallest index i such that s[i] == s[n - i - 1].
#
# If no such index exists, return -1.
#
# Example 1:
#
# Input: s = "abcacbd"
#
# Output: 1
#
# Explanation:
#
# At index i = 1, s[1] and s[5] are both 'b'.
#
# No smaller index satisfies the condition, so the answer is 1.
#
# Example 2:
#
# Input: s = "abc"
#
# Output: 1
#
# Explanation:
#
# ​​​​​​​At index i = 1, the two compared positions coincide, so both
# characters are 'b'.
#
# No smaller index satisfies the condition, so the answer is 1.
#
# Example 3:
#
# Input: s = "abcdab"
#
# Output: -1
#
# Explanation:
#
# ​​​​​​​For every index i, the characters at positions i and n - i - 1
# are different.
#
# Therefore, no valid index exists, so the answer is -1.
#
# Constraints:
#
# 1 <= n == s.length <= 100
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def firstMatchingIndex(self, s: str) -> int:
        """
        Interview explanation:
        Smallest i with s[i] == s[n-1-i] (mirrored positions, including the middle).

        Algorithm:
        - Check i from 0..n-1; return the first match, else -1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        for i in range(n):
            if s[i] == s[n - 1 - i]:
                return i
        return -1
# @lc code=end
