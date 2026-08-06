#
# @lc app=leetcode id=1641 lang=python3
#
# [1641] Count Sorted Vowel Strings
#
# https://leetcode.com/problems/count-sorted-vowel-strings/description/
#
# algorithms
# Medium (79.39%)
# Likes:    3947
# Dislikes: 93
# Total Accepted:    210K
# Total Submissions: 265K
# Testcase Example:  "1"
#
# Given an integer n, return the number of strings of length n that consist
# only of vowels (a, e, i, o, u) and are lexicographically sorted.
#
# A string s is lexicographically sorted if for all valid i, s[i] is the same
# as or comes before s[i+1] in the alphabet.
#
# Example 1:
#
# Input: n = 1
# Output: 5
# Explanation: The 5 sorted strings that consist of vowels only are
# ["a","e","i","o","u"].
#
# Example 2:
#
# Input: n = 2
# Output: 15
# Explanation: The 15 sorted strings that consist of vowels only are
# ["aa","ae","ai","ao","au","ee","ei","eo","eu","ii","io","iu","oo","ou","uu"].
# Note that "ea" is not a valid string since 'e' comes after 'a' in the
# alphabet.
#
# Example 3:
#
# Input: n = 33
# Output: 66045
#
# Constraints:
#
# 1 <= n <= 50
#

# @lc code=start
class Solution:
    def countVowelStrings(self, n: int) -> int:
        """
        Interview explanation:
        Lex-sorted strings of length n using aeiou = combinations with repetition
        C(n+5-1, 5-1) = C(n+4, 4).

        Algorithm (combinatorics):
        - Return (n+4)*(n+3)*(n+2)*(n+1)//24.

        Complexity: O(1) time/space.
        """
        return (n + 4) * (n + 3) * (n + 2) * (n + 1) // 24

    def countVowelStrings_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate DP: dp[i][v] = strings length i ending with vowel index v;
        or dp[v] cumulative.

        Algorithm (DP):
        - Start [1]*5; for each length, prefix sums so nondecreasing vowels.

        Complexity: O(n) time, O(1) space.
        """
        dp = [1] * 5
        for _ in range(n - 1):
            for i in range(1, 5):
                dp[i] += dp[i - 1]
        return sum(dp)
# @lc code=end
