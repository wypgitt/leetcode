#
# @lc app=leetcode id=2276 lang=python3
#
# [2276] Count Integers in Intervals
#
# https://leetcode.com/problems/count-integers-in-intervals/description/
#
# algorithms
# Hard (36.12%)
# Likes:    629
# Dislikes: 64
# Total Accepted:    30.4K
# Total Submissions: 84.1K
# Testcase Example:  "[\"CountIntervals\",\"add\",\"add\",\"count\",\"add\",\"count\"]\n[[],[2,3],[7,10],[],[5,8],[]]"
#
# Given an empty set of intervals, implement a data structure that can:
#
#
# Add an interval to the set of intervals.
#
#
# Count the number of integers that are present in at least one interval.
#
# Implement the CountIntervals class:
#
#
# CountIntervals() Initializes the object with an empty set of intervals.
#
#
# void add(int left, int right) Adds the interval [left, right] to the set of
# intervals.
#
#
# int count() Returns the number of integers that are present in at least one
# interval.
#
# Note that an interval [left, right] denotes all the integers x where left <= x
# <= right.
#
#
#
# Example 1:
#
# Input
# ["CountIntervals", "add", "add", "count", "add", "count"]
# [[], [2, 3], [7, 10], [], [5, 8], []]
# Output
# [null, null, null, 6, null, 8]
#
# Explanation
# CountIntervals countIntervals = new CountIntervals(); // initialize the object
# with an empty set of intervals.
# countIntervals.add(2, 3);  // add [2, 3] to the set of intervals.
# countIntervals.add(7, 10); // add [7, 10] to the set of intervals.
# countIntervals.count();    // return 6
#                            // the integers 2 and 3 are present in the interval
# [2, 3].
#                            // the integers 7, 8, 9, and 10 are present in the
# interval [7, 10].
# countIntervals.add(5, 8);  // add [5, 8] to the set of intervals.
# countIntervals.count();    // return 8
#                            // the integers 2 and 3 are present in the interval
# [2, 3].
#                            // the integers 5 and 6 are present in the interval
# [5, 8].
#                            // the integers 7 and 8 are present in the
# intervals [5, 8] and [7, 10].
#                            // the integers 9 and 10 are present in the
# interval [7, 10].
#
#
#
# Constraints:
#
#
# 1 <= left <= right <= 10^9
#
#
# At most 10^5 calls in total will be made to add and count.
#
#
# At least one call will be made to count.
#

# @lc code=start
import bisect
from typing import List


class CountIntervals:
    def __init__(self):
        """
        Interview explanation:
        Maintain union of integer intervals; support add and count of covered ints.

        Algorithm:
        - Sorted list of non-overlapping [L,R]; merge on add; track covered count.

        Complexity: O(n) space for n adds.
        """
        self.intervals: List[List[int]] = []
        self.covered = 0

    def add(self, left: int, right: int) -> None:
        """
        Interview explanation:
        Add [left, right] into the union, merging overlaps/adjacents.

        Algorithm:
        - Find merge range via bisect; subtract old lengths; insert merged.

        Complexity: O(n) time worst-case, O(log n) locate.
        """
        intervals = self.intervals
        i = bisect.bisect_left(intervals, [left, left])
        if i > 0 and intervals[i - 1][1] >= left - 1:
            i -= 1
        j = i
        ml, mr = left, right
        while j < len(intervals) and intervals[j][0] <= right + 1:
            ml = min(ml, intervals[j][0])
            mr = max(mr, intervals[j][1])
            self.covered -= intervals[j][1] - intervals[j][0] + 1
            j += 1
        self.covered += mr - ml + 1
        intervals[i:j] = [[ml, mr]]

    def count(self) -> int:
        """
        Interview explanation:
        Return number of distinct integers covered by any interval.

        Algorithm:
        - Return maintained covered counter.

        Complexity: O(1).
        """
        return self.covered


# Your CountIntervals object will be instantiated and called as such:
# obj = CountIntervals()
# obj.add(left,right)
# param_2 = obj.count()
# @lc code=end
