#
# @lc app=leetcode id=3540 lang=python3
#
# [3540] Minimum Time to Visit All Houses
#
# https://leetcode.com/problems/minimum-time-to-visit-all-houses/description/
#
# algorithms
# Medium (69.19%)
# Likes:    9
# Dislikes: 2
# Total Accepted:    1.3K
# Total Submissions: 1.9K
# Testcase Example:  "[1,4,4]\n[4,1,2]\n[1,2,0,2]"
#
#
# You are given two integer arrays forward and backward, both of size n.
# You are also given another integer array queries.
#
# There are n houses arranged in a circle. The houses are connected via
# roads in a special arrangement:
#
# For all 0 <= i <= n - 2, house i is connected to house i + 1 via a road
# with length forward[i] meters. Additionally, house n - 1 is connected
# back to house 0 via a road with length forward[n - 1] meters, completing
# the circle.
#
# For all 1 <= i <= n - 1, house i is connected to house i - 1 via a road
# with length backward[i] meters. Additionally, house 0 is connected back
# to house n - 1 via a road with length backward[0] meters, completing the
# circle.
#
# You can walk at a pace of one meter per second. Starting from house 0,
# find the minimum time taken to visit each house in the order specified
# by queries.
#
# Return the minimum total time taken to visit the houses.
#
# Example 1:
#
# Input: forward = [1,4,4], backward = [4,1,2], queries = [1,2,0,2]
#
# Output: 12
#
# Explanation:
#
# The path followed is 0^(0) → 1^(1) →​​​​​​​ 2^(5) → 1^(7) →​​​​​​​ 0^(8)
# → 2^(12).
#
# Note: The notation used is node^(total time), → represents forward road,
# and → represents backward road.
#
# Example 2:
#
# Input: forward = [1,1,1,1], backward = [2,2,2,2], queries = [1,2,3,0]
#
# Output: 4
#
# Explanation:
#
# The path travelled is 0 →​​​​​​​ 1 →​​​​​​​ 2 →​​​​​​​ 3 → 0. Each step
# is in the forward direction and requires 1 second.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# n == forward.length == backward.length
#
# 1 <= forward[i], backward[i] <= 10^5
#
# 1 <= queries.length <= 10^5
#
# 0 <= queries[i] < n
#
# queries[i] != queries[i + 1]
#
# queries[0] is not 0.
#

# @lc code=start
import itertools
from typing import List


class Solution:
    def minTotalTime(
        self, forward: List[int], backward: List[int], queries: List[int]
    ) -> int:
        """
        Interview explanation:
        Houses form a directed circle with distinct forward and backward edge
        weights. Between consecutive query houses take min(clockwise, counterclockwise)
        via prefix sums.

        Algorithm:
        - prefixF[i] = sum of first i forward edges; prefixB cumulative backward.
        - For each step pos→q, compute both arc lengths in O(1) and add the min.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(forward)
        summ = sum(backward)
        prefix_f = [0] + list(itertools.accumulate(forward))
        prefix_b = list(itertools.accumulate(backward)) + [0]
        ans = 0
        pos = 0
        for q in queries:
            r = (prefix_f[-1] if q < pos else 0) + prefix_f[q] - prefix_f[pos]
            l = (summ if q > pos else 0) + prefix_b[pos] - prefix_b[q]
            ans += min(l, r)
            pos = q
        return ans
# @lc code=end
