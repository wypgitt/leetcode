#
# @lc app=leetcode id=2117 lang=python3
#
# [2117] Abbreviating the Product of a Range
#
# https://leetcode.com/problems/abbreviating-the-product-of-a-range/description/
#
# algorithms
# Hard (24.59%)
# Likes:    92
# Dislikes: 162
# Total Accepted:    5K
# Total Submissions: 20.3K
# Testcase Example:  "1\n4"
#
# You are given two positive integers left and right with left <= right.
# Calculate the product of all integers in the inclusive range [left, right].
#
# Since the product may be very large, you will abbreviate it following these
# steps:
#
#
# Count all trailing zeros in the product and remove them. Let us denote this
# count as C.
#
#
#
#
# For example, there are 3 trailing zeros in 1000, and there are 0 trailing
# zeros in 546.
#
#
#
#
#
#
# Denote the remaining number of digits in the product as d. If d > 10, then
# express the product as <pre>...<suf> where <pre> denotes the first 5 digits of
# the product, and <suf> denotes the last 5 digits of the product after removing
# all trailing zeros. If d <= 10, we keep it unchanged.
#
#
#
# For example, we express 1234567654321 as 12345...54321, but 1234567 is
# represented as 1234567.
#
#
#
#
#
#
# Finally, represent the product as a string "<pre>...<suf>eC".
#
#
#
# For example, 12345678987600000 will be represented as "12345...89876e5".
#
#
#
#
#
# Return a string denoting the abbreviated product of all integers in the
# inclusive range [left, right].
#
#
#
# Example 1:
#
# Input: left = 1, right = 4
# Output: "24e0"
# Explanation: The product is 1 × 2 × 3 × 4 = 24.
# There are no trailing zeros, so 24 remains the same. The abbreviation will end
# with "e0".
# Since the number of digits is 2, which is less than 10, we do not have to
# abbreviate it further.
# Thus, the final representation is "24e0".
#
# Example 2:
#
# Input: left = 2, right = 11
# Output: "399168e2"
# Explanation: The product is 39916800.
# There are 2 trailing zeros, which we remove to get 399168. The abbreviation
# will end with "e2".
# The number of digits after removing the trailing zeros is 6, so we do not
# abbreviate it further.
# Hence, the abbreviated product is "399168e2".
#
# Example 3:
#
# Input: left = 371, right = 375
# Output: "7219856259e3"
# Explanation: The product is 7219856259000.
#
#
#
# Constraints:
#
#
# 1 <= left <= right <= 10^4
#



# @lc code=start
class Solution:
    def abbreviateProduct(self, left: int, right: int) -> str:
        """
        Interview explanation:
        Product of [left, right]. Return full "digits e zeros" if the non-trailing-
        zero part has ≤10 digits; else "pre...suf e zeros" with 5 leading and
        5 trailing non-zero digits.

        Algorithm:
        - Mantissa prod in [0.1,1) via repeated *=num and /=10, counting digits.
        - Integer suffix: multiply, strip trailing zeros (count them), mod 10^10.
        - If nonzero digits ≤10: reconstruct from mantissa; else format abbrev.

        Complexity: O(right-left+1) time, O(1) space.
        """
        prod = 1.0
        suf = 1
        count_digits = 0
        count_zeros = 0
        max_suf = 10**10

        for num in range(left, right + 1):
            prod *= num
            while prod >= 1.0:
                prod /= 10.0
                count_digits += 1
            suf *= num
            while suf % 10 == 0:
                suf //= 10
                count_zeros += 1
            if suf > max_suf:
                suf %= max_suf

        nonzero_digits = count_digits - count_zeros
        if nonzero_digits <= 10:
            tens = 10 ** nonzero_digits
            return str(int(prod * tens + 0.5)) + 'e' + str(count_zeros)

        pre = str(int(prod * 10**5 + 1e-9))
        # ensure exactly 5 leading digits despite float noise
        if len(pre) > 5:
            pre = pre[:5]
        while len(pre) < 5:
            pre += '0'
        suf_str = f"{suf % 100000:05d}"
        return pre + '...' + suf_str + 'e' + str(count_zeros)
# @lc code=end


