#
# @lc app=leetcode id=1560 lang=python3
#
# [1560] Most Visited Sector in  a Circular Track
#
# https://leetcode.com/problems/most-visited-sector-in-a-circular-track/description/
#
# algorithms
# Easy (59.99%)
# Likes:    341
# Dislikes: 682
# Total Accepted:    41.0K
# Total Submissions: 68.4K
# Testcase Example:  "4"
#
# Given an integer n and an integer array rounds. We have a circular track
# which consists of n sectors labeled from 1 to n. A marathon will be held on
# this track, the marathon consists of m rounds. The i^th round starts at
# sector rounds[i - 1] and ends at sector rounds[i]. For example, round 1
# starts at sector rounds[0] and ends at sector rounds[1]
#
# Return an array of the most visited sectors sorted in ascending order.
#
# Notice that you circulate the track in ascending order of sector numbers in
# the counter-clockwise direction (See the first example).
#
# Example 1:
#
# Input: n = 4, rounds = [1,3,1,2]
# Output: [1,2]
# Explanation: The marathon starts at sector 1. The order of the visited
# sectors is as follows:
# 1 --> 2 --> 3 (end of round 1) --> 4 --> 1 (end of round 2) --> 2 (end of
# round 3 and the marathon)
# We can see that both sectors 1 and 2 are visited twice and they are the most
# visited sectors. Sectors 3 and 4 are visited only once.
#
# Example 2:
#
# Input: n = 2, rounds = [2,1,2,1,2,1,2,1,2]
# Output: [2]
#
# Example 3:
#
# Input: n = 7, rounds = [1,3,5,7]
# Output: [1,2,3,4,5,6,7]
#
# Constraints:
#
# 2 <= n <= 100
#
# 1 <= m <= 100
#
# rounds.length == m + 1
#
# 1 <= rounds[i] <= n
#
# rounds[i] != rounds[i + 1] for 0 <= i < m
#

# @lc code=start
from typing import List


class Solution:
    def mostVisited(self, n: int, rounds: List[int]) -> List[int]:
        """
        Interview explanation:
        Circular track 1..n; rounds are consecutive visits. Intermediate full
        laps visit every sector equally; only the arc from rounds[0] to
        rounds[-1] (inclusive) gets one extra visit. Return that arc sorted.

        Algorithm:
        - start, end = rounds[0], rounds[-1]
        - if start <= end: range(start, end+1) else [1..end]+[start..n]

        Complexity: O(n) time, O(n) space.
        """
        start, end = rounds[0], rounds[-1]
        if start <= end:
            return list(range(start, end + 1))
        return list(range(1, end + 1)) + list(range(start, n + 1))

    def mostVisited_count(self, n: int, rounds: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate simulation: walk each segment rounds[i]→rounds[i+1] counting
        visits; return sectors with max count.

        Algorithm:
        - For each consecutive pair, walk circularly incrementing counters.

        Complexity: O(n * len(rounds)) worst, O(n) space.
        """
        cnt = [0] * (n + 1)
        cnt[rounds[0]] += 1
        for a, b in zip(rounds, rounds[1:]):
            x = a
            while x != b:
                x = 1 if x == n else x + 1
                cnt[x] += 1
        mx = max(cnt[1:])
        return [i for i in range(1, n + 1) if cnt[i] == mx]
# @lc code=end

