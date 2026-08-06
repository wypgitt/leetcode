#
# @lc app=leetcode id=1114 lang=python3
#
# [1114] Print in Order
#
# https://leetcode.com/problems/print-in-order/description/
#
# algorithms
# Easy (73.29%)
# Likes:    1626
# Dislikes: 221
# Total Accepted:    253K
# Total Submissions: 345K
# Testcase Example:  "[1,2,3]"
#
# Suppose we have a class:
#
# public class Foo {
# public void first() { print("first"); }
# public void second() { print("second"); }
# public void third() { print("third"); }
# }
#
# The same instance of Foo will be passed to three different threads. Thread A
# will call first(), thread B will call second(), and thread C will call
# third(). Design a mechanism and modify the program to ensure that second() is
# executed after first(), and third() is executed after second().
#
# Note:
#
# We do not know how the threads will be scheduled in the operating system,
# even though the numbers in the input seem to imply the ordering. The input
# format you see is mainly to ensure our tests' comprehensiveness.
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: "firstsecondthird"
# Explanation: There are three threads being fired asynchronously. The input
# [1,2,3] means thread A calls first(), thread B calls second(), and thread C
# calls third(). "firstsecondthird" is the correct output.
#
# Example 2:
#
# Input: nums = [1,3,2]
# Output: "firstsecondthird"
# Explanation: The input [1,3,2] means thread A calls first(), thread B calls
# third(), and thread C calls second(). "firstsecondthird" is the correct
# output.
#
# Constraints:
#
# nums is a permutation of [1, 2, 3].
#

# @lc code=start
import threading
from typing import Callable


class Foo:
    def __init__(self):
        """
        Interview explanation:
        Three threads call first/second/third; enforce order first→second→third
        with locks (or events/conditions). first releases second; second
        releases third.

        Algorithm:
        - Two locks initially acquired: lock2, lock3.
        - first() prints then unlocks lock2.
        - second() waits lock2, prints, unlocks lock3.
        - third() waits lock3, prints.

        Complexity: O(1) synchronization overhead per call.
        """
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()
        self.lock2.acquire()
        self.lock3.acquire()

    def first(self, printFirst: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Run first action unconditionally, then signal second may proceed.

        Algorithm:
        - printFirst(); release lock2.

        Complexity: O(1).
        """
        printFirst()
        self.lock2.release()

    def second(self, printSecond: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Block until first finished, then print and unblock third.

        Algorithm:
        - acquire lock2; printSecond(); release lock3.

        Complexity: O(1).
        """
        self.lock2.acquire()
        printSecond()
        self.lock3.release()

    def third(self, printThird: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Block until second finished, then print.

        Algorithm:
        - acquire lock3; printThird().

        Complexity: O(1).
        """
        self.lock3.acquire()
        printThird()
# @lc code=end
