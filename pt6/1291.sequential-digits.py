#
# @lc app=leetcode id=1291 lang=python3
#
# [1291] Sequential Digits
#
# https://leetcode.com/problems/sequential-digits/description/
#
# algorithms
# Medium (65.36%)
# Likes:    2917
# Dislikes: 178
# Total Accepted:    236K
# Total Submissions: 361K
# Testcase Example:  '100\n300'
#
# An integer has sequential digits if and only if each digit in the number is
# one more than the previous digit.
# 
# Return a sorted list of all the integers in the range [low, high] inclusive
# that have sequential digits.
# 
# 
# Example 1:
# Input: low = 100, high = 300
# Output: [123,234]
# Example 2:
# Input: low = 1000, high = 13000
# Output: [1234,2345,3456,4567,5678,6789,12345]
# 
# 
# Constraints:
# 
# 
# 10 <= low <= high <= 10^9
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def sequentialDigits(self, low: int, high: int) -> List[int]:
        digits = "123456789"
        ans = []

        for length in range(2, 10):
            for start in range(0, 10 - length):
                num = int(digits[start:start + length])
                if low <= num <= high:
                    ans.append(num)

        return ans
# @lc code=end

# Explanation
# -----------
# Every sequential-digit number is a contiguous substring of "123456789" with
# length at least 2. Generate those substrings by length and start position,
# convert to integers, and keep the ones in [low, high].
#
# This direct generation is tiny and deterministic. It is better than scanning
# the whole numeric range because there are only 36 possible sequential-digit
# numbers.
#
# Edge cases: no valid numbers in range; low/high near one digit; numbers like
# 789 are generated but 890 is not because digits must be 1 through 9 in order.
#
# Time complexity: O(1) for the fixed digit set.
# Space complexity: O(1) besides the output.
