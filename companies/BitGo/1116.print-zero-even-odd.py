#
# @lc app=leetcode id=1116 lang=python3
#
# [1116] Print Zero Even Odd
#
# https://leetcode.com/problems/print-zero-even-odd/description/
#
# algorithms
# Medium (65.99%)
# Likes:    567
# Dislikes: 379
# Total Accepted:    91.3K
# Total Submissions: 138K
# Testcase Example:  "2"
#
# You have a function printNumber that can be called with an integer parameter
# and prints it to the console.
#
# For example, calling printNumber(7) prints 7 to the console.
#
# You are given an instance of the class ZeroEvenOdd that has three functions:
# zero, even, and odd. The same instance of ZeroEvenOdd will be passed to three
# different threads:
#
# Thread A: calls zero() that should only output 0's.
#
# Thread B: calls even() that should only output even numbers.
#
# Thread C: calls odd() that should only output odd numbers.
#
# Modify the given class to output the series "010203040506..." where the
# length of the series must be 2n.
#
# Implement the ZeroEvenOdd class:
#
# ZeroEvenOdd(int n) Initializes the object with the number n that represents
# the numbers that should be printed.
#
# void zero(printNumber) Calls printNumber to output one zero.
#
# void even(printNumber) Calls printNumber to output one even number.
#
# void odd(printNumber) Calls printNumber to output one odd number.
#
# Example 1:
#
# Input: n = 2
# Output: "0102"
# Explanation: There are three threads being fired asynchronously.
# One of them calls zero(), the other calls even(), and the last one calls
# odd().
# "0102" is the correct output.
#
# Example 2:
#
# Input: n = 5
# Output: "0102030405"
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
import threading
from typing import Callable


class ZeroEvenOdd:
    def __init__(self, n):
        """
        Interview explanation:
        Three threads print 0, odd, even interleaved as 010203...2n.
        Use a Condition (or three locks) and a state: next to print is zero,
        then odd or even depending on the number.

        Algorithm:
        - Condition + state in {"zero","odd","even"}; num from 1..n.
        - zero prints 0 then signals odd/even; odd/even print i then signal zero.

        Complexity: O(n) synchronization steps.
        """
        self.n = n
        self.cond = threading.Condition()
        self.state = "zero"
        self.num = 1

    def zero(self, printNumber: "Callable[[int], None]") -> None:
        """
        Interview explanation:
        Print 0 before each of 1..n, alternating who goes next (odd then even).

        Algorithm:
        - Loop n times under Condition: wait until state=="zero"; print 0;
          set state to odd/even by parity of num; notify_all.

        Complexity: O(n).
        """
        for _ in range(self.n):
            with self.cond:
                while self.state != "zero":
                    self.cond.wait()
                printNumber(0)
                self.state = "odd" if self.num % 2 == 1 else "even"
                self.cond.notify_all()

    def even(self, printNumber: "Callable[[int], None]") -> None:
        """
        Interview explanation:
        Print even numbers 2,4,...,n when signaled after a zero.

        Algorithm:
        - For each even i: wait state=="even"; print i; state="zero"; num++.

        Complexity: O(n).
        """
        for i in range(2, self.n + 1, 2):
            with self.cond:
                while self.state != "even":
                    self.cond.wait()
                printNumber(i)
                self.num += 1
                self.state = "zero"
                self.cond.notify_all()

    def odd(self, printNumber: "Callable[[int], None]") -> None:
        """
        Interview explanation:
        Print odd numbers 1,3,...,n when signaled after a zero.

        Algorithm:
        - For each odd i: wait state=="odd"; print i; state="zero"; num++.

        Complexity: O(n).
        """
        for i in range(1, self.n + 1, 2):
            with self.cond:
                while self.state != "odd":
                    self.cond.wait()
                printNumber(i)
                self.num += 1
                self.state = "zero"
                self.cond.notify_all()
# @lc code=end
