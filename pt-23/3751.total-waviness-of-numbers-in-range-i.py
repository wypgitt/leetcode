#
# @lc app=leetcode id=3751 lang=python3
#
# [3751] Total Waviness of Numbers in Range I
#
# https://leetcode.com/problems/total-waviness-of-numbers-in-range-i/description/
#
# algorithms
# Medium (87.44%)
# Likes:    287
# Dislikes: 17
# Total Accepted:    146.4K
# Total Submissions: 167.5K
# Testcase Example:  "120\n130"
#
#
# You are given two integers num1 and num2 representing an inclusive range
# [num1, num2].
#
# The waviness of a number is defined as the total count of its peaks and
# valleys:
#
# A digit is a peak if it is strictly greater than both of its immediate
# neighbors.
#
# A digit is a valley if it is strictly less than both of its immediate
# neighbors.
#
# The first and last digits of a number cannot be peaks or valleys.
#
# Any number with fewer than 3 digits has a waviness of 0.
#
# Return the total sum of waviness for all numbers in the range [num1,
# num2].
#
# Example 1:
#
# Input: num1 = 120, num2 = 130
#
# Output: 3
#
# Explanation:
#
# In the range [120, 130]:
#
# 120: middle digit 2 is a peak, waviness = 1.
#
# 121: middle digit 2 is a peak, waviness = 1.
#
# 130: middle digit 3 is a peak, waviness = 1.
#
# All other numbers in the range have a waviness of 0.
#
# Thus, total waviness is 1 + 1 + 1 = 3.
#
# Example 2:
#
# Input: num1 = 198, num2 = 202
#
# Output: 3
#
# Explanation:
#
# In the range [198, 202]:
#
# 198: middle digit 9 is a peak, waviness = 1.
#
# 201: middle digit 0 is a valley, waviness = 1.
#
# 202: middle digit 0 is a valley, waviness = 1.
#
# All other numbers in the range have a waviness of 0.
#
# Thus, total waviness is 1 + 1 + 1 = 3.
#
# Example 3:
#
# Input: num1 = 4848, num2 = 4848
#
# Output: 2
#
# Explanation:
#
# Number 4848: the second digit 8 is a peak, and the third digit 4 is a
# valley, giving a waviness of 2.
#
# Constraints:
#
# 1 <= num1 <= num2 <= 10^5
#

# @lc code=start
class Solution:
    def totalWaviness(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Waviness = count of strict peaks/valleys among interior digits. Sum over
        a small range (num2 <= 1e5) by scanning each number.

        Algorithm:
        - For each x in [num1, num2], convert to digits and count positions i
          with (d[i-1] < d[i] > d[i+1]) or (d[i-1] > d[i] < d[i+1]).

        Complexity: O((num2-num1+1) * D) time, O(D) space, D <= 6.
        """
        def waviness(x: int) -> int:
            s = str(x)
            if len(s) < 3:
                return 0
            ans = 0
            for i in range(1, len(s) - 1):
                a, b, c = s[i - 1], s[i], s[i + 1]
                if (a < b > c) or (a > b < c):
                    ans += 1
            return ans

        return sum(waviness(x) for x in range(num1, num2 + 1))
# @lc code=end
