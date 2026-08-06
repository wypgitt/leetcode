#
# @lc app=leetcode id=556 lang=python3
#
# [556] Next Greater Element III
#
# https://leetcode.com/problems/next-greater-element-iii/description/
#
# algorithms
# Medium (35.51%)
# Likes:    3973
# Dislikes: 500
# Total Accepted:    216K
# Total Submissions: 609K
# Testcase Example:  "12"
#
# Given a positive integer n, find the smallest integer which has exactly the
# same digits existing in the integer n and is greater in value than n. If no
# such positive integer exists, return -1.
#
# Note that the returned integer should fit in 32-bit integer, if there is a
# valid answer but it does not fit in 32-bit integer, return -1.
#
# Example 1:
#
# Input: n = 12
# Output: 21
#
# Example 2:
#
# Input: n = 21
# Output: -1
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#

# @lc code=start
class Solution:
    def nextGreaterElement(self, n: int) -> int:
        """
        Interview explanation:
        Next permutation of the digits: find rightmost ascent, swap with next
        larger digit to the right, reverse the suffix. If no greater
        permutation or result > 2^31-1, return -1.

        Algorithm:
        - Digits list; classic next_permutation; join and bounds-check.

        Complexity: O(d) time for d digits, O(d) space.
        """
        digits = list(str(n))
        i = len(digits) - 2
        while i >= 0 and digits[i] >= digits[i + 1]:
            i -= 1
        if i < 0:
            return -1
        j = len(digits) - 1
        while digits[j] <= digits[i]:
            j -= 1
        digits[i], digits[j] = digits[j], digits[i]
        digits[i + 1 :] = reversed(digits[i + 1 :])
        ans = int("".join(digits))
        return ans if ans <= 2**31 - 1 else -1
# @lc code=end

