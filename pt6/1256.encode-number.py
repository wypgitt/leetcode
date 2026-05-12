#
# @lc app=leetcode id=1256 lang=python3
#
# [1256] Encode Number
#
# https://leetcode.com/problems/encode-number/description/
#
# algorithms
# Medium (70.31%)
# Likes:    82
# Dislikes: 258
# Total Accepted:    8.7K
# Total Submissions: 12.4K
# Testcase Example:  '23'
#
# Given a non-negative integer num, Return its encoding string.
# 
# The encoding is done by converting the integer to a string using a secret
# function that you should deduce from the following table:
# 
# 
# 
# 
# Example 1:
# 
# 
# Input: num = 23
# Output: "1000"
# 
# 
# Example 2:
# 
# 
# Input: num = 107
# Output: "101100"
# 
# 
# 
# Constraints:
# 
# 
# 0 <= num <= 10^9
# 
#

# @lc code=start
class Solution:
    def encode(self, num: int) -> str:
        return bin(num + 1)[3:]
# @lc code=end

# Explanation
# -----------
# The encoding sequence is grouped by binary length:
# 0 -> "", 1 -> "0", 2 -> "1", 3 -> "00", and so on. If we write num + 1 in
# binary and remove the leading "1", we get exactly the code for num.
#
# Python's bin(num + 1) returns a string like "0b11000"; slicing from index 3
# removes "0b1" and keeps the encoded suffix.
#
# Edge cases: num = 0 gives bin(1) = "0b1", so the slice is the empty string.
#
# Time complexity: O(log num) to build the binary representation.
# Space complexity: O(log num) for the returned string.
