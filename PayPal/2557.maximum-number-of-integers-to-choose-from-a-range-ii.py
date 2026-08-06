#
# @lc app=leetcode id=2557 lang=python3
#
# [2557] Maximum Number of Integers to Choose From a Range II
#
# https://leetcode.com/problems/maximum-number-of-integers-to-choose-from-a-range-ii/description/
#
# algorithms
# Medium (34.81%)
# Likes:    42
# Dislikes: 26
# Total Accepted:    3K
# Total Submissions: 8.6K
# Testcase Example:  "[1,4,6]\n6\n4"
#
#
# You are given an integer array banned and two integers n and maxSum. You
# are choosing some number of integers following the below rules:
#
# The chosen integers have to be in the range [1, n].
#
# Each integer can be chosen at most once.
#
# The chosen integers should not be in the array banned.
#
# The sum of the chosen integers should not exceed maxSum.
#
# Return the maximum number of integers you can choose following the
# mentioned rules.
#
# Example 1:
#
# Input: banned = [1,4,6], n = 6, maxSum = 4
# Output: 1
# Explanation: You can choose the integer 3.
# 3 is in the range [1, 6], and do not appear in banned. The sum of the
# chosen integers is 3, which does not exceed maxSum.
#
# Example 2:
#
# Input: banned = [4,3,5,6], n = 7, maxSum = 18
# Output: 3
# Explanation: You can choose the integers 1, 2, and 7.
# All these integers are in the range [1, 7], all do not appear in banned,
# and their sum is 10, which does not exceed maxSum.
#
# Constraints:
#
# 1 <= banned.length <= 10^5
#
# 1 <= banned[i] <= n <= 10^9
#
# 1 <= maxSum <= 10^15
#
# @lc code=start
from typing import List


class Solution:
    def maxCount(self, banned: List[int], n: int, maxSum: int) -> int:
        """
        Interview explanation:
        Same as Range I but n up to 1e9: greedily take smallest non-banned integers
        using consecutive ranges between sorted banned values, with binary search on count.

        Algorithm:
        - Sort unique banned in [1,n]; walk gaps [prev+1, x-1].
        - For a gap of consecutive integers starting at L with length len, take as many
          as sum allows via binary search / closed form for triangular sums.
        - Also consider final gap after last banned to n.

        Complexity: O(b log b + b log n) time, O(b) space.
        """
        ban = sorted({x for x in banned if 1 <= x <= n})
        ans = 0
        total = 0
        prev = 0

        def take_from(L: int, R: int) -> None:
            nonlocal ans, total
            if L > R:
                return
            # max t such that sum of L..(L+t-1) = t*L + t*(t-1)/2 <= maxSum-total
            lo, hi = 0, R - L + 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                s = mid * L + mid * (mid - 1) // 2
                if total + s <= maxSum:
                    lo = mid
                else:
                    hi = mid - 1
            if lo:
                total += lo * L + lo * (lo - 1) // 2
                ans += lo

        for x in ban:
            take_from(prev + 1, x - 1)
            if total >= maxSum:
                return ans
            prev = x
        take_from(prev + 1, n)
        return ans
# @lc code=end
