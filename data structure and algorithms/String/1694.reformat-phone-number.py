#
# @lc app=leetcode id=1694 lang=python3
#
# [1694] Reformat Phone Number
#
# https://leetcode.com/problems/reformat-phone-number/description/
#
# algorithms
# Easy (67.79%)
# Likes:    404
# Dislikes: 206
# Total Accepted:    51.2K
# Total Submissions: 75.5K
# Testcase Example:  "\"1-23-45 6\""
#
# You are given a phone number as a string number. number consists of digits,
# spaces ' ', and/or dashes '-'.
#
# You would like to reformat the phone number in a certain manner. Firstly,
# remove all spaces and dashes. Then, group the digits from left to right into
# blocks of length 3 until there are 4 or fewer digits. The final digits are
# then grouped as follows:
#
# 2 digits: A single block of length 2.
#
# 3 digits: A single block of length 3.
#
# 4 digits: Two blocks of length 2 each.
#
# The blocks are then joined by dashes. Notice that the reformatting process
# should never produce any blocks of length 1 and produce at most two blocks of
# length 2.
#
# Return the phone number after formatting.
#
# Example 1:
#
# Input: number = "1-23-45 6"
# Output: "123-456"
# Explanation: The digits are "123456".
# Step 1: There are more than 4 digits, so group the next 3 digits. The 1st
# block is "123".
# Step 2: There are 3 digits remaining, so put them in a single block of length
# 3. The 2nd block is "456".
# Joining the blocks gives "123-456".
#
# Example 2:
#
# Input: number = "123 4-567"
# Output: "123-45-67"
# Explanation: The digits are "1234567".
# Step 1: There are more than 4 digits, so group the next 3 digits. The 1st
# block is "123".
# Step 2: There are 4 digits left, so split them into two blocks of length 2.
# The blocks are "45" and "67".
# Joining the blocks gives "123-45-67".
#
# Example 3:
#
# Input: number = "123 4-5678"
# Output: "123-456-78"
# Explanation: The digits are "12345678".
# Step 1: The 1st block is "123".
# Step 2: The 2nd block is "456".
# Step 3: There are 2 digits left, so put them in a single block of length 2.
# The 3rd block is "78".
# Joining the blocks gives "123-456-78".
#
# Constraints:
#
# 2 <= number.length <= 100
#
# number consists of digits and the characters '-' and ' '.
#
# There are at least two digits in number.
#

# @lc code=start
class Solution:
    def reformatNumber(self, number: str) -> str:
        """
        Interview explanation:
        Digits only; group into blocks of 3, last block 2 or 3; if last would be
        1 digit, use 2-2 instead of 3-1.

        Algorithm:
        - Extract digits; while len>4: take 3; if len==4: 2-2; else remaining.

        Complexity: O(n) time, O(n) space.
        """
        digits = [c for c in number if c.isdigit()]
        parts = []
        i = 0
        n = len(digits)
        while n - i > 4:
            parts.append("".join(digits[i : i + 3]))
            i += 3
        rem = n - i
        if rem == 4:
            parts.append("".join(digits[i : i + 2]))
            parts.append("".join(digits[i + 2 : i + 4]))
        else:
            parts.append("".join(digits[i:]))
        return "-".join(parts)
# @lc code=end
