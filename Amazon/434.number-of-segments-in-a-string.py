#
# @lc app=leetcode id=434 lang=python3
#
# [434] Number of Segments in a String
#
# https://leetcode.com/problems/number-of-segments-in-a-string/description/
#
# algorithms
# Easy (37.61%)
# Likes:    928
# Dislikes: 1349
# Total Accepted:    295K
# Total Submissions: 784K
# Testcase Example:  "\"Hello, my name is John\""
#
# Given a string s, return the number of segments in the string.
#
# A segment is defined to be a contiguous sequence of non-space characters.
#
# Example 1:
#
# Input: s = "Hello, my name is John"
# Output: 5
# Explanation: The five segments are ["Hello,", "my", "name", "is", "John"]
#
# Example 2:
#
# Input: s = "Hello"
# Output: 1
#
# Constraints:
#
# 0 <= s.length <= 300
#
# s consists of lowercase and uppercase English letters, digits, or one of the
# following characters "!@#$%^&*()_+-=',.:".
#
# The only space character in s is ' '.
#

# @lc code=start

class Solution:
    def countSegments(self, s: str) -> int:
        """
        Interview explanation:
        A segment is a maximal run of non-space characters. Count transitions
        into a non-space run (or simply split on whitespace).

        Algorithm:
        - Count positions where s[i] != ' ' and (i==0 or s[i-1]==' ').

        Complexity: O(n) time, O(1) space.
        """
        count = 0
        for i, ch in enumerate(s):
            if ch != " " and (i == 0 or s[i - 1] == " "):
                count += 1
        return count
# @lc code=end
