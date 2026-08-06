#
# @lc app=leetcode id=1374 lang=python3
#
# [1374] Generate a String With Characters That Have Odd Counts
#
# https://leetcode.com/problems/generate-a-string-with-characters-that-have-odd-counts/description/
#
# algorithms
# Easy (78.58%)
# Likes:    534
# Dislikes: 1288
# Total Accepted:    117K
# Total Submissions: 149K
# Testcase Example:  "4"
#
# Given an integer n, return a string with n characters such that each
# character in such string occurs an odd number of times.
#
# The returned string must contain only lowercase English letters. If there are
# multiples valid strings, return any of them.
#
# Example 1:
#
# Input: n = 4
# Output: "pppz"
# Explanation: "pppz" is a valid string since the character 'p' occurs three
# times and the character 'z' occurs once. Note that there are many other valid
# strings such as "ohhh" and "love".
#
# Example 2:
#
# Input: n = 2
# Output: "xy"
# Explanation: "xy" is a valid string since the characters 'x' and 'y' occur
# once. Note that there are many other valid strings such as "ag" and "ur".
#
# Example 3:
#
# Input: n = 7
# Output: "holasss"
#
# Constraints:
#
# 1 <= n <= 500
#

# @lc code=start

class Solution:
    def generateTheString(self, n: int) -> str:
        """
        Interview explanation:
        Return any string of length n where every distinct char has odd count.
        If n odd: n a's; if even: (n-1) a's + one b.

        Algorithm:
        - return 'a'*n if n odd else 'a'*(n-1)+'b'

        Complexity: O(n) time, O(n) space.
        """
        if n % 2:
            return "a" * n
        return "a" * (n - 1) + "b"
# @lc code=end
