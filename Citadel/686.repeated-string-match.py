#
# @lc app=leetcode id=686 lang=python3
#
# [686] Repeated String Match
#
# https://leetcode.com/problems/repeated-string-match/description/
#
# algorithms
# Medium (39.56%)
# Likes:    2934
# Dislikes: 1014
# Total Accepted:    279K
# Total Submissions: 704K
# Testcase Example:  "\"abcd\""
#
# Given two strings a and b, return the minimum number of times you should
# repeat string a so that string b is a substring of it. If it is impossible
# for b to be a substring of a after repeating it, return -1.
#
# Notice: string "abc" repeated 0 times is "", repeated 1 time is "abc" and
# repeated 2 times is "abcabc".
#
# Example 1:
#
# Input: a = "abcd", b = "cdabcdab"
# Output: 3
# Explanation: We return 3 because by repeating a three times "abcdabcdabcd", b
# is a substring of it.
#
# Example 2:
#
# Input: a = "a", b = "aa"
# Output: 2
#
# Constraints:
#
# 1 <= a.length, b.length <= 10^4
#
# a and b consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def repeatedStringMatch(self, a: str, b: str) -> int:
        """
        Interview explanation:
        Minimum times to repeat a so that b is a substring. Need at least
        ceil(len(b)/len(a)) repeats; one or two more may be needed for alignment.

        Algorithm:
        - Start with k = ceil(len(b)/len(a)); check a*k and a*(k+1) (and maybe
          k+2 for wrap). Return first k where b in a*k, else -1.

        Complexity: O((k)*|a|) = O(|a|+|b|) string build/search typical.
        """
        if not b:
            return 0
        k = (len(b) + len(a) - 1) // len(a)
        for times in (k, k + 1, k + 2):
            if b in a * times:
                return times
        return -1
# @lc code=end
