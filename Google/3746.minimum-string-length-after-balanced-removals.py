#
# @lc app=leetcode id=3746 lang=python3
#
# [3746] Minimum String Length After Balanced Removals
#
# https://leetcode.com/problems/minimum-string-length-after-balanced-removals/description/
#
# algorithms
# Medium (78.54%)
# Likes:    62
# Dislikes: 8
# Total Accepted:    43K
# Total Submissions: 54.8K
# Testcase Example:  "\"aabbab\""
#
#
# You are given a string s consisting only of the characters 'a' and 'b'.
#
# You are allowed to repeatedly remove any substring where the number of
# 'a' characters is equal to the number of 'b' characters. After each
# removal, the remaining parts of the string are concatenated together
# without gaps.
#
# Return an integer denoting the minimum possible length of the string
# after performing any number of such operations.
#
# Example 1:
#
# Input: s = "aabbab"
#
# Output: 0
#
# Explanation:
#
# The substring "aabbab" has three 'a' and three 'b'. Since their counts
# are equal, we can remove the entire string directly. The minimum length
# is 0.
#
# Example 2:
#
# Input: s = "aaaa"
#
# Output: 4
#
# Explanation:
#
# Every substring of "aaaa" contains only 'a' characters. No substring can
# be removed as a result, so the minimum length remains 4.
#
# Example 3:
#
# Input: s = "aaabb"
#
# Output: 1
#
# Explanation:
#
# First, remove the substring "ab", leaving "aab". Next, remove the new
# substring "ab", leaving "a". No further removals are possible, so the
# minimum length is 1.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either 'a' or 'b'.
#

# @lc code=start
class Solution:
    def minLengthAfterRemovals(self, s: str) -> int:
        """
        Interview explanation:
        Each removal deletes equally many 'a's and 'b's, so |#a - #b| is invariant
        and is achievable as the final monochromatic length.

        Algorithm:
        - Return abs(count('a') - count('b')).

        Complexity: O(n) time, O(1) space.
        """
        return abs(s.count("a") - s.count("b"))

    def minLengthAfterRemovals_balance(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: maintain a running balance of a vs b.

        Algorithm:
        - bal += 1 for 'a', -1 for 'b'; answer abs(bal).

        Complexity: O(n) time, O(1) space.
        """
        bal = 0
        for ch in s:
            bal += 1 if ch == "a" else -1
        return abs(bal)
# @lc code=end
