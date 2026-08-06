#
# @lc app=leetcode id=3753 lang=python3
#
# [3753] Total Waviness of Numbers in Range II
#
# https://leetcode.com/problems/total-waviness-of-numbers-in-range-ii/description/
#
# algorithms
# Hard (56.64%)
# Likes:    247
# Dislikes: 24
# Total Accepted:    68.2K
# Total Submissions: 120.4K
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
# 1 <= num1 <= num2 <= 10^15​​​​​​​
#

# @lc code=start
class Solution:
    def totalWaviness(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Same waviness as Range I, but num2 <= 1e15 — digit DP summing peak/valley
        contributions over [1, x], then f(num2) - f(num1 - 1).

        Algorithm:
        - dfs returns (count, waviness_sum) for suffixes.
        - State: (pos, prev, prev2, still_leading_zero, tight).
        - When placing digit d with a started number and prev2 known, if prev is
          a peak/valley vs (prev2, d), add the number of completions to waviness.

        Complexity: O(log x * states) time/space.
        """
        def count_up_to(x: int) -> int:
            if x < 0:
                return 0
            s = str(x)
            memo = {}

            def dp(i: int, prev: int, prev2: int, zero: bool, tight: bool):
                if i == len(s):
                    return 1, 0
                key = (i, prev, prev2, zero, tight)
                if key in memo:
                    return memo[key]
                cnt = w = 0
                mx = int(s[i]) if tight else 9
                for d in range(mx + 1):
                    new_tight = tight and d == int(s[i])
                    new_zero = zero and d == 0
                    new_prev2 = prev
                    new_prev = -1 if new_zero else d
                    new_cnt, nw = dp(i + 1, new_prev, new_prev2, new_zero, new_tight)
                    cnt += new_cnt
                    if not zero and prev2 != -1 and (
                        (prev2 < prev > d) or (prev2 > prev < d)
                    ):
                        w += new_cnt
                    w += nw
                memo[key] = (cnt, w)
                return cnt, w

            return dp(0, -1, -1, True, True)[1]

        return count_up_to(num2) - count_up_to(num1 - 1)
# @lc code=end
