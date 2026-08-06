#
# @lc app=leetcode id=273 lang=python3
#
# [273] Integer to English Words
#
# https://leetcode.com/problems/integer-to-english-words/description/
#
# algorithms
# Hard (35.14%)
# Likes:    3877
# Dislikes: 6847
# Total Accepted:    592K
# Total Submissions: 1.7M
# Testcase Example:  "123"
#
# Convert a non-negative integer num to its English words representation.
#
# Example 1:
#
# Input: num = 123
# Output: "One Hundred Twenty Three"
#
# Example 2:
#
# Input: num = 12345
# Output: "Twelve Thousand Three Hundred Forty Five"
#
# Example 3:
#
# Input: num = 1234567
# Output: "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty
# Seven"
#
# Constraints:
#
# 0 <= num <= 2^31 - 1
#

# @lc code=start
class Solution:
    def numberToWords(self, num: int) -> str:
        """
        Interview explanation:
        Convert by 3-digit chunks (thousands / millions / billions). Each chunk
        of at most 999 is spoken with below-20, tens, and hundreds words, then
        a scale suffix is appended.

        Algorithm:
        - Handle 0 specially → "Zero".
        - Process least-significant chunk first; append scale words.
        - Helper converts 1..999 into English without a leading scale.

        Complexity: O(1) time/space (fixed digit count for 32-bit ints).
        """
        if num == 0:
            return "Zero"

        below_20 = [
            "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
            "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
            "Sixteen", "Seventeen", "Eighteen", "Nineteen",
        ]
        tens = [
            "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
            "Eighty", "Ninety",
        ]
        thousands = ["", "Thousand", "Million", "Billion"]

        def helper(n: int) -> str:
            if n == 0:
                return ""
            if n < 20:
                return below_20[n] + " "
            if n < 100:
                return tens[n // 10] + " " + helper(n % 10)
            return below_20[n // 100] + " Hundred " + helper(n % 100)

        res = ""
        i = 0
        while num:
            if num % 1000:
                res = helper(num % 1000) + thousands[i] + (" " if thousands[i] else "") + res
            num //= 1000
            i += 1
        return res.strip()
# @lc code=end

