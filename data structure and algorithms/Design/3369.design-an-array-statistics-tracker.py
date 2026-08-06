#
# @lc app=leetcode id=3369 lang=python3
#
# [3369] Design an Array Statistics Tracker 
#
# https://leetcode.com/problems/design-an-array-statistics-tracker/description/
#
# algorithms
# Hard (35.79%)
# Likes:    15
# Dislikes: 2
# Total Accepted:    1.5K
# Total Submissions: 4.3K
# Testcase Example:  "[\"StatisticsTracker\",\"addNumber\",\"addNumber\",\"addNumber\",\"addNumber\",\"getMean\",\"getMedian\",\"getMode\",\"removeFirstAddedNumber\",\"getMode\"]\n[[],[4],[4],[2],[3],[],[],[],[],[]]"
#
#
# Design a data structure that keeps track of the values in it and answers
# some queries regarding their mean, median, and mode.
#
# Implement the StatisticsTracker class.
#
# StatisticsTracker(): Initialize the StatisticsTracker object with an
# empty array.
#
# void addNumber(int number): Add number to the data structure.
#
# void removeFirstAddedNumber(): Remove the earliest added number from the
# data structure.
#
# int getMean(): Return the floored mean of the numbers in the data
# structure.
#
# int getMedian(): Return the median of the numbers in the data structure.
#
# int getMode(): Return the mode of the numbers in the data structure. If
# there are multiple modes, return the smallest one.
#
# Note:
#
# The mean of an array is the sum of all the values divided by the number
# of values in the array.
#
# The median of an array is the middle element of the array when it is
# sorted in non-decreasing order. If there are two choices for a median,
# the larger of the two values is taken.
#
# The mode of an array is the element that appears most often in the
# array.
#
# Example 1:
#
# Input:
#
# ["StatisticsTracker", "addNumber", "addNumber", "addNumber",
# "addNumber", "getMean", "getMedian", "getMode",
# "removeFirstAddedNumber", "getMode"]
#
# [[], [4], [4], [2], [3], [], [], [], [], []]
#
# Output:
#
# [null, null, null, null, null, 3, 4, 4, null, 2]
#
# Explanation
#
# StatisticsTracker statisticsTracker = new StatisticsTracker();
#
# statisticsTracker.addNumber(4); // The data structure now contains [4]
#
# statisticsTracker.addNumber(4); // The data structure now contains [4,
# 4]
#
# statisticsTracker.addNumber(2); // The data structure now contains [4,
# 4, 2]
#
# statisticsTracker.addNumber(3); // The data structure now contains [4,
# 4, 2, 3]
#
# statisticsTracker.getMean(); // return 3
#
# statisticsTracker.getMedian(); // return 4
#
# statisticsTracker.getMode(); // return 4
#
# statisticsTracker.removeFirstAddedNumber(); // The data structure now
# contains [4, 2, 3]
#
# statisticsTracker.getMode(); // return 2
#
# Example 2:
#
# Input:
#
# ["StatisticsTracker", "addNumber", "addNumber", "getMean",
# "removeFirstAddedNumber", "addNumber", "addNumber",
# "removeFirstAddedNumber", "getMedian", "addNumber", "getMode"]
#
# [[], [9], [5], [], [], [5], [6], [], [], [8], []]
#
# Output:
#
# [null, null, null, 7, null, null, null, null, 6, null, 5]
#
# Explanation
#
# StatisticsTracker statisticsTracker = new StatisticsTracker();
#
# statisticsTracker.addNumber(9); // The data structure now contains [9]
#
# statisticsTracker.addNumber(5); // The data structure now contains [9,
# 5]
#
# statisticsTracker.getMean(); // return 7
#
# statisticsTracker.removeFirstAddedNumber(); // The data structure now
# contains [5]
#
# statisticsTracker.addNumber(5); // The data structure now contains [5,
# 5]
#
# statisticsTracker.addNumber(6); // The data structure now contains [5,
# 5, 6]
#
# statisticsTracker.removeFirstAddedNumber(); // The data structure now
# contains [5, 6]
#
# statisticsTracker.getMedian(); // return 6
#
# statisticsTracker.addNumber(8); // The data structure now contains [5,
# 6, 8]
#
# statisticsTracker.getMode(); // return 5
#
# Constraints:
#
# 1 <= number <= 10^9
#
# At most, 10^5 calls will be made to addNumber, removeFirstAddedNumber,
# getMean, getMedian, and getMode in total.
#
# removeFirstAddedNumber, getMean, getMedian, and getMode will be called
# only if there is at least one element in the data structure.
#

# @lc code=start
from collections import deque, defaultdict

try:
    from sortedcontainers import SortedList
except ImportError:  # local fallback
    import bisect

    class SortedList(list):
        def add(self, x):
            bisect.insort(self, x)

        def discard(self, x):
            i = bisect.bisect_left(self, x)
            if i < len(self) and self[i] == x:
                del self[i]

        def remove(self, x):
            i = bisect.bisect_left(self, x)
            if i < len(self) and self[i] == x:
                del self[i]
            else:
                raise ValueError(x)


class StatisticsTracker:
    """
    Interview explanation:
    FIFO multiset with mean / median / mode queries.
    Deque for order; SortedList for order stats; freq SortedList for mode.

    Algorithm:
    - add/remove update sum, SortedList of values, and (value, freq) ordered by
      (-freq, value).
    - mean = sum // n; median = sorted[n//2] (larger of two middles);
      mode = first in freq list.

    Complexity: O(log n) per update with SortedList (O(n) local fallback);
    O(1) queries. O(n) space.
    """

    def __init__(self):
        self.q = deque()
        self.s = 0
        self.cnt = defaultdict(int)
        self.sl = SortedList()
        # Prefer key= when available (sortedcontainers); else store (-freq, val)
        try:
            self.sl2 = SortedList(key=lambda x: (-x[1], x[0]))
            self._mode_pair = lambda num, freq: (num, freq)
            self._mode_val = lambda item: item[0]
        except TypeError:
            self.sl2 = SortedList()
            self._mode_pair = lambda num, freq: (-freq, num)
            self._mode_val = lambda item: item[1]

    def addNumber(self, number: int) -> None:
        """
        Interview explanation:
        Append number to the FIFO stream and refresh order/freq stats.

        Algorithm:
        - Push deque; insert SortedList; bump freq in mode structure; add to sum.

        Complexity: O(log n) with SortedList (O(n) local fallback).
        """
        self.q.append(number)
        self.sl.add(number)
        old = self._mode_pair(number, self.cnt[number])
        self.sl2.discard(old)
        self.cnt[number] += 1
        self.sl2.add(self._mode_pair(number, self.cnt[number]))
        self.s += number

    def removeFirstAddedNumber(self) -> None:
        """
        Interview explanation:
        Remove the earliest added number and keep stats consistent.

        Algorithm:
        - Popleft; erase from SortedList and mode structure; subtract from sum.

        Complexity: O(log n) with SortedList (O(n) local fallback).
        """
        number = self.q.popleft()
        self.sl.remove(number)
        self.sl2.discard(self._mode_pair(number, self.cnt[number]))
        self.cnt[number] -= 1
        if self.cnt[number]:
            self.sl2.add(self._mode_pair(number, self.cnt[number]))
        else:
            del self.cnt[number]
        self.s -= number

    def getMean(self) -> int:
        """
        Interview explanation:
        Floor mean of current numbers.

        Algorithm:
        - Return sum // count.

        Complexity: O(1) time.
        """
        return self.s // len(self.q)

    def getMedian(self) -> int:
        """
        Interview explanation:
        Larger of the two middle values when even count (sorted[n//2]).

        Algorithm:
        - Index into SortedList at n//2.

        Complexity: O(1) / O(log n) depending on SortedList impl.
        """
        return self.sl[len(self.q) // 2]

    def getMode(self) -> int:
        """
        Interview explanation:
        Most frequent value; ties -> smallest value.

        Algorithm:
        - Mode SortedList ordered by (-freq, value); return first.

        Complexity: O(1) time.
        """
        return self._mode_val(self.sl2[0])


# Your StatisticsTracker object will be instantiated and called as such:
# obj = StatisticsTracker()
# obj.addNumber(number)
# obj.removeFirstAddedNumber()
# param_3 = obj.getMean()
# param_4 = obj.getMedian()
# param_5 = obj.getMode()
# @lc code=end
