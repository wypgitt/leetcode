#
# @lc app=leetcode id=2457 lang=python3
#
# [2457] Minimum Addition to Make Integer Beautiful
#
# https://leetcode.com/problems/minimum-addition-to-make-integer-beautiful/description/
#
# algorithms
# Medium (38.89%)
# Likes:    550
# Dislikes: 26
# Total Accepted:    26.2K
# Total Submissions: 67.4K
# Testcase Example:  "16\n6"
#
# You are given two positive integers n and target.
#
# An integer is considered beautiful if the sum of its digits is less than or
# equal to target.
#
# Return the minimum non-negative integer x such that n + x is beautiful. The
# input will be generated such that it is always possible to make n beautiful.
#
#
#
# Example 1:
#
# Input: n = 16, target = 6
# Output: 4
# Explanation: Initially n is 16 and its digit sum is 1 + 6 = 7. After adding 4,
# n becomes 20 and digit sum becomes 2 + 0 = 2. It can be shown that we can not
# make n beautiful with adding non-negative integer less than 4.
#
# Example 2:
#
# Input: n = 467, target = 6
# Output: 33
# Explanation: Initially n is 467 and its digit sum is 4 + 6 + 7 = 17. After
# adding 33, n becomes 500 and digit sum becomes 5 + 0 + 0 = 5. It can be shown
# that we can not make n beautiful with adding non-negative integer less than
# 33.
#
# Example 3:
#
# Input: n = 1, target = 1
# Output: 0
# Explanation: Initially n is 1 and its digit sum is 1, which is already smaller
# than or equal to target.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^12
#
#
# 1 <= target <= 150
#
#
# The input will be generated such that it is always possible to make n
# beautiful.
#

# @lc code=start
class Solution:
    def makeIntegerBeautiful(self, n: int, target: int) -> int:
        """
        Interview explanation:
        Add the smallest non-negative x so digit sum of n+x <= target.

        Algorithm:
        - While digit sum > target, round up the lowest non-zero suffix to next
          power of 10 (carry), accumulate the added amount.

        Complexity: O(log n) time, O(1) space.
        """
        def digit_sum(x: int) -> int:
            return sum(int(d) for d in str(x))

        ans = 0
        p = 1
        while digit_sum(n) > target:
            d = (n // p) % 10
            add = (10 - d) * p
            n += add
            ans += add
            p *= 10
        return ans
# @lc code=end

