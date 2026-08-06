#
# @lc app=leetcode id=2937 lang=python3
#
# [2937] Make Three Strings Equal
#
# https://leetcode.com/problems/make-three-strings-equal/description/
#
# algorithms
# Easy (45.30%)
# Likes:    330
# Dislikes: 43
# Total Accepted:    41.9K
# Total Submissions: 92.6K
# Testcase Example:  "\"abc\"\n\"abb\"\n\"ab\""
#
#
# You are given three strings: s1, s2, and s3. In one operation you can
# choose one of these strings and delete its rightmost character. Note
# that you cannot completely empty a string.
#
# Return the minimum number of operations required to make the strings
# equal. If it is impossible to make them equal, return -1.
#
# Example 1:
#
# Input: s1 = "abc", s2 = "abb", s3 = "ab"
#
# Output: 2
#
# Explanation: Deleting the rightmost character from both s1 and s2 will
# result in three equal strings.
#
# Example 2:
#
# Input: s1 = "dac", s2 = "bac", s3 = "cac"
#
# Output: -1
#
# Explanation: Since the first letters of s1 and s2 differ, they cannot be
# made equal.
#
# Constraints:
#
# 1 <= s1.length, s2.length, s3.length <= 100
#
# s1, s2 and s3 consist only of lowercase English letters.
#

# @lc code=start

class Solution:
    def findMinimumOperations(self, s1: str, s2: str, s3: str) -> int:
        """
        Interview explanation:
        Only delete rightmost chars; final equal string must be a common prefix
        of all three (nonempty). Minimize deletions = total length - 3*prefix.

        Algorithm:
        - Longest common prefix length L; if L==0 return -1 else len sum - 3L.

        Complexity: O(min lengths) time, O(1) space.
        """
        i = 0
        m = min(len(s1), len(s2), len(s3))
        while i < m and s1[i] == s2[i] == s3[i]:
            i += 1
        if i == 0:
            return -1
        return len(s1) + len(s2) + len(s3) - 3 * i
# @lc code=end

