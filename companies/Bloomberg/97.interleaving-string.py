#
# @lc app=leetcode id=97 lang=python3
#
# [97] Interleaving String
#
# https://leetcode.com/problems/interleaving-string/description/
#
# algorithms
# Medium (43.95%)
# Likes:    8862
# Dislikes: 556
# Total Accepted:    786.8K
# Total Submissions: 1.8M
# Testcase Example:  '"aabcc"\n"dbbca"\n"aadbbcbcac"'
#
# Given strings s1, s2, and s3, find whether s3 is formed by an interleaving of
# s1 and s2.
# 
# An interleaving of two strings s and t is a configuration where s and t are
# divided into n and m substrings respectively, such that:
# 
# 
# s = s1 + s2 + ... + sn
# t = t1 + t2 + ... + tm
# |n - m| <= 1
# The interleaving is s1 + t1 + s2 + t2 + s3 + t3 + ... or t1 + s1 + t2 + s2 +
# t3 + s3 + ...
# 
# 
# Note: a + b is the concatenation of strings a and b.
# 
# 
# Example 1:
# 
# 
# Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"
# Output: true
# Explanation: One way to obtain s3 is:
# Split s1 into s1 = "aa" + "bc" + "c", and s2 into s2 = "dbbc" + "a".
# Interleaving the two splits, we get "aa" + "dbbc" + "bc" + "a" + "c" =
# "aadbbcbcac".
# Since s3 can be obtained by interleaving s1 and s2, we return true.
# 
# 
# Example 2:
# 
# 
# Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"
# Output: false
# Explanation: Notice how it is impossible to interleave s2 with any other
# string to obtain s3.
# 
# 
# Example 3:
# 
# 
# Input: s1 = "", s2 = "", s3 = ""
# Output: true
# 
# 
# 
# Constraints:
# 
# 
# 0 <= s1.length, s2.length <= 100
# 0 <= s3.length <= 200
# s1, s2, and s3 consist of lowercase English letters.
# 
# 
# 
# Follow up: Could you solve it using only O(s2.length) additional memory
# space?
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        """
        Interview explanation:
        DP over prefixes answers whether s3[:i+j] can be formed from s1[:i] and
        s2[:j]. The last character of such an interleaving must come either from
        s1[i-1] or s2[j-1], so each state depends on top and left states. A
        one-dimensional array is enough.

        Edge cases and tests:
        - Length mismatch returns False immediately.
        - Empty s1 or s2 reduces to string equality with the other.
        - Repeated characters require DP, not greedy choice.

        Complexity: O(m*n) time, O(n) space.
        """
        if len(s1) + len(s2) != len(s3):
            return False

        n = len(s2)
        dp = [False] * (n + 1)
        dp[0] = True

        for i in range(len(s1) + 1):
            for j in range(n + 1):
                if i == 0 and j == 0:
                    continue
                k = i + j - 1
                from_s1 = i > 0 and dp[j] and s1[i - 1] == s3[k]
                from_s2 = j > 0 and dp[j - 1] and s2[j - 1] == s3[k]
                dp[j] = from_s1 or from_s2

        return dp[n]
# @lc code=end


