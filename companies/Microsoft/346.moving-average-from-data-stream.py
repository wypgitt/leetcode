#
# @lc app=leetcode id=346 lang=python3
#
# [346] Moving Average from Data Stream
#
# https://leetcode.com/problems/moving-average-from-data-stream/description/
#
# algorithms
# Easy (80.22%)
# Likes:    1757
# Dislikes: 194
# Total Accepted:    538.5K
# Total Submissions: 671.3K
# Testcase Example:  "[\"MovingAverage\",\"next\",\"next\",\"next\",\"next\"]\n[[3],[1],[10],[3],[5]]"
#
#
# Given a stream of integers and a window size, calculate the moving
# average of all integers in the sliding window.
#
# Implement the MovingAverage class:
#
# MovingAverage(int size) Initializes the object with the size of the
# window size.
#
# double next(int val) Returns the moving average of the last size values
# of the stream.
#
# Example 1:
#
# Input
# ["MovingAverage", "next", "next", "next", "next"]
# [[3], [1], [10], [3], [5]]
# Output
# [null, 1.0, 5.5, 4.66667, 6.0]
#
# Explanation
# MovingAverage movingAverage = new MovingAverage(3);
# movingAverage.next(1); // return 1.0 = 1 / 1
# movingAverage.next(10); // return 5.5 = (1 + 10) / 2
# movingAverage.next(3); // return 4.66667 = (1 + 10 + 3) / 3
# movingAverage.next(5); // return 6.0 = (10 + 3 + 5) / 3
#
# Constraints:
#
# 1 <= size <= 1000
#
# -10^5 <= val <= 10^5
#
# At most 10^4 calls will be made to next.
#
# @lc code=start
from collections import deque


class MovingAverage:
    """
    Interview explanation:
    Sliding-window queue of size at most `size`. Keep running sum; on overflow
    dequeue oldest and subtract. next returns sum / current length.

    Algorithm:
    - __init__(size): empty deque, sum=0.
    - next(val): append; if len > size popleft and subtract; return avg.

    Complexity: O(1) per next, O(size) space.
    """

    def __init__(self, size: int):
        """
        Interview explanation:
        Fixed-capacity sliding window with a running sum for O(1) averages.

        Algorithm:
        - Store window size, empty deque, and total = 0.

        Complexity: O(1) init, O(size) space over the lifetime.
        """
        self.size = size
        self.q = deque()
        self.total = 0

    def next(self, val: int) -> float:
        """
        Interview explanation:
        Append val; if the window overflows, drop the oldest and subtract it
        from the running sum; return average of the current window.

        Algorithm:
        - append/add; if len > size: total -= popleft(); return total / len.

        Complexity: O(1) time, O(1) extra space.
        """
        self.q.append(val)
        self.total += val
        if len(self.q) > self.size:
            self.total -= self.q.popleft()
        return self.total / len(self.q)


# Your MovingAverage object will be instantiated and called as such:
# obj = MovingAverage(size)
# param_1 = obj.next(val)
# @lc code=end
