#
# @lc app=leetcode id=2513 lang=python3
#
# [2513] Minimize the Maximum of Two Arrays
#
# https://leetcode.com/problems/minimize-the-maximum-of-two-arrays/description/
#
# algorithms
# Medium (32.58%)
# Likes:    528
# Dislikes: 105
# Total Accepted:    17.5K
# Total Submissions: 53.6K
# Testcase Example:  "2\n7\n1\n3"
#
# We have two arrays arr1 and arr2 which are initially empty. You need to add
# positive integers to them such that they satisfy all the following conditions:
#
#
# arr1 contains uniqueCnt1 distinct positive integers, each of which is not
# divisible by divisor1.
#
#
# arr2 contains uniqueCnt2 distinct positive integers, each of which is not
# divisible by divisor2.
#
#
# No integer is present in both arr1 and arr2.
#
# Given divisor1, divisor2, uniqueCnt1, and uniqueCnt2, return the minimum
# possible maximum integer that can be present in either array.
#
#
#
# Example 1:
#
# Input: divisor1 = 2, divisor2 = 7, uniqueCnt1 = 1, uniqueCnt2 = 3
# Output: 4
# Explanation:
# We can distribute the first 4 natural numbers into arr1 and arr2.
# arr1 = [1] and arr2 = [2,3,4].
# We can see that both arrays satisfy all the conditions.
# Since the maximum value is 4, we return it.
#
# Example 2:
#
# Input: divisor1 = 3, divisor2 = 5, uniqueCnt1 = 2, uniqueCnt2 = 1
# Output: 3
# Explanation:
# Here arr1 = [1,2], and arr2 = [3] satisfy all conditions.
# Since the maximum value is 3, we return it.
#
# Example 3:
#
# Input: divisor1 = 2, divisor2 = 4, uniqueCnt1 = 8, uniqueCnt2 = 2
# Output: 15
# Explanation:
# Here, the final possible arrays can be arr1 = [1,3,5,7,9,11,13,15], and arr2 =
# [2,6].
# It can be shown that it is not possible to obtain a lower maximum satisfying
# all conditions.
#
#
#
# Constraints:
#
#
# 2 <= divisor1, divisor2 <= 10^5
#
#
# 1 <= uniqueCnt1, uniqueCnt2 < 10^9
#
#
# 2 <= uniqueCnt1 + uniqueCnt2 <= 10^9
#

# @lc code=start
import math


class Solution:
    def minimizeSet(self, divisor1: int, divisor2: int, uniqueCnt1: int, uniqueCnt2: int) -> int:
        """
        Interview explanation:
        Fill two arrays with distinct positives under divisibility bans; minimize
        the largest number used.

        Algorithm:
        (binary search + LCM)
        - Check mid x: enough nums not div by d1, not div by d2, and not div by
          both (lcm) overall for uniqueCnt1+uniqueCnt2.

        Complexity: O(log(uniqueCnt1+uniqueCnt2)) time, O(1) space.
        """
        lcm = divisor1 * divisor2 // math.gcd(divisor1, divisor2)
        lo, hi = 1, (uniqueCnt1 + uniqueCnt2) * 2

        def ok(x: int) -> bool:
            cnt1 = x - x // divisor1
            cnt2 = x - x // divisor2
            both = x - x // lcm
            return cnt1 >= uniqueCnt1 and cnt2 >= uniqueCnt2 and both >= uniqueCnt1 + uniqueCnt2

        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
