#
# @lc app=leetcode id=1482 lang=python3
#
# [1482] Minimum Number of Days to Make m Bouquets
#
# https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/description/
#
# algorithms
# Medium (56.99%)
# Likes:    5891
# Dislikes: 328
# Total Accepted:    573K
# Total Submissions: 1.0M
# Testcase Example:  "[1,10,3,10,2]"
#
# You are given an integer array bloomDay, an integer m and an integer k.
#
# You want to make m bouquets. To make a bouquet, you need to use k adjacent
# flowers from the garden.
#
# The garden consists of n flowers, the i^th flower will bloom in the
# bloomDay[i] and then can be used in exactly one bouquet.
#
# Return the minimum number of days you need to wait to be able to make m
# bouquets from the garden. If it is impossible to make m bouquets return -1.
#
# Example 1:
#
# Input: bloomDay = [1,10,3,10,2], m = 3, k = 1
# Output: 3
# Explanation: Let us see what happened in the first three days. x means flower
# bloomed and _ means flower did not bloom in the garden.
# We need 3 bouquets each should contain 1 flower.
# After day 1: [x, _, _, _, _] // we can only make one bouquet.
# After day 2: [x, _, _, _, x] // we can only make two bouquets.
# After day 3: [x, _, x, _, x] // we can make 3 bouquets. The answer is 3.
#
# Example 2:
#
# Input: bloomDay = [1,10,3,10,2], m = 3, k = 2
# Output: -1
# Explanation: We need 3 bouquets each has 2 flowers, that means we need 6
# flowers. We only have 5 flowers so it is impossible to get the needed
# bouquets and we return -1.
#
# Example 3:
#
# Input: bloomDay = [7,7,7,7,12,7,7], m = 2, k = 3
# Output: 12
# Explanation: We need 2 bouquets each should have 3 flowers.
# Here is the garden after the 7 and 12 days:
# After day 7: [x, x, x, x, _, x, x]
# We can make one bouquet of the first three flowers that bloomed. We cannot
# make another bouquet from the last three flowers that bloomed because they
# are not adjacent.
# After day 12: [x, x, x, x, x, x, x]
# It is obvious that we can make two bouquets in different ways.
#
# Constraints:
#
# bloomDay.length == n
#
# 1 <= n <= 10^5
#
# 1 <= bloomDay[i] <= 10^9
#
# 1 <= m <= 10^6
#
# 1 <= k <= n
#

# @lc code=start
from typing import List


class Solution:
    def minDays(self, bloomDay: List[int], m: int, k: int) -> int:
        """
        Interview explanation:
        Need m bouquets of k adjacent flowers; flower i blooms on bloomDay[i].
        Binary search the day; feasibility: greedily count groups of k adjacent
        bloomed flowers.

        Algorithm:
        - If m*k > n return -1; lo=min days, hi=max; check(mid) counts bouquets.

        Complexity: O(n log D) time, O(1) space.
        """
        n = len(bloomDay)
        if m * k > n:
            return -1

        def ok(day):
            bouquets = flowers = 0
            for d in bloomDay:
                if d <= day:
                    flowers += 1
                    if flowers == k:
                        bouquets += 1
                        flowers = 0
                else:
                    flowers = 0
            return bouquets >= m

        lo, hi = min(bloomDay), max(bloomDay)
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def minDays_linear(self, bloomDay: List[int], m: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: try each distinct bloom day in sorted order (same feasibility
        check) — still correct but worse than binary search when D is large.

        Algorithm:
        - If m*k>n return -1; for day in sorted(set(bloomDay)): if ok return day.

        Complexity: O(n * U) time for U unique days, O(U) space.
        """
        n = len(bloomDay)
        if m * k > n:
            return -1

        def ok(day):
            bouquets = flowers = 0
            for d in bloomDay:
                if d <= day:
                    flowers += 1
                    if flowers == k:
                        bouquets += 1
                        flowers = 0
                else:
                    flowers = 0
            return bouquets >= m

        for day in sorted(set(bloomDay)):
            if ok(day):
                return day
        return -1

# @lc code=end
