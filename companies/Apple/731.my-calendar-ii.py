#
# @lc app=leetcode id=731 lang=python3
#
# [731] My Calendar II
#
# https://leetcode.com/problems/my-calendar-ii/description/
#
# algorithms
# Medium (63.39%)
# Likes:    2304
# Dislikes: 190
# Total Accepted:    223K
# Total Submissions: 351K
# Testcase Example:  "[\"MyCalendarTwo\",\"book\",\"book\",\"book\",\"book\",\"book\",\"book\"]"
#
# You are implementing a program to use as your calendar. We can add a new
# event if adding the event will not cause a triple booking.
#
# A triple booking happens when three events have some non-empty intersection
# (i.e., some moment is common to all the three events.).
#
# The event can be represented as a pair of integers startTime and endTime that
# represents a booking on the half-open interval [startTime, endTime), the
# range of real numbers x such that startTime <= x < endTime.
#
# Implement the MyCalendarTwo class:
#
# MyCalendarTwo() Initializes the calendar object.
#
# boolean book(int startTime, int endTime) Returns true if the event can be
# added to the calendar successfully without causing a triple booking.
# Otherwise, return false and do not add the event to the calendar.
#
# Example 1:
#
# Input
# ["MyCalendarTwo", "book", "book", "book", "book", "book", "book"]
# [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]
# Output
# [null, true, true, true, false, true, true]
#
# Explanation
# MyCalendarTwo myCalendarTwo = new MyCalendarTwo();
# myCalendarTwo.book(10, 20); // return True, The event can be booked.
# myCalendarTwo.book(50, 60); // return True, The event can be booked.
# myCalendarTwo.book(10, 40); // return True, The event can be double booked.
# myCalendarTwo.book(5, 15); // return False, The event cannot be booked,
# because it would result in a triple booking.
# myCalendarTwo.book(5, 10); // return True, The event can be booked, as it
# does not use time 10 which is already double booked.
# myCalendarTwo.book(25, 55); // return True, The event can be booked, as the
# time in [25, 40) will be double booked with the third event, the time [40,
# 50) will be single booked, and the time [50, 55) will be double booked with
# the second event.
#
# Constraints:
#
# 0 <= start < end <= 10^9
#
# At most 1000 calls will be made to book.
#


# @lc code=start
class MyCalendarTwo:
    """
    Interview explanation:
    Allow up to double booking. Keep a list of single bookings and a list of
    double-booked intersections. A new event is accepted iff it does not
    overlap any double-booked interval (which would create a triple).
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize empty booking and overlap lists.

        Algorithm:
        - self.booked = []; self.overlaps = []

        Complexity: O(1) init.
        """
        self.booked = []
        self.overlaps = []

    def book(self, startTime: int, endTime: int) -> bool:
        """
        Interview explanation:
        Reject if [start,end) overlaps any existing double-booked region.
        Otherwise, for each single booking that overlaps, record the
        intersection as a new double region, then add the booking.

        Algorithm:
        - For each (os, oe) in overlaps: if max(os,start) < min(oe,end): False
        - For each (bs, be) in booked: if overlap, append intersection to overlaps
        - Append (start,end) to booked; return True

        Complexity: O(n) time per book, O(n) space.
        """
        for os, oe in self.overlaps:
            if max(os, startTime) < min(oe, endTime):
                return False
        for bs, be in self.booked:
            lo, hi = max(bs, startTime), min(be, endTime)
            if lo < hi:
                self.overlaps.append((lo, hi))
        self.booked.append((startTime, endTime))
        return True


# Your MyCalendarTwo object will be instantiated and called as such:
# obj = MyCalendarTwo()
# param_1 = obj.book(startTime,endTime)
# @lc code=end

