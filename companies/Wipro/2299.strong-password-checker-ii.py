#
# @lc app=leetcode id=2299 lang=python3
#
# [2299] Strong Password Checker II
#
# https://leetcode.com/problems/strong-password-checker-ii/description/
#
# algorithms
# Easy (55.60%)
# Likes:    393
# Dislikes: 41
# Total Accepted:    61K
# Total Submissions: 109.6K
# Testcase Example:  "\"IloveLe3tcode!\""
#
# A password is said to be strong if it satisfies all the following criteria:
#
#
# It has at least 8 characters.
#
#
# It contains at least one lowercase letter.
#
#
# It contains at least one uppercase letter.
#
#
# It contains at least one digit.
#
#
# It contains at least one special character. The special characters are the
# characters in the following string: "!@#$%^&*()-+".
#
#
# It does not contain 2 of the same character in adjacent positions (i.e., "aab"
# violates this condition, but "aba" does not).
#
# Given a string password, return true if it is a strong password. Otherwise,
# return false.
#
#
#
# Example 1:
#
# Input: password = "IloveLe3tcode!"
# Output: true
# Explanation: The password meets all the requirements. Therefore, we return
# true.
#
# Example 2:
#
# Input: password = "Me+You--IsMyDream"
# Output: false
# Explanation: The password does not contain a digit and also contains 2 of the
# same character in adjacent positions. Therefore, we return false.
#
# Example 3:
#
# Input: password = "1aB!"
# Output: false
# Explanation: The password does not meet the length requirement. Therefore, we
# return false.
#
#
#
# Constraints:
#
#
# 1 <= password.length <= 100
#
#
# password consists of letters, digits, and special characters: "!@#$%^&*()-+".
#

# @lc code=start
class Solution:
    def strongPasswordCheckerII(self, password: str) -> bool:
        """
        Interview explanation:
        Strong if len>=8, has lower/upper/digit/special from "!@#$%^&*()-+",
        and no two adjacent equal chars.

        Algorithm:
        - Single scan checking all constraints.

        Complexity: O(n) time, O(1) space.
        """
        if len(password) < 8:
            return False
        special = set("!@#$%^&*()-+")
        has_l = has_u = has_d = has_s = False
        prev = None
        for ch in password:
            if prev is not None and ch == prev:
                return False
            prev = ch
            if ch.islower():
                has_l = True
            elif ch.isupper():
                has_u = True
            elif ch.isdigit():
                has_d = True
            elif ch in special:
                has_s = True
        return has_l and has_u and has_d and has_s
# @lc code=end
