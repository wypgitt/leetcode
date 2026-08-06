#
# @lc app=leetcode id=1326 lang=python3
#
# [1326] Minimum Number of Taps to Open to Water a Garden
#
# https://leetcode.com/problems/minimum-number-of-taps-to-open-to-water-a-garden/description/
#
# algorithms
# Hard (51.04%)
# Likes:    3646
# Dislikes: 198
# Total Accepted:    165K
# Total Submissions: 323K
# Testcase Example:  "5"
#
# There is a one-dimensional garden on the x-axis. The garden starts at the
# point 0 and ends at the point n. (i.e., the length of the garden is n).
#
# There are n + 1 taps located at points [0, 1, ..., n] in the garden.
#
# Given an integer n and an integer array ranges of length n + 1 where
# ranges[i] (0-indexed) means the i-th tap can water the area [i - ranges[i], i
# + ranges[i]] if it was open.
#
# Return the minimum number of taps that should be open to water the whole
# garden, If the garden cannot be watered return -1.
#
# Example 1:
#
# Input: n = 5, ranges = [3,4,1,1,0,0]
# Output: 1
# Explanation: The tap at point 0 can cover the interval [-3,3]
# The tap at point 1 can cover the interval [-3,5]
# The tap at point 2 can cover the interval [1,3]
# The tap at point 3 can cover the interval [2,4]
# The tap at point 4 can cover the interval [4,4]
# The tap at point 5 can cover the interval [5,5]
# Opening Only the second tap will water the whole garden [0,5]
#
# Example 2:
#
# Input: n = 3, ranges = [0,0,0,0]
# Output: -1
# Explanation: Even if you activate all the four taps you cannot water the
# whole garden.
#
# Constraints:
#
# 1 <= n <= 10^4
#
# ranges.length == n + 1
#
# 0 <= ranges[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def minTaps(self, n: int, ranges: List[int]) -> int:
        """
        Interview explanation:
        Tap i covers [i-ranges[i], i+ranges[i]] clamped to [0,n]. Equivalent to
        jump game: from each left endpoint, farthest right reachable. Greedy
        jump-game II style.

        Algorithm (greedy jump):
        - max_reach[L] = max R among taps covering from L.
        - For i in 0..n: max_reach[left]=max(right). Then jump greedy.

        Complexity: O(n) time, O(n) space.
        """
        max_reach = [0] * (n + 1)
        for i, r in enumerate(ranges):
            left = max(0, i - r)
            right = min(n, i + r)
            max_reach[left] = max(max_reach[left], right)

        taps = end = farthest = 0
        for i in range(n):
            farthest = max(farthest, max_reach[i])
            if i == end:
                if farthest <= i:
                    return -1
                taps += 1
                end = farthest
                if end >= n:
                    return taps
        return -1 if end < n else taps

    def minTaps_dp(self, n: int, ranges: List[int]) -> int:
        """
        Interview explanation:
        Alternate DP: dp[x] = min taps to water [0,x]. For each tap covering
        [L,R], update dp[j] for j in L+1..R.

        Algorithm:
        - dp[0]=0, rest INF; for each tap relax interval.

        Complexity: O(n * avg_range) time, O(n) space.
        """
        INF = 10**9
        dp = [INF] * (n + 1)
        dp[0] = 0
        for i, r in enumerate(ranges):
            left = max(0, i - r)
            right = min(n, i + r)
            for j in range(left + 1, right + 1):
                dp[j] = min(dp[j], dp[left] + 1)
        return -1 if dp[n] >= INF else dp[n]
# @lc code=end

