#
# @lc app=leetcode id=3677 lang=python3
#
# [3677] Count Binary Palindromic Numbers
#
# https://leetcode.com/problems/count-binary-palindromic-numbers/description/
#
# algorithms
# Hard (33.78%)
# Likes:    86
# Dislikes: 4
# Total Accepted:    16.3K
# Total Submissions: 48.4K
# Testcase Example:  "9"
#
#
# You are given a non-negative integer n.
#
# A non-negative integer is called binary-palindromic if its binary
# representation (written without leading zeros) reads the same forward
# and backward.
#
# Return the number of integers k such that 0 <= k <= n and the binary
# representation of k is a palindrome.
#
# Note: The number 0 is considered binary-palindromic, and its
# representation is "0".
#
# Example 1:
#
# Input: n = 9
#
# Output: 6
#
# Explanation:
#
# The integers k in the range [0, 9] whose binary representations are
# palindromes are:
#
# 0 → "0"
#
# 1 → "1"
#
# 3 → "11"
#
# 5 → "101"
#
# 7 → "111"
#
# 9 → "1001"
#
# All other values in [0, 9] have non-palindromic binary forms. Therefore,
# the count is 6.
#
# Example 2:
#
# Input: n = 0
#
# Output: 1
#
# Explanation:
#
# Since "0" is a palindrome, the count is 1.
#
# Constraints:
#
# 0 <= n <= 10^15
#

# @lc code=start
class Solution:
    def countBinaryPalindromes(self, n: int) -> int:
        """
        Interview explanation:
        Binary palindromes are fixed by their first half (mirrored). Count all
        shorter-length palindromes in closed form, then count same-length ones
        whose half is ≤ n's half, checking the mirrored candidate against n.

        Algorithm:
        - Let s be binary digits of n, L = len(s)//2.
        - Shorter palindromes (incl. 0): (1<<L) - 1, plus the half-prefix count
          n>>L, plus 1 if the palindrome built from n's half is ≤ n.
        - Handles n = 0 → 1.

        Complexity: O(log n) time, O(log n) space for the bit list.
        """
        s = [int(c) for c in bin(n)[2:]]
        half = len(s) // 2
        mirrored = s[: len(s) - half] + s[:half][::-1]
        return ((1 << half) - 1) + (n >> half) + int(mirrored <= s)
# @lc code=end
