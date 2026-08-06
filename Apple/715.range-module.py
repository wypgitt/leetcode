#
# @lc app=leetcode id=715 lang=python3
#
# [715] Range Module
#
# https://leetcode.com/problems/range-module/description/
#
# algorithms
# Hard (45.35%)
# Likes:    1607
# Dislikes: 144
# Total Accepted:    98.0K
# Total Submissions: 216K
# Testcase Example:  "[\"RangeModule\",\"addRange\",\"removeRange\",\"queryRange\",\"queryRange\",\"queryRange\"]"
#
# A Range Module is a module that tracks ranges of numbers. Design a data
# structure to track the ranges represented as half-open intervals and query
# about them.
#
# A half-open interval [left, right) denotes all the real numbers x where left
# <= x < right.
#
# Implement the RangeModule class:
#
# RangeModule() Initializes the object of the data structure.
#
# void addRange(int left, int right) Adds the half-open interval [left, right),
# tracking every real number in that interval. Adding an interval that
# partially overlaps with currently tracked numbers should add any numbers in
# the interval [left, right) that are not already tracked.
#
# boolean queryRange(int left, int right) Returns true if every real number in
# the interval [left, right) is currently being tracked, and false otherwise.
#
# void removeRange(int left, int right) Stops tracking every real number
# currently being tracked in the half-open interval [left, right).
#
# Example 1:
#
# Input
# ["RangeModule", "addRange", "removeRange", "queryRange", "queryRange",
# "queryRange"]
# [[], [10, 20], [14, 16], [10, 14], [13, 15], [16, 17]]
# Output
# [null, null, null, true, false, true]
#
# Explanation
# RangeModule rangeModule = new RangeModule();
# rangeModule.addRange(10, 20);
# rangeModule.removeRange(14, 16);
# rangeModule.queryRange(10, 14); // return True,(Every number in [10, 14) is
# being tracked)
# rangeModule.queryRange(13, 15); // return False,(Numbers like 14, 14.03,
# 14.17 in [13, 15) are not being tracked)
# rangeModule.queryRange(16, 17); // return True, (The number 16 in [16, 17) is
# still being tracked, despite the remove operation)
#
# Constraints:
#
# 1 <= left < right <= 10^9
#
# At most 10^4 calls will be made to addRange, queryRange, and removeRange.
#

# @lc code=start
import bisect


class RangeModule:
    def __init__(self):
        """
        Interview explanation:
        Track disjoint half-open intervals [L,R) as a sorted flat endpoint list
        [l0,r0,l1,r1,...]. Bisect locates overlaps for add/query/remove.

        Algorithm:
        - Empty endpoint list initially.

        Complexity: O(1) init.
        """
        self.track = []

    def addRange(self, left: int, right: int) -> None:
        """
        Interview explanation:
        Merge [left,right) into tracked coverage, coalescing overlaps.

        Algorithm:
        - i = bisect_left(left), j = bisect_right(right).
        - Replace track[i:j] with [left] if i even (start new/open) and [right]
          if j even (close), which merges overlapping intervals cleanly.

        Complexity: O(n) time for list splice, O(log n) to find indices.
        """
        i = bisect.bisect_left(self.track, left)
        j = bisect.bisect_right(self.track, right)
        self.track[i:j] = [left] * (i % 2 == 0) + [right] * (j % 2 == 0)

    def queryRange(self, left: int, right: int) -> bool:
        """
        Interview explanation:
        True iff [left,right) lies entirely inside one covered interval.

        Algorithm:
        - i = bisect_right(left), j = bisect_left(right); covered iff i==j and i odd.

        Complexity: O(log n).
        """
        i = bisect.bisect_right(self.track, left)
        j = bisect.bisect_left(self.track, right)
        return i == j and i % 2 == 1

    def removeRange(self, left: int, right: int) -> None:
        """
        Interview explanation:
        Delete coverage over [left,right), possibly splitting an interval.

        Algorithm:
        - i = bisect_left(left), j = bisect_right(right).
        - Replace track[i:j] with [left] if i odd (close leftover) and [right]
          if j odd (reopen leftover).

        Complexity: O(n) time.
        """
        i = bisect.bisect_left(self.track, left)
        j = bisect.bisect_right(self.track, right)
        self.track[i:j] = [left] * (i % 2 == 1) + [right] * (j % 2 == 1)


# Your RangeModule object will be instantiated and called as such:
# obj = RangeModule()
# obj.addRange(left,right)
# param_2 = obj.queryRange(left,right)
# obj.removeRange(left,right)
# @lc code=end
