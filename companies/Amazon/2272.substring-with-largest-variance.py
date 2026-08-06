#
# @lc app=leetcode id=2272 lang=python3
#
# [2272] Substring With Largest Variance
#
# https://leetcode.com/problems/substring-with-largest-variance/description/
#
# algorithms
# Hard (46.01%)
# Likes:    1933
# Dislikes: 214
# Total Accepted:    77K
# Total Submissions: 167.3K
# Testcase Example:  "\"aababbb\""
#
# The variance of a string is defined as the largest difference between the
# number of occurrences of any 2 characters present in the string. Note the two
# characters may or may not be the same.
#
# Given a string s consisting of lowercase English letters only, return the
# largest variance possible among all substrings of s.
#
# A substring is a contiguous sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "aababbb"
# Output: 3
# Explanation:
# All possible variances along with their respective substrings are listed
# below:
# - Variance 0 for substrings "a", "aa", "ab", "abab", "aababb", "ba", "b",
# "bb", and "bbb".
# - Variance 1 for substrings "aab", "aba", "abb", "aabab", "ababb", "aababbb",
# and "bab".
# - Variance 2 for substrings "aaba", "ababbb", "abbb", and "babb".
# - Variance 3 for substring "babbb".
# Since the largest possible variance is 3, we return it.
#
# Example 2:
#
# Input: s = "abcde"
# Output: 0
# Explanation:
# No letter occurs more than once in s, so the variance of every substring is 0.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^4
#
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def largestVariance(self, s: str) -> int:
        """
        Interview explanation:
        Variance of a substring = max char freq - min char freq (among chars that
        appear). Maximize over all substrings.

        Algorithm:
        - For every ordered pair (major, minor), run a Kadane-like scan: +1 for
          major, -1 for minor; reset when negative only if more minors remain;
          update when minor has appeared.

        Complexity: O(26*26*n) time, O(1) extra space.
        """
        ans = 0
        chars = set(s)
        for a in chars:
            for b in chars:
                if a == b:
                    continue
                maj = mn = 0
                rest_b = s.count(b)
                for ch in s:
                    if ch == a:
                        maj += 1
                    elif ch == b:
                        mn += 1
                        rest_b -= 1
                    if mn > 0:
                        ans = max(ans, maj - mn)
                    if maj < mn and rest_b > 0:
                        maj = mn = 0
        return ans

# @lc code=end
