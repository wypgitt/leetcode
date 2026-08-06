#
# @lc app=leetcode id=2398 lang=python3
#
# [2398] Maximum Number of Robots Within Budget
#
# https://leetcode.com/problems/maximum-number-of-robots-within-budget/description/
#
# algorithms
# Hard (38.92%)
# Likes:    924
# Dislikes: 22
# Total Accepted:    37.5K
# Total Submissions: 96.5K
# Testcase Example:  "[3,6,1,3,4]\n[2,1,3,4,5]\n25"
#
# You have n robots. You are given two 0-indexed integer arrays, chargeTimes and
# runningCosts, both of length n. The i^th robot costs chargeTimes[i] units to
# charge and costs runningCosts[i] units to run. You are also given an integer
# budget.
#
# The total cost of running k chosen robots is equal to max(chargeTimes) + k *
# sum(runningCosts), where max(chargeTimes) is the largest charge cost among the
# k robots and sum(runningCosts) is the sum of running costs among the k robots.
#
# Return the maximum number of consecutive robots you can run such that the
# total cost does not exceed budget.
#
#
#
# Example 1:
#
# Input: chargeTimes = [3,6,1,3,4], runningCosts = [2,1,3,4,5], budget = 25
# Output: 3
# Explanation:
# It is possible to run all individual and consecutive pairs of robots within
# budget.
# To obtain answer 3, consider the first 3 robots. The total cost will be
# max(3,6,1) + 3 * sum(2,1,3) = 6 + 3 * 6 = 24 which is less than 25.
# It can be shown that it is not possible to run more than 3 consecutive robots
# within budget, so we return 3.
#
# Example 2:
#
# Input: chargeTimes = [11,12,19], runningCosts = [10,8,7], budget = 19
# Output: 0
# Explanation: No robot can be run that does not exceed the budget, so we return
# 0.
#
#
#
# Constraints:
#
#
# chargeTimes.length == runningCosts.length == n
#
#
# 1 <= n <= 5 * 10^4
#
#
# 1 <= chargeTimes[i], runningCosts[i] <= 10^5
#
#
# 1 <= budget <= 10^15
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def maximumRobots(self, chargeTimes: List[int], runningCosts: List[int], budget: int) -> int:
        """
        Interview explanation:
        Contiguous robots [i..j]: cost = max(chargeTimes) + (j-i+1)*sum(running).
        Max k such that some window of length k has cost <= budget.

        Algorithm:
        - Sliding window + monotonic deque for max charge; expand/shrink while
          cost exceeds budget; track max window length.

        Complexity: O(n) time, O(n) space.
        """
        n = len(chargeTimes)
        dq = deque()  # indices decreasing chargeTimes
        s = 0
        ans = 0
        left = 0
        for right in range(n):
            s += runningCosts[right]
            while dq and chargeTimes[dq[-1]] <= chargeTimes[right]:
                dq.pop()
            dq.append(right)
            while left <= right and chargeTimes[dq[0]] + (right - left + 1) * s > budget:
                if dq[0] == left:
                    dq.popleft()
                s -= runningCosts[left]
                left += 1
            ans = max(ans, right - left + 1)
        return ans

    def maximumRobots_binary_search(self, chargeTimes: List[int], runningCosts: List[int], budget: int) -> int:
        """
        Interview explanation:
        Alternate: binary search on k; check if any window of length k fits
        using sliding max + prefix sums.

        Algorithm:
        - Check(k): for each window compute max charge + k*sum via deque/prefix.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(chargeTimes)
        pref = [0]
        for x in runningCosts:
            pref.append(pref[-1] + x)

        def ok(k: int) -> bool:
            if k == 0:
                return True
            dq = deque()
            for i in range(n):
                while dq and dq[0] <= i - k:
                    dq.popleft()
                while dq and chargeTimes[dq[-1]] <= chargeTimes[i]:
                    dq.pop()
                dq.append(i)
                if i >= k - 1:
                    mx = chargeTimes[dq[0]]
                    sm = pref[i + 1] - pref[i + 1 - k]
                    if mx + k * sm <= budget:
                        return True
            return False

        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
