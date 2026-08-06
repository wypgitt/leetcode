#
# @lc app=leetcode id=1851 lang=python3
#
# [1851] Minimum Interval to Include Each Query
#
# https://leetcode.com/problems/minimum-interval-to-include-each-query/description/
#
# algorithms
# Hard (54.86%)
# Likes:    1182
# Dislikes: 50
# Total Accepted:    77.3K
# Total Submissions: 141K
# Testcase Example:  "[[1,4],[2,4],[3,6],[4,4]]"
#
# You are given a 2D integer array intervals, where intervals[i] = [left_i,
# right_i] describes the i^th interval starting at left_i and ending at right_i
# (inclusive). The size of an interval is defined as the number of integers it
# contains, or more formally right_i - left_i + 1.
#
# You are also given an integer array queries. The answer to the j^th query is
# the size of the smallest interval i such that left_i <= queries[j] <=
# right_i. If no such interval exists, the answer is -1.
#
# Return an array containing the answers to the queries.
#
# Example 1:
#
# Input: intervals = [[1,4],[2,4],[3,6],[4,4]], queries = [2,3,4,5]
# Output: [3,3,1,4]
# Explanation: The queries are processed as follows:
# - Query = 2: The interval [2,4] is the smallest interval containing 2. The
# answer is 4 - 2 + 1 = 3.
# - Query = 3: The interval [2,4] is the smallest interval containing 3. The
# answer is 4 - 2 + 1 = 3.
# - Query = 4: The interval [4,4] is the smallest interval containing 4. The
# answer is 4 - 4 + 1 = 1.
# - Query = 5: The interval [3,6] is the smallest interval containing 5. The
# answer is 6 - 3 + 1 = 4.
#
# Example 2:
#
# Input: intervals = [[2,3],[2,5],[1,8],[20,25]], queries = [2,19,5,22]
# Output: [2,-1,4,6]
# Explanation: The queries are processed as follows:
# - Query = 2: The interval [2,3] is the smallest interval containing 2. The
# answer is 3 - 2 + 1 = 2.
# - Query = 19: None of the intervals contain 19. The answer is -1.
# - Query = 5: The interval [2,5] is the smallest interval containing 5. The
# answer is 5 - 2 + 1 = 4.
# - Query = 22: The interval [20,25] is the smallest interval containing 22.
# The answer is 25 - 20 + 1 = 6.
#
# Constraints:
#
# 1 <= intervals.length <= 10^5
#
# 1 <= queries.length <= 10^5
#
# intervals[i].length == 2
#
# 1 <= left_i <= right_i <= 10^7
#
# 1 <= queries[j] <= 10^7
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minInterval(self, intervals: List[List[int]], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        For each query, find the smallest interval covering it. Sort intervals
        and queries; sweep queries left→right, adding intervals that start ≤ q
        into a min-heap by size, popping those that end < q.

        Algorithm (sort + min-heap):
        - Sort intervals by left; sort queries with original indices.
        - Heap of (size, right). For each query q: push all intervals with
          left ≤ q; pop while right < q; top size is answer (or -1).

        Complexity: O((n+q) log n) time, O(n+q) space.
        """
        intervals = sorted(intervals)
        qs = sorted((q, i) for i, q in enumerate(queries))
        ans = [-1] * len(queries)
        heap = []
        i = 0
        n = len(intervals)
        for q, qi in qs:
            while i < n and intervals[i][0] <= q:
                l, r = intervals[i]
                heapq.heappush(heap, (r - l + 1, r))
                i += 1
            while heap and heap[0][1] < q:
                heapq.heappop(heap)
            if heap:
                ans[qi] = heap[0][0]
        return ans

    def minInterval_bruteforce(self, intervals: List[List[int]], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        Classic alternate for interview discussion: for each query scan all
        covering intervals and take min size. Too slow for constraints.

        Algorithm:
        - For each q: ans = min(r-l+1 for l,r in intervals if l<=q<=r) or -1.

        Complexity: O(n*q) time, O(1) extra space.
        """
        out = []
        for q in queries:
            best = -1
            for l, r in intervals:
                if l <= q <= r:
                    sz = r - l + 1
                    if best < 0 or sz < best:
                        best = sz
            out.append(best)
        return out
# @lc code=end
