#
# @lc app=leetcode id=1758 lang=python3
#
# [1758] Minimum Changes To Make Alternating Binary String
#
# https://leetcode.com/problems/minimum-changes-to-make-alternating-binary-string/description/
#
# algorithms
# Easy (67.89%)
# Likes:    1846
# Dislikes: 57
# Total Accepted:    304K
# Total Submissions: 448K
# Testcase Example:  "\"0100\""
#
# You are given a string s consisting only of the characters '0' and '1'. In
# one operation, you can change any '0' to '1' or vice versa.
#
# The string is called alternating if no two adjacent characters are equal. For
# example, the string "010" is alternating, while the string "0100" is not.
#
# Return the minimum number of operations needed to make s alternating.
#
# Example 1:
#
# Input: s = "0100"
# Output: 1
# Explanation: If you change the last character to '1', s will be "0101", which
# is alternating.
#
# Example 2:
#
# Input: s = "10"
# Output: 0
# Explanation: s is already alternating.
#
# Example 3:
#
# Input: s = "1111"
# Output: 2
# Explanation: You need two operations to reach "0101" or "1010".
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def minOperations(self, s: str) -> int:
        """
        Interview explanation:
        Target is alternating 0101... or 1010.... Count mismatches vs 0101...;
        the other pattern's cost is n − that count; take the min.

        Algorithm:
        - diff0 = mismatches vs '0' on even indices / '1' on odd; return min(diff0, n-diff0).

        Complexity: O(n) time, O(1) space.
        """
        diff0 = sum(ch != ("0" if i % 2 == 0 else "1") for i, ch in enumerate(s))
        return min(diff0, len(s) - diff0)

    def minOperations_two_patterns(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: explicitly count mismatches against both alternating patterns.

        Algorithm:
        - Track a (start with 0) and b (start with 1); return min(a, b).

        Complexity: O(n) time, O(1) space.
        """
        a = b = 0
        for i, ch in enumerate(s):
            if ch != str(i % 2):
                a += 1
            if ch != str(1 - i % 2):
                b += 1
        return min(a, b)
# @lc code=end
