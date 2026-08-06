#
# @lc app=leetcode id=2048 lang=python3
#
# [2048] Next Greater Numerically Balanced Number
#
# https://leetcode.com/problems/next-greater-numerically-balanced-number/description/
#
# algorithms
# Medium (63.06%)
# Likes:    563
# Dislikes: 376
# Total Accepted:    107.9K
# Total Submissions: 171.2K
# Testcase Example:  "1"
#
# An integer x is numerically balanced if for every digit d in the number x,
# there are exactly d occurrences of that digit in x.
#
# Given an integer n, return the smallest numerically balanced number strictly
# greater than n.
#
#
#
# Example 1:
#
# Input: n = 1
# Output: 22
# Explanation:
# 22 is numerically balanced since:
# - The digit 2 occurs 2 times.
# It is also the smallest numerically balanced number strictly greater than 1.
#
# Example 2:
#
# Input: n = 1000
# Output: 1333
# Explanation:
# 1333 is numerically balanced since:
# - The digit 1 occurs 1 time.
# - The digit 3 occurs 3 times.
# It is also the smallest numerically balanced number strictly greater than
# 1000.
# Note that 1022 cannot be the answer because 0 appeared more than 0 times.
#
# Example 3:
#
# Input: n = 3000
# Output: 3133
# Explanation:
# 3133 is numerically balanced since:
# - The digit 1 occurs 1 time.
# - The digit 3 occurs 3 times.
# It is also the smallest numerically balanced number strictly greater than
# 3000.
#
#
#
# Constraints:
#
#
# 0 <= n <= 10^6
#

# @lc code=start
class Solution:
    def nextBeautifulNumber(self, n: int) -> int:
        """
        Interview explanation:
        Numerically balanced number: digit d appears exactly d times. Find
        smallest beautiful number strictly greater than n.

        Algorithm:
        - Increment from n+1; check balance via digit counts (n small, <=1e6).

        Complexity: O((U-n) * log U) time with U bound ~1224444; O(1) space.
        """
        def beautiful(x: int) -> bool:
            cnt = [0] * 10
            while x:
                cnt[x % 10] += 1
                x //= 10
            for d in range(10):
                if cnt[d] and cnt[d] != d:
                    return False
            return True

        x = n + 1
        while not beautiful(x):
            x += 1
        return x
# @lc code=end
