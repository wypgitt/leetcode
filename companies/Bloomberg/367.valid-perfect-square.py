#
# @lc app=leetcode id=367 lang=python3
#
# [367] Valid Perfect Square
#
# https://leetcode.com/problems/valid-perfect-square/description/
#
# algorithms
# Easy (45.15%)
# Likes:    4722
# Dislikes: 339
# Total Accepted:    974K
# Total Submissions: 2.2M
# Testcase Example:  "16"
#
# Given a positive integer num, return true if num is a perfect square or false
# otherwise.
#
# A perfect square is an integer that is the square of an integer. In other
# words, it is the product of some integer with itself.
#
# You must not use any built-in library function, such as sqrt.
#
# Example 1:
#
# Input: num = 16
# Output: true
# Explanation: We return true because 4 * 4 = 16 and 4 is an integer.
#
# Example 2:
#
# Input: num = 14
# Output: false
# Explanation: We return false because 3.742 * 3.742 = 14 and 3.742 is not an
# integer.
#
# Constraints:
#
# 1 <= num <= 2^31 - 1
#

# @lc code=start
class Solution:
    def isPerfectSquare(self, num: int) -> bool:
        """
        Interview explanation:
        Binary search for integer r with r*r == num in [1, num].

        Algorithm:
        - lo, hi = 1, num; while lo <= hi: mid; compare mid*mid to num.

        Complexity: O(log num) time, O(1) space.
        """
        lo, hi = 1, num
        while lo <= hi:
            mid = (lo + hi) // 2
            sq = mid * mid
            if sq == num:
                return True
            if sq < num:
                lo = mid + 1
            else:
                hi = mid - 1
        return False
# @lc code=end
