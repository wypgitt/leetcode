#
# @lc app=leetcode id=683 lang=python3
#
# [683] K Empty Slots
#
# https://leetcode.com/problems/k-empty-slots/description/
#
# algorithms
# Hard (38.02%)
# Likes:    831
# Dislikes: 707
# Total Accepted:    67.7K
# Total Submissions: 178.1K
# Testcase Example:  "[1,3,2]\n1"
#
#
# You have n bulbs in a row numbered from 1 to n. Initially, all the bulbs
# are turned off. We turn on exactly one bulb every day until all bulbs
# are on after n days.
#
# You are given an array bulbs of length n where bulbs[i] = x means that
# on the (i+1)^th day, we will turn on the bulb at position x where i is
# 0-indexed and x is 1-indexed.
#
# Given an integer k, return the minimum day number such that there exists
# two turned on bulbs that have exactly k bulbs between them that are all
# turned off. If there isn't such day, return -1.
#
# Example 1:
#
# Input: bulbs = [1,3,2], k = 1
# Output: 2
# Explanation:
# On the first day: bulbs[0] = 1, first bulb is turned on: [1,0,0]
# On the second day: bulbs[1] = 3, third bulb is turned on: [1,0,1]
# On the third day: bulbs[2] = 2, second bulb is turned on: [1,1,1]
# We return 2 because on the second day, there were two on bulbs with one
# off bulb between them.
#
# Example 2:
#
# Input: bulbs = [1,2,3], k = 1
# Output: -1
#
# Constraints:
#
# n == bulbs.length
#
# 1 <= n <= 2 * 10^4
#
# 1 <= bulbs[i] <= n
#
# bulbs is a permutation of numbers from 1 to n.
#
# 0 <= k <= 2 * 10^4
#
# @lc code=start
from typing import List


class Solution:
    def kEmptySlots(self, bulbs: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium: bulbs[i] is the position turned on at day i+1. Earliest day when
        two on bulbs have exactly k empty positions between them.

        Algorithm:
        - days[pos-1] = turn-on day.
        - Sliding window size k+2 with ends left,right=left+k+1. If every middle
          day is later than both ends, candidate = max(end days). On a mid that
          is earlier, restart window at that mid.

        Complexity: O(n) time, O(n) space.
        """
        n = len(bulbs)
        days = [0] * n
        for day, pos in enumerate(bulbs, 1):
            days[pos - 1] = day

        ans = float("inf")
        left = 0
        right = k + 1
        while right < n:
            for i in range(left + 1, right):
                if days[i] < days[left] or days[i] < days[right]:
                    left, right = i, i + k + 1
                    break
            else:
                ans = min(ans, max(days[left], days[right]))
                left, right = right, right + k + 1
        return int(ans) if ans < float("inf") else -1
# @lc code=end
