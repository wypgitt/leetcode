#
# @lc app=leetcode id=3726 lang=python3
#
# [3726] Remove Zeros in Decimal Representation
#
# https://leetcode.com/problems/remove-zeros-in-decimal-representation/description/
#
# algorithms
# Easy (76.60%)
# Likes:    52
# Dislikes: 2
# Total Accepted:    54.8K
# Total Submissions: 71.6K
# Testcase Example:  "1020030"
#
#
# You are given a positive integer n.
#
# Return the integer obtained by removing all zeros from the decimal
# representation of n.
#
# Example 1:
#
# Input: n = 1020030
#
# Output: 123
#
# Explanation:
#
# After removing all zeros from 1020030, we get 123.
#
# Example 2:
#
# Input: n = 1
#
# Output: 1
#
# Explanation:
#
# 1 has no zero in its decimal representation. Therefore, the answer is 1.
#
# Constraints:
#
# 1 <= n <= 10^15
#

# @lc code=start
class Solution:
    def removeZeros(self, n: int) -> int:
        """
        Interview explanation:
        Drop every digit 0 from the decimal representation and parse back.

        Algorithm:
        - Filter non-zero characters from str(n); int(...) the result.

        Complexity: O(log n) time and space.
        """
        return int("".join(ch for ch in str(n) if ch != "0"))

    def removeZeros_math(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: peel digits arithmetically, skipping zeros.

        Algorithm:
        - Repeatedly take n % 10; if non-zero, append to answer via place value.

        Complexity: O(log n) time, O(1) space.
        """
        ans, place = 0, 1
        while n:
            d = n % 10
            if d:
                ans += d * place
                place *= 10
            n //= 10
        return ans
# @lc code=end

