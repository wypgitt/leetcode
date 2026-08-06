#
# @lc app=leetcode id=295 lang=python3
#
# [295] Find Median from Data Stream
#
# https://leetcode.com/problems/find-median-from-data-stream/description/
#
# algorithms
# Hard (54.83%)
# Likes:    13383
# Dislikes: 284
# Total Accepted:    1.3M
# Total Submissions: 2.3M
# Testcase Example:  "[\"MedianFinder\",\"addNum\",\"addNum\",\"findMedian\",\"addNum\",\"findMedian\"]"
#
# The median is the middle value in an ordered integer list. If the size of the
# list is even, there is no middle value, and the median is the mean of the two
# middle values.
#
# For example, for arr = [2,3,4], the median is 3.
#
# For example, for arr = [2,3], the median is (2 + 3) / 2 = 2.5.
#
# Implement the MedianFinder class:
#
# MedianFinder() initializes the MedianFinder object.
#
# void addNum(int num) adds the integer num from the data stream to the data
# structure.
#
# double findMedian() returns the median of all elements so far. Answers within
# 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input
# ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
# [[], [1], [2], [], [3], []]
# Output
# [null, null, null, 1.5, null, 2.0]
#
# Explanation
# MedianFinder medianFinder = new MedianFinder();
# medianFinder.addNum(1); // arr = [1]
# medianFinder.addNum(2); // arr = [1, 2]
# medianFinder.findMedian(); // return 1.5 (i.e., (1 + 2) / 2)
# medianFinder.addNum(3); // arr[1, 2, 3]
# medianFinder.findMedian(); // return 2.0
#
# Constraints:
#
# -10^5 <= num <= 10^5
#
# There will be at least one element in the data structure before calling
# findMedian.
#
# At most 5 * 10^4 calls will be made to addNum and findMedian.
#
# Follow up:
#
# If all integer numbers from the stream are in the range [0, 100], how would
# you optimize your solution?
#
# If 99% of all integer numbers from the stream are in the range [0, 100], how
# would you optimize your solution?
#

# @lc code=start
import heapq


class MedianFinder:
    def __init__(self):
        """
        Interview explanation:
        Two heaps: max-heap (low half) and min-heap (high half), sizes balanced
        so median is top of low, or average of both tops.

        Algorithm:
        - addNum: push to low; move max of low to high; if high larger, move min back.
        - findMedian: if odd count (low bigger) return -low[0]; else average.

        Complexity: O(log n) add, O(1) median; O(n) space.
        """
        self.low = []   # max-heap via negation
        self.high = []  # min-heap

    def addNum(self, num: int) -> None:
        """
        Interview explanation:
        Insert into the max-heap low half, then rebalance so every low value is
        ≤ every high value and sizes differ by at most one (low may be larger).

        Algorithm:
        - Push -num to low; move low's max into high; if high bigger, move min back.

        Complexity: O(log n) time, O(1) extra space.
        """
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self) -> float:
        """
        Interview explanation:
        With balanced heaps, odd count → top of low; even → average of both tops.

        Algorithm:
        - If len(low) > len(high): return -low[0]; else (-low[0] + high[0]) / 2.

        Complexity: O(1) time, O(1) space.
        """
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()
# @lc code=end

