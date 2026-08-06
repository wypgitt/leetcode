#
# @lc app=leetcode id=2843 lang=python3
#
# [2843]   Count Symmetric Integers
#
# https://leetcode.com/problems/count-symmetric-integers/description/
#
# algorithms
# Easy (83.14%)
# Likes:    661
# Dislikes: 65
# Total Accepted:    203.6K
# Total Submissions: 244.9K
# Testcase Example:  "1\n100"
#
#
# You are given two positive integers low and high.
#
# An integer x consisting of 2 * n digits is symmetric if the sum of the
# first n digits of x is equal to the sum of the last n digits of x.
# Numbers with an odd number of digits are never symmetric.
#
# Return the number of symmetric integers in the range [low, high].
#
# Example 1:
#
# Input: low = 1, high = 100
# Output: 9
# Explanation: There are 9 symmetric integers between 1 and 100: 11, 22,
# 33, 44, 55, 66, 77, 88, and 99.
#
# Example 2:
#
# Input: low = 1200, high = 1230
# Output: 4
# Explanation: There are 4 symmetric integers between 1200 and 1230: 1203,
# 1212, 1221, and 1230.
#
# Constraints:
#
# 1 <= low <= high <= 10^4
#

# @lc code=start
class Solution:
    def countSymmetricIntegers(self, low: int, high: int) -> int:
        """
        Interview explanation:
        Count numbers in [low, high] with even digit length whose first half digit
        sum equals the second half. Constraints high <= 1e4 => brute force.

        Algorithm:
        - For each x, stringify; skip odd length; compare half digit sums.

        Complexity: O((high-low+1) * log high) time, O(1) space.
        """
        ans = 0
        for x in range(low, high + 1):
            s = str(x)
            n = len(s)
            if n & 1:
                continue
            h = n // 2
            if sum(map(int, s[:h])) == sum(map(int, s[h:])):
                ans += 1
        return ans
# @lc code=end
