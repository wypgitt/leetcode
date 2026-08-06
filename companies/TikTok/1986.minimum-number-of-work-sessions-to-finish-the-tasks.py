#
# @lc app=leetcode id=1986 lang=python3
#
# [1986] Minimum Number of Work Sessions to Finish the Tasks
#
# https://leetcode.com/problems/minimum-number-of-work-sessions-to-finish-the-tasks/description/
#
# algorithms
# Medium (35.18%)
# Likes:    1201
# Dislikes: 71
# Total Accepted:    36.5K
# Total Submissions: 104K
# Testcase Example:  "[1,2,3]"
#
# There are n tasks assigned to you. The task times are represented as an
# integer array tasks of length n, where the i^th task takes tasks[i] hours to
# finish. A work session is when you work for at most sessionTime consecutive
# hours and then take a break.
#
# You should finish the given tasks in a way that satisfies the following
# conditions:
#
# If you start a task in a work session, you must complete it in the same work
# session.
#
# You can start a new task immediately after finishing the previous one.
#
# You may complete the tasks in any order.
#
# Given tasks and sessionTime, return the minimum number of work sessions
# needed to finish all the tasks following the conditions above.
#
# The tests are generated such that sessionTime is greater than or equal to the
# maximum element in tasks[i].
#
# Example 1:
#
# Input: tasks = [1,2,3], sessionTime = 3
# Output: 2
# Explanation: You can finish the tasks in two work sessions.
# - First work session: finish the first and the second tasks in 1 + 2 = 3
# hours.
# - Second work session: finish the third task in 3 hours.
#
# Example 2:
#
# Input: tasks = [3,1,3,1,1], sessionTime = 8
# Output: 2
# Explanation: You can finish the tasks in two work sessions.
# - First work session: finish all the tasks except the last one in 3 + 1 + 3 +
# 1 = 8 hours.
# - Second work session: finish the last task in 1 hour.
#
# Example 3:
#
# Input: tasks = [1,2,3,4,5], sessionTime = 15
# Output: 1
# Explanation: You can finish all the tasks in one work session.
#
# Constraints:
#
# n == tasks.length
#
# 1 <= n <= 14
#
# 1 <= tasks[i] <= 10
#
# max(tasks[i]) <= sessionTime <= 15
#

# @lc code=start
from typing import List


class Solution:
    def minSessions(self, tasks: List[int], sessionTime: int) -> int:
        """
        Interview explanation:
        Assign tasks into minimum sessions each of capacity sessionTime.
        Bit DP: for each subset, try last session partition.

        Algorithm:
        - dp[mask] = (sessions, load_in_last) minimal; or binary search sessions
          + bit DP feasibility. Classic: dp[mask] min sessions for subset;
          transition add a task into a new/existing session via state.

        Complexity: O(2^n * n) or O(2^n * n^2); n<=14.
        """
        n = len(tasks)
        # dp[mask] = minimum (sessions used, time used in current session)
        INF = (n + 1, 0)
        dp = [INF] * (1 << n)
        dp[0] = (1, 0)  # start with one empty session conceptually
        for mask in range(1 << n):
            sessions, load = dp[mask]
            if sessions > n:
                continue
            for i in range(n):
                if mask & (1 << i):
                    continue
                t = tasks[i]
                if load + t <= sessionTime:
                    nxt = (sessions, load + t)
                else:
                    nxt = (sessions + 1, t)
                nmask = mask | (1 << i)
                if nxt < dp[nmask]:
                    dp[nmask] = nxt
        return dp[(1 << n) - 1][0]

    def minSessions_feasibility(self, tasks: List[int], sessionTime: int) -> int:
        """
        Interview explanation:
        Alternate: binary search number of sessions; check if tasks can be packed
        into that many bins (backtracking / bit DP).

        Algorithm:
        - lo=1, hi=n; check(mid) via assigning masks into mid capacities.

        Complexity: O(log n * 2^n * n) time.
        """
        n = len(tasks)
        # Precompute sum of each subset
        ssum = [0] * (1 << n)
        for mask in range(1 << n):
            for i in range(n):
                if mask & (1 << i):
                    ssum[mask] += tasks[i]

        def ok(sessions: int) -> bool:
            # dp[mask] = whether mask can be packed into some number of sessions
            # Actually: min sessions for mask via subset enumeration
            need = [n + 1] * (1 << n)
            need[0] = 0
            for mask in range(1 << n):
                if need[mask] > sessions:
                    continue
                # grow remaining tasks into one valid session subset
                remaining = ((1 << n) - 1) ^ mask
                sub = remaining
                while sub:
                    if ssum[sub] <= sessionTime:
                        need[mask | sub] = min(need[mask | sub], need[mask] + 1)
                    sub = (sub - 1) & remaining
            return need[(1 << n) - 1] <= sessions

        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end

