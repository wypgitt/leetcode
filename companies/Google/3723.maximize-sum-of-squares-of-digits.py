#
# @lc app=leetcode id=3723 lang=python3
#
# [3723] Maximize Sum of Squares of Digits
#
# https://leetcode.com/problems/maximize-sum-of-squares-of-digits/description/
#
# algorithms
# Medium (59.17%)
# Likes:    65
# Dislikes: 2
# Total Accepted:    24.1K
# Total Submissions: 40.8K
# Testcase Example:  "2\n3"
#
#
# You are given two positive integers num and sum.
#
# A positive integer n is good if it satisfies both of the following:
#
# The number of digits in n is exactly num.
#
# The sum of digits in n is exactly sum.
#
# The score of a good integer n is the sum of the squares of digits in n.
#
# Return a string denoting the good integer n that achieves the maximum
# score. If there are multiple possible integers, return the maximum
# ​​​​​​​one. If no such integer exists, return an empty string.
#
# Example 1:
#
# Input: num = 2, sum = 3
#
# Output: "30"
#
# Explanation:
#
# There are 3 good integers: 12, 21, and 30.
#
# The score of 12 is 1^2 + 2^2 = 5.
#
# The score of 21 is 2^2 + 1^2 = 5.
#
# The score of 30 is 3^2 + 0^2 = 9.
#
# The maximum score is 9, which is achieved by the good integer 30.
# Therefore, the answer is "30".
#
# Example 2:
#
# Input: num = 2, sum = 17
#
# Output: "98"
#
# Explanation:
#
# There are 2 good integers: 89 and 98.
#
# The score of 89 is 8^2 + 9^2 = 145.
#
# The score of 98 is 9^2 + 8^2 = 145.
#
# The maximum score is 145. The maximum good integer that achieves this
# score is 98. Therefore, the answer is "98".
#
# Example 3:
#
# Input: num = 1, sum = 10
#
# Output: ""
#
# Explanation:
#
# There are no integers that have exactly 1 digit and whose digits sum to
# 10. Therefore, the answer is "".
#
# Constraints:
#
# 1 <= num <= 2 * 10^5
#
# 1 <= sum <= 2 * 10^6
#

# @lc code=start
class Solution:
    def maxSumOfSquares(self, num: int, sum: int) -> str:
        """
        Interview explanation:
        Score is sum of digit squares, so prefer digit 9 (largest square).
        Among max-score numbers, the largest numeral puts large digits left.

        Algorithm:
        - Impossible if sum > 9 * num.
        - Emit as many 9s as possible, then one remainder digit, then zeros.

        Complexity: O(num) time and space for the answer string.
        """
        if num * 9 < sum:
            return ""
        nines, rem = divmod(sum, 9)
        ans = "9" * nines
        if rem:
            ans += str(rem)
        ans += "0" * (num - len(ans))
        return ans

    def maxSumOfSquares_list(self, num: int, sum: int) -> str:
        """
        Interview explanation:
        Alternate: fill a digit array from the left greedily.

        Algorithm:
        - For each position, take min(9, remaining sum); fail if leftover > 0.

        Complexity: O(num) time and space.
        """
        if num * 9 < sum:
            return ""
        digits = []
        rem = sum
        for _ in range(num):
            d = min(9, rem)
            digits.append(str(d))
            rem -= d
        return "".join(digits) if rem == 0 else ""
# @lc code=end

