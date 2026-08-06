#
# @lc app=leetcode id=1481 lang=python3
#
# [1481] Least Number of Unique Integers after K Removals
#
# https://leetcode.com/problems/least-number-of-unique-integers-after-k-removals/description/
#
# algorithms
# Medium (63.91%)
# Likes:    2353
# Dislikes: 235
# Total Accepted:    287K
# Total Submissions: 448K
# Testcase Example:  "[5,5,4]"
#
# Given an array of integers arr and an integer k. Find the least number of
# unique integers after removing exactly k elements.
#
# Example 1:
#
# Input: arr = [5,5,4], k = 1
# Output: 1
# Explanation: Remove the single 4, only 5 is left.
#
# Example 2:
#
# Input: arr = [4,3,1,1,3,3,2], k = 3
# Output: 2
# Explanation: Remove 4, 2 and either one of the two 1s or three 3s. 1 and 3
# will be left.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 10^9
#
# 0 <= k <= arr.length
#

# @lc code=start
from typing import List
from collections import Counter
import heapq


class Solution:
    def findLeastNumOfUniqueInts(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Remove k occurrences to minimize number of distinct remaining values —
        greedily remove smallest frequencies first.

        Algorithm:
        - Counter; sort frequencies ascending; subtract from k until can't.

        Complexity: O(n + d log d) time, O(d) space.
        """
        freqs = sorted(Counter(arr).values())
        rem = len(freqs)
        for f in freqs:
            if k >= f:
                k -= f
                rem -= 1
            else:
                break
        return rem

    def findLeastNumOfUniqueInts_heap(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: min-heap of frequencies; pop while k allows.

        Algorithm:
        - heapify freq values; same greedy removals.

        Complexity: O(n + d log d) time, O(d) space.
        """
        heap = list(Counter(arr).values())
        heapq.heapify(heap)
        while heap and k >= heap[0]:
            k -= heapq.heappop(heap)
        return len(heap)
# @lc code=end
