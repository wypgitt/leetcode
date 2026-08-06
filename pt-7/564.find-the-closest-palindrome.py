#
# @lc app=leetcode id=564 lang=python3
#
# [564] Find the Closest Palindrome
#
# https://leetcode.com/problems/find-the-closest-palindrome/description/
#
# algorithms
# Hard (32.05%)
# Likes:    1336
# Dislikes: 1742
# Total Accepted:    141K
# Total Submissions: 440K
# Testcase Example:  "\"123\""
#
# Given a string n representing an integer, return the closest integer (not
# including itself), which is a palindrome. If there is a tie, return the
# smaller one.
#
# The closest is defined as the absolute difference minimized between two
# integers.
#
# Example 1:
#
# Input: n = "123"
# Output: "121"
#
# Example 2:
#
# Input: n = "1"
# Output: "0"
# Explanation: 0 and 2 are the closest palindromes but we return the smallest
# which is 0.
#
# Constraints:
#
# 1 <= n.length <= 18
#
# n consists of only digits.
#
# n does not have leading zeros.
#
# n is representing an integer in the range [1, 10^18 - 1].
#


# @lc code=start
class Solution:
    def nearestPalindromic(self, n: str) -> str:
        """
        Interview explanation:
        Closest palindrome is among a small candidate set built from mirroring
        the left half (and half±1), plus edge cases with different digit lengths
        (999...9 and 100...001). Pick the nearest by absolute difference,
        breaking ties toward the smaller value.

        Algorithm:
        - Let half = first ceil(len/2) digits as integer.
        - Candidates from mirroring half-1, half, half+1.
        - Also add 10^d - 1 and 10^d + 1 for length transitions.
        - Exclude n itself; choose min by (|diff|, value).

        Complexity: O(d) time for d = len(n), O(d) space for candidates/strings.
        """
        length = len(n)
        num = int(n)
        candidates = set()
        candidates.add(10 ** (length - 1) - 1)  # 999...9 (shorter)
        candidates.add(10 ** length + 1)        # 100...001 (longer)

        prefix_len = (length + 1) // 2
        prefix = int(n[:prefix_len])
        for p in (prefix - 1, prefix, prefix + 1):
            s = str(p)
            if length % 2 == 0:
                pal = s + s[::-1]
            else:
                pal = s + s[-2::-1]
            candidates.add(int(pal))

        candidates.discard(num)
        best = min(candidates, key=lambda x: (abs(x - num), x))
        return str(best)
# @lc code=end

