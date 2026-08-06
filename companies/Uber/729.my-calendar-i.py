#
# @lc app=leetcode id=729 lang=python3
#
# [729] My Calendar I
#
# https://leetcode.com/problems/my-calendar-i/description/
#
# algorithms
# Medium (58.36%)
# Likes:    4845
# Dislikes: 143
# Total Accepted:    470K
# Total Submissions: 805K
# Testcase Example:  "[\"MyCalendar\",\"book\",\"book\",\"book\"]"
#
# You are implementing a program to use as your calendar. We can add a new
# event if adding the event will not cause a double booking.
#
# A double booking happens when two events have some non-empty intersection
# (i.e., some moment is common to both events.).
#
# The event can be represented as a pair of integers startTime and endTime that
# represents a booking on the half-open interval [startTime, endTime), the
# range of real numbers x such that startTime <= x < endTime.
#
# Implement the MyCalendar class:
#
# MyCalendar() Initializes the calendar object.
#
# boolean book(int startTime, int endTime) Returns true if the event can be
# added to the calendar successfully without causing a double booking.
# Otherwise, return false and do not add the event to the calendar.
#
# Example 1:
#
# Input
# ["MyCalendar", "book", "book", "book"]
# [[], [10, 20], [15, 25], [20, 30]]
# Output
# [null, true, false, true]
#
# Explanation
# MyCalendar myCalendar = new MyCalendar();
# myCalendar.book(10, 20); // return True
# myCalendar.book(15, 25); // return False, It can not be booked because time
# 15 is already booked by another event.
# myCalendar.book(20, 30); // return True, The event can be booked, as the
# first event takes every time less than 20, but not including 20.
#
# Constraints:
#
# 0 <= start < end <= 10^9
#
# At most 1000 calls will be made to book.
#


# @lc code=start
import bisect


class MyCalendar:
    """
    Interview explanation:
    Store booked [start, end) intervals sorted by start. A new booking is valid
    iff it does not overlap any existing interval (end_i <= start or end <= start_i).
    Binary search finds the insertion neighbor to check in O(log n).
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize an empty sorted list of booked intervals.

        Algorithm:
        - self.books = [] of (start, end)

        Complexity: O(1) time, O(1) space initially.
        """
        self.books = []

    def book(self, startTime: int, endTime: int) -> bool:
        """
        Interview explanation:
        Binary-search the first interval with start >= startTime; check overlap
        with that interval and the previous one. If clear, insert.

        Algorithm:
        - i = bisect_left by start
        - If i > 0 and books[i-1].end > startTime: conflict
        - If i < n and books[i].start < endTime: conflict
        - Else insert (startTime, endTime) at i; return True

        Complexity: O(n) time due to list insert (O(log n) search); O(n) space.
        """
        i = bisect.bisect_left(self.books, (startTime, endTime))
        if i > 0 and self.books[i - 1][1] > startTime:
            return False
        if i < len(self.books) and self.books[i][0] < endTime:
            return False
        self.books.insert(i, (startTime, endTime))
        return True


# Your MyCalendar object will be instantiated and called as such:
# obj = MyCalendar()
# param_1 = obj.book(startTime,endTime)
# @lc code=end

