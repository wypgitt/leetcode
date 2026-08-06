#
# @lc app=leetcode id=2335 lang=python3
#
# [2335] Minimum Amount of Time to Fill Cups
#
# https://leetcode.com/problems/minimum-amount-of-time-to-fill-cups/description/
#
# algorithms
# Easy (60.46%)
# Likes:    775
# Dislikes: 93
# Total Accepted:    71.1K
# Total Submissions: 117.6K
# Testcase Example:  "[1,4,2]"
#
# You have a water dispenser that can dispense cold, warm, and hot water. Every
# second, you can either fill up 2 cups with different types of water, or 1 cup
# of any type of water.
#
# You are given a 0-indexed integer array amount of length 3 where amount[0],
# amount[1], and amount[2] denote the number of cold, warm, and hot water cups
# you need to fill respectively. Return the minimum number of seconds needed to
# fill up all the cups.
#
#
#
# Example 1:
#
# Input: amount = [1,4,2]
# Output: 4
# Explanation: One way to fill up the cups is:
# Second 1: Fill up a cold cup and a warm cup.
# Second 2: Fill up a warm cup and a hot cup.
# Second 3: Fill up a warm cup and a hot cup.
# Second 4: Fill up a warm cup.
# It can be proven that 4 is the minimum number of seconds needed.
#
# Example 2:
#
# Input: amount = [5,4,4]
# Output: 7
# Explanation: One way to fill up the cups is:
# Second 1: Fill up a cold cup, and a hot cup.
# Second 2: Fill up a cold cup, and a warm cup.
# Second 3: Fill up a cold cup, and a warm cup.
# Second 4: Fill up a warm cup, and a hot cup.
# Second 5: Fill up a cold cup, and a hot cup.
# Second 6: Fill up a cold cup, and a warm cup.
# Second 7: Fill up a hot cup.
#
# Example 3:
#
# Input: amount = [5,0,0]
# Output: 5
# Explanation: Every second, we fill up a cold cup.
#
#
#
# Constraints:
#
#
# amount.length == 3
#
#
# 0 <= amount[i] <= 100
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def fillCups(self, amount: List[int]) -> int:
        """
        Interview explanation:
        Each second fill 1 or 2 different types by 1. Min seconds to zero all.

        Algorithm:
        - Math: max(max(amount), ceil(sum/2)).

        Complexity: O(1) time, O(1) space.
        """
        return max(max(amount), (sum(amount) + 1) // 2)

    def fillCups_math(self, amount: List[int]) -> int:
        """
        Interview explanation:
        Closed-form max(max, ceil(sum/2)) (same as primary).

        Algorithm:
        - Bottleneck is either the largest type or total/2.

        Complexity: O(1) time, O(1) space.
        """
        return self.fillCups(amount)

    def fillCups_heap(self, amount: List[int]) -> int:
        """
        Interview explanation:
        Simulation with max-heap: always reduce the two largest remaining.

        Algorithm:
        - Pop two >0, decrement, push back; count seconds.

        Complexity: O(S log 3) time where S=sum(amount), O(1) space.
        """
        h = [-x for x in amount if x]
        heapq.heapify(h)
        ans = 0
        while h:
            if len(h) == 1:
                return ans - h[0]
            a = -heapq.heappop(h)
            b = -heapq.heappop(h)
            ans += 1
            if a - 1:
                heapq.heappush(h, -(a - 1))
            if b - 1:
                heapq.heappush(h, -(b - 1))
        return ans
# @lc code=end
