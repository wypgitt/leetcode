#
# @lc app=leetcode id=352 lang=python3
#
# [352] Data Stream as Disjoint Intervals
#
# https://leetcode.com/problems/data-stream-as-disjoint-intervals/description/
#
# algorithms
# Hard (60.44%)
# Likes:    1828
# Dislikes: 378
# Total Accepted:    141K
# Total Submissions: 233K
# Testcase Example:  "[\"SummaryRanges\",\"addNum\",\"getIntervals\",\"addNum\",\"getIntervals\",\"addNum\",\"getIntervals\",\"addNum\",\"getIntervals\",\"addNum\",\"getIntervals\"]"
#
# Given a data stream input of non-negative integers a_1, a_2, ..., a_n,
# summarize the numbers seen so far as a list of disjoint intervals.
#
# Implement the SummaryRanges class:
#
# SummaryRanges() Initializes the object with an empty stream.
#
# void addNum(int value) Adds the integer value to the stream.
#
# int[][] getIntervals() Returns a summary of the integers in the stream
# currently as a list of disjoint intervals [start_i, end_i]. The answer should
# be sorted by start_i.
#
# Example 1:
#
# Input
# ["SummaryRanges", "addNum", "getIntervals", "addNum", "getIntervals",
# "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals"]
# [[], [1], [], [3], [], [7], [], [2], [], [6], []]
# Output
# [null, null, [[1, 1]], null, [[1, 1], [3, 3]], null, [[1, 1], [3, 3], [7,
# 7]], null, [[1, 3], [7, 7]], null, [[1, 3], [6, 7]]]
#
# Explanation
# SummaryRanges summaryRanges = new SummaryRanges();
# summaryRanges.addNum(1); // arr = [1]
# summaryRanges.getIntervals(); // return [[1, 1]]
# summaryRanges.addNum(3); // arr = [1, 3]
# summaryRanges.getIntervals(); // return [[1, 1], [3, 3]]
# summaryRanges.addNum(7); // arr = [1, 3, 7]
# summaryRanges.getIntervals(); // return [[1, 1], [3, 3], [7, 7]]
# summaryRanges.addNum(2); // arr = [1, 2, 3, 7]
# summaryRanges.getIntervals(); // return [[1, 3], [7, 7]]
# summaryRanges.addNum(6); // arr = [1, 2, 3, 6, 7]
# summaryRanges.getIntervals(); // return [[1, 3], [6, 7]]
#
# Constraints:
#
# 0 <= value <= 10^4
#
# At most 3 * 10^4 calls will be made to addNum and getIntervals.
#
# At most 10^2 calls will be made to getIntervals.
#
# Follow up: What if there are lots of merges and the number of disjoint
# intervals is small compared to the size of the data stream?
#

# @lc code=start
import bisect
from typing import List


class SummaryRanges:
    """
    Interview explanation:
    Maintain sorted disjoint intervals. On addNum, binary-search neighbors and
    merge left and/or right when value is adjacent or already covered.

    Algorithm:
    - Sorted list of [start, end].
    - Find last interval with start <= value; check cover / merge left / right.
    - getIntervals returns the list.

    Complexity: O(n) add worst-case (list insert), O(n) get; O(n) space.
    TreeMap variant is O(log n) add with the same merge cases.
    """

    def __init__(self):
        """
        Interview explanation:
        Sorted list of disjoint [start, end] intervals summarizing the stream.

        Algorithm:
        - intervals starts empty; addNum maintains sorted disjointness.

        Complexity: O(1) init, O(n) space for n intervals.
        """
        self.intervals: List[List[int]] = []

    def addNum(self, value: int) -> None:
        """
        Interview explanation:
        Binary-search neighboring intervals and merge when value is covered or
        adjacent on the left and/or right.

        Algorithm:
        - Find last interval with start <= value; if covered, return.
        - Merge left, right, both, or insert a singleton [value, value].

        Complexity: O(n) time worst-case (list insert), O(1) extra space.
        """
        iv = self.intervals
        i = bisect.bisect_right(iv, [value, float("inf")]) - 1
        left = iv[i] if i >= 0 else None
        right = iv[i + 1] if i + 1 < len(iv) else None

        if left and left[0] <= value <= left[1]:
            return

        merge_left = left is not None and left[1] + 1 == value
        merge_right = right is not None and right[0] - 1 == value

        if merge_left and merge_right:
            left[1] = right[1]
            del iv[i + 1]
        elif merge_left:
            left[1] = value
        elif merge_right:
            right[0] = value
        else:
            iv.insert(i + 1, [value, value])

    def getIntervals(self) -> List[List[int]]:
        """
        Interview explanation:
        Return the current sorted disjoint summary (already maintained).

        Algorithm:
        - Return intervals.

        Complexity: O(1) time (return reference), O(n) if a copy is required.
        """
        return self.intervals


# Your SummaryRanges object will be instantiated and called as such:
# obj = SummaryRanges()
# obj.addNum(value)
# param_2 = obj.getIntervals()
# @lc code=end
