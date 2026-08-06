#
# @lc app=leetcode id=1354 lang=python3
#
# [1354] Construct Target Array With Multiple Sums
#
# https://leetcode.com/problems/construct-target-array-with-multiple-sums/description/
#
# algorithms
# Hard (37.16%)
# Likes:    2146
# Dislikes: 181
# Total Accepted:    90.3K
# Total Submissions: 243K
# Testcase Example:  "[9,3,5]"
#
# You are given an array target of n integers. From a starting array arr
# consisting of n 1's, you may perform the following procedure :
#
# let x be the sum of all elements currently in your array.
#
# choose index i, such that 0 <= i < n and set the value of arr at index i to
# x.
#
# You may repeat this procedure as many times as needed.
#
# Return true if it is possible to construct the target array from arr,
# otherwise, return false.
#
# Example 1:
#
# Input: target = [9,3,5]
# Output: true
# Explanation: Start with arr = [1, 1, 1]
# [1, 1, 1], sum = 3 choose index 1
# [1, 3, 1], sum = 5 choose index 2
# [1, 3, 5], sum = 9 choose index 0
# [9, 3, 5] Done
#
# Example 2:
#
# Input: target = [1,1,1,2]
# Output: false
# Explanation: Impossible to create target array from [1,1,1,1].
#
# Example 3:
#
# Input: target = [8,5]
# Output: true
#
# Constraints:
#
# n == target.length
#
# 1 <= n <= 5 * 10^4
#
# 1 <= target[i] <= 10^9
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def isPossible(self, target: List[int]) -> bool:
        """
        Interview explanation:
        Forward replaces an element with sum of all; reverse: repeatedly replace
        the max value x with x - (total-x). Use modulo to skip many steps when
        max >> rest.

        Algorithm:
        - Max-heap of target; total=sum
        - While max>1: rest=total-max; if rest<1 return False
          nxt = max % rest (or max-rest if rest==1); if nxt==0 and n>1 fail
          Update heap/total

        Complexity: O(n + log(max)*log n) time, O(n) space.
        """
        if len(target) == 1:
            return target[0] == 1
        total = sum(target)
        hq = [-x for x in target]
        heapq.heapify(hq)
        while True:
            mx = -heapq.heappop(hq)
            if mx == 1:
                return True
            rest = total - mx
            if rest == 1:
                return True
            if rest < 1 or mx <= rest:
                return False
            nxt = mx % rest
            if nxt == 0:
                return False
            total = total - mx + nxt
            heapq.heappush(hq, -nxt)
# @lc code=end
