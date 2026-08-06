#
# @lc app=leetcode id=3606 lang=python3
#
# [3606] Coupon Code Validator
#
# https://leetcode.com/problems/coupon-code-validator/description/
#
# algorithms
# Easy (64.73%)
# Likes:    340
# Dislikes: 108
# Total Accepted:    128.1K
# Total Submissions: 198K
# Testcase Example:  "[\"SAVE20\",\"\",\"PHARMA5\",\"SAVE@20\"]\n[\"restaurant\",\"grocery\",\"pharmacy\",\"restaurant\"]\n[true,true,true,true]"
#
#
# You are given three arrays of length n that describe the properties of n
# coupons: code, businessLine, and isActive. The i^th coupon has:
#
# code[i]: a string representing the coupon identifier.
#
# businessLine[i]: a string denoting the business category of the coupon.
#
# isActive[i]: a boolean indicating whether the coupon is currently
# active.
#
# A coupon is considered valid if all of the following conditions hold:
#
# code[i] is non-empty and consists only of alphanumeric characters (a-z,
# A-Z, 0-9) and underscores (_).
#
# businessLine[i] is one of the following four categories: "electronics",
# "grocery", "pharmacy", "restaurant".
#
# isActive[i] is true.
#
# Return an array of the codes of all valid coupons, sorted first by their
# businessLine in the order: "electronics", "grocery", "pharmacy",
# "restaurant", and then by code in lexicographical (ascending) order
# within each category.
#
# Example 1:
#
# Input: code = ["SAVE20","","PHARMA5","SAVE@20"], businessLine =
# ["restaurant","grocery","pharmacy","restaurant"], isActive =
# [true,true,true,true]
#
# Output: ["PHARMA5","SAVE20"]
#
# Explanation:
#
# First coupon is valid.
#
# Second coupon has empty code (invalid).
#
# Third coupon is valid.
#
# Fourth coupon has special character @ (invalid).
#
# Example 2:
#
# Input: code = ["GROCERY15","ELECTRONICS_50","DISCOUNT10"], businessLine
# = ["grocery","electronics","invalid"], isActive = [false,true,true]
#
# Output: ["ELECTRONICS_50"]
#
# Explanation:
#
# First coupon is inactive (invalid).
#
# Second coupon is valid.
#
# Third coupon has invalid business line (invalid).
#
# Constraints:
#
# n == code.length == businessLine.length == isActive.length
#
# 1 <= n <= 100
#
# 0 <= code[i].length, businessLine[i].length <= 100
#
# code[i] and businessLine[i] consist of printable ASCII characters.
#
# isActive[i] is either true or false.
#

# @lc code=start

from typing import List


class Solution:
    def validateCoupons(
        self, code: List[str], businessLine: List[str], isActive: List[bool]
    ) -> List[str]:
        """
        Interview explanation:
        Keep active coupons with valid alphanumeric/_ codes and one of four
        business lines; sort by category order then code.

        Algorithm:
        - Filter valid triples; sort by (category rank, code).

        Complexity: O(n log n) time, O(n) space.
        """
        order = {"electronics": 0, "grocery": 1, "pharmacy": 2, "restaurant": 3}
        valid = []
        for c, b, active in zip(code, businessLine, isActive):
            if not active or b not in order or not c:
                continue
            if all(ch.isalnum() or ch == "_" for ch in c):
                valid.append((order[b], c))
        valid.sort()
        return [c for _, c in valid]
# @lc code=end
