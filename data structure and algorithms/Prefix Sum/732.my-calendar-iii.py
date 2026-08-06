#
# @lc app=leetcode id=732 lang=python3
#
# [732] My Calendar III
#
# https://leetcode.com/problems/my-calendar-iii/description/
#
# algorithms
# Hard (72.07%)
# Likes:    2107
# Dislikes: 277
# Total Accepted:    117K
# Total Submissions: 162K
# Testcase Example:  "[\"MyCalendarThree\",\"book\",\"book\",\"book\",\"book\",\"book\",\"book\"]"
#
# A k-booking happens when k events have some non-empty intersection (i.e.,
# there is some time that is common to all k events.)
#
# You are given some events [startTime, endTime), after each given event,
# return an integer k representing the maximum k-booking between all the
# previous events.
#
# Implement the MyCalendarThree class:
#
# MyCalendarThree() Initializes the object.
#
# int book(int startTime, int endTime) Returns an integer k representing the
# largest integer such that there exists a k-booking in the calendar.
#
# Example 1:
#
# Input
# ["MyCalendarThree", "book", "book", "book", "book", "book", "book"]
# [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]
# Output
# [null, 1, 1, 2, 3, 3, 3]
#
# Explanation
# MyCalendarThree myCalendarThree = new MyCalendarThree();
# myCalendarThree.book(10, 20); // return 1
# myCalendarThree.book(50, 60); // return 1
# myCalendarThree.book(10, 40); // return 2
# myCalendarThree.book(5, 15); // return 3
# myCalendarThree.book(5, 10); // return 3
# myCalendarThree.book(25, 55); // return 3
#
# Constraints:
#
# 0 <= startTime < endTime <= 10^9
#
# At most 400 calls will be made to book.
#



# @lc code=start
class MyCalendarThree:
    """
    Interview explanation:
    Sweep-line difference map: +1 at start, -1 at end. After each booking, scan
    times in sorted order; the maximum running sum is the current k-booking.
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize an empty difference dictionary time -> delta.

        Algorithm:
        - self.diff = {}

        Complexity: O(1) init.
        """
        self.diff = {}

    def book(self, startTime: int, endTime: int) -> int:
        """
        Interview explanation:
        Record the event endpoints, then sweep to find peak concurrency.

        Algorithm:
        - diff[start] += 1; diff[end] -= 1
        - cur = ans = 0; for t in sorted(diff): cur += diff[t]; ans = max(ans, cur)
        - Return ans

        Complexity: O(n log n) time per book (sort keys), O(n) space.
        """
        self.diff[startTime] = self.diff.get(startTime, 0) + 1
        self.diff[endTime] = self.diff.get(endTime, 0) - 1
        cur = ans = 0
        for t in sorted(self.diff):
            cur += self.diff[t]
            if cur > ans:
                ans = cur
        return ans


# Your MyCalendarThree object will be instantiated and called as such:
# obj = MyCalendarThree()
# param_1 = obj.book(startTime,endTime)
# @lc code=end


