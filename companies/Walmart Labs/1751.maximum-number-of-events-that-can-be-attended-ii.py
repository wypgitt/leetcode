#
# @lc app=leetcode id=1751 lang=python3
#
# [1751] Maximum Number of Events That Can Be Attended II
#
# https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended-ii/description/
#
# algorithms
# Hard (63.4%)
# Likes:    2569
# Dislikes: 54
# Total Accepted:    166K
# Total Submissions: 261K
# Testcase Example:  "[[1,2,4],[3,4,3],[2,3,1]]"
#
# You are given an array of events where events[i] = [startDay_i, endDay_i,
# value_i]. The i^th event starts at startDay_i_ and ends at endDay_i, and if
# you attend this event, you will receive a value of value_i. You are also
# given an integer k which represents the maximum number of events you can
# attend.
#
# You can only attend one event at a time. If you choose to attend an event,
# you must attend the entire event. Note that the end day is inclusive: that
# is, you cannot attend two events where one of them starts and the other ends
# on the same day.
#
# Return the maximum sum of values that you can receive by attending events.
#
# Example 1:
#
# Input: events = [[1,2,4],[3,4,3],[2,3,1]], k = 2
# Output: 7
# Explanation: Choose the green events, 0 and 1 (0-indexed) for a total value
# of 4 + 3 = 7.
#
# Example 2:
#
# Input: events = [[1,2,4],[3,4,3],[2,3,10]], k = 2
# Output: 10
# Explanation: Choose event 2 for a total value of 10.
# Notice that you cannot attend any other event as they overlap, and that you
# do not have to attend k events.
#
# Example 3:
#
# Input: events = [[1,1,1],[2,2,2],[3,3,3],[4,4,4]], k = 3
# Output: 9
# Explanation: Although the events do not overlap, you can only attend 3
# events. Pick the highest valued three.
#
# Constraints:
#
# 1 <= k <= events.length
#
# 1 <= k * events.length <= 10^6
#
# 1 <= startDay_i <= endDay_i <= 10^9
#
# 1 <= value_i <= 10^6
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def maxValue(self, events: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Attend up to k non-overlapping events (end inclusive → next start > end).
        Sort by start; DP[i][t] = max value from events[i:] using ≤t attendances.
        Binary-search the next feasible event after taking events[i].

        Algorithm:
        - Sort events by startDay; starts = [e[0] for e in events].
        - dp[i][t] = max(dp[i+1][t], value_i + dp[next][t-1]).
        - next = bisect_right(starts, endDay).

        Complexity: O(n k log n) time, O(n k) space.
        """
        n = len(events)
        events = sorted(events)
        starts = [e[0] for e in events]
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            nxt = bisect.bisect_right(starts, events[i][1])
            for t in range(1, k + 1):
                dp[i][t] = max(dp[i + 1][t], events[i][2] + dp[nxt][t - 1])
        return dp[0][k]

    def maxValue_memo(self, events: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate classic: top-down memoized DFS with binary search for the
        next non-overlapping event. Same recurrence as iterative DP.

        Algorithm:
        - Sort by start; dfs(i, remain): skip or take + dfs(next, remain-1).
        - Memo on (i, remain).

        Complexity: O(n k log n) time, O(n k) space.
        """
        n = len(events)
        events = sorted(events)
        starts = [e[0] for e in events]
        memo = {}

        def dfs(i: int, remain: int) -> int:
            if i >= n or remain == 0:
                return 0
            key = (i, remain)
            if key in memo:
                return memo[key]
            best = dfs(i + 1, remain)
            nxt = bisect.bisect_right(starts, events[i][1])
            best = max(best, events[i][2] + dfs(nxt, remain - 1))
            memo[key] = best
            return best

        return dfs(0, k)
# @lc code=end
