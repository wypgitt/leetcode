#
# @lc app=leetcode id=2251 lang=python3
#
# [2251] Number of Flowers in Full Bloom
#
# https://leetcode.com/problems/number-of-flowers-in-full-bloom/description/
#
# algorithms
# Hard (58.09%)
# Likes:    1831
# Dislikes: 46
# Total Accepted:    112.7K
# Total Submissions: 194.1K
# Testcase Example:  "[[1,6],[3,7],[9,12],[4,13]]\n[2,3,7,11]"
#
# You are given a 0-indexed 2D integer array flowers, where flowers[i] =
# [start_i, end_i] means the i^th flower will be in full bloom from start_i to
# end_i (inclusive). You are also given a 0-indexed integer array people of size
# n, where people[i] is the time that the i^th person will arrive to see the
# flowers.
#
# Return an integer array answer of size n, where answer[i] is the number of
# flowers that are in full bloom when the i^th person arrives.
#
#
#
# Example 1:
#
# Input: flowers = [[1,6],[3,7],[9,12],[4,13]], people = [2,3,7,11]
# Output: [1,2,2,2]
# Explanation: The figure above shows the times when the flowers are in full
# bloom and when the people arrive.
# For each person, we return the number of flowers in full bloom during their
# arrival.
#
# Example 2:
#
# Input: flowers = [[1,10],[3,3]], people = [3,3,2]
# Output: [2,2,1]
# Explanation: The figure above shows the times when the flowers are in full
# bloom and when the people arrive.
# For each person, we return the number of flowers in full bloom during their
# arrival.
#
#
#
# Constraints:
#
#
# 1 <= flowers.length <= 5 * 10^4
#
#
# flowers[i].length == 2
#
#
# 1 <= start_i <= end_i <= 10^9
#
#
# 1 <= people.length <= 5 * 10^4
#
#
# 1 <= people[i] <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def fullBloomFlowers(self, flowers: List[List[int]], people: List[int]) -> List[int]:
        """
        Interview explanation:
        For each person at time t, count flowers with start <= t <= end.

        Algorithm:
        - Sort starts and ends; blooms(t) = #starts<=t - #ends<t.

        Complexity: O((n+m) log n) time, O(n) space.
        """
        starts = sorted(s for s, _ in flowers)
        ends = sorted(e for _, e in flowers)
        return [bisect.bisect_right(starts, t) - bisect.bisect_left(ends, t) for t in people]

    def fullBloomFlowers_sweep(self, flowers: List[List[int]], people: List[int]) -> List[int]:
        """
        Interview explanation:
        Sweep-line alternate: +1 at start, -1 at end+1; process people in order.

        Algorithm:
        - Sort events; walk people sorted by time accumulating active blooms.

        Complexity: O((n+m) log (n+m)) time, O(n+m) space.
        """
        events = []
        for s, e in flowers:
            events.append((s, 1))
            events.append((e + 1, -1))
        events.sort()
        order = sorted(range(len(people)), key=lambda i: people[i])
        ans = [0] * len(people)
        i = cur = 0
        for idx in order:
            t = people[idx]
            while i < len(events) and events[i][0] <= t:
                cur += events[i][1]
                i += 1
            ans[idx] = cur
        return ans
# @lc code=end
