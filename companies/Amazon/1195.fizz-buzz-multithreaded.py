#
# @lc app=leetcode id=1195 lang=python3
#
# [1195] Fizz Buzz Multithreaded
#
# https://leetcode.com/problems/fizz-buzz-multithreaded/description/
#
# algorithms
# Medium (75.02%)
# Likes:    692
# Dislikes: 445
# Total Accepted:    82.3K
# Total Submissions: 110K
# Testcase Example:  "15"
#
# You have the four functions:
#
# printFizz that prints the word "fizz" to the console,
#
# printBuzz that prints the word "buzz" to the console,
#
# printFizzBuzz that prints the word "fizzbuzz" to the console, and
#
# printNumber that prints a given integer to the console.
#
# You are given an instance of the class FizzBuzz that has four functions:
# fizz, buzz, fizzbuzz and number. The same instance of FizzBuzz will be passed
# to four different threads:
#
# Thread A: calls fizz() that should output the word "fizz".
#
# Thread B: calls buzz() that should output the word "buzz".
#
# Thread C: calls fizzbuzz() that should output the word "fizzbuzz".
#
# Thread D: calls number() that should only output the integers.
#
# Modify the given class to output the series [1, 2, "fizz", 4, "buzz", ...]
# where the i^th token (1-indexed) of the series is:
#
# "fizzbuzz" if i is divisible by 3 and 5,
#
# "fizz" if i is divisible by 3 and not 5,
#
# "buzz" if i is divisible by 5 and not 3, or
#
# i if i is not divisible by 3 or 5.
#
# Implement the FizzBuzz class:
#
# FizzBuzz(int n) Initializes the object with the number n that represents the
# length of the sequence that should be printed.
#
# void fizz(printFizz) Calls printFizz to output "fizz".
#
# void buzz(printBuzz) Calls printBuzz to output "buzz".
#
# void fizzbuzz(printFizzBuzz) Calls printFizzBuzz to output "fizzbuzz".
#
# void number(printNumber) Calls printnumber to output the numbers.
#
# Example 1:
#
# Input: n = 15
# Output:
# [1,2,"fizz",4,"buzz","fizz",7,8,"fizz","buzz",11,"fizz",13,14,"fizzbuzz"]
#
# Example 2:
#
# Input: n = 5
# Output: [1,2,"fizz",4,"buzz"]
#
# Constraints:
#
# 1 <= n <= 50
#

# @lc code=start

import threading
from typing import Callable


class FizzBuzz:
    def __init__(self, n: int):
        """
        Interview explanation:
        Four threads print the FizzBuzz sequence up to n. Share a counter and
        Condition so each thread waits until it is its turn for the current i.

        Algorithm:
        - self.n = n; self.i = 1; lock + Condition.

        Complexity: O(1) init.
        """
        self.n = n
        self.i = 1
        self.cv = threading.Condition()

    def fizz(self, printFizz: Callable[[], None]) -> None:
        """
        Interview explanation:
        Print "fizz" when i divisible by 3 but not 5; advance i and notify.

        Algorithm:
        - Loop with cv: wait until i>n or (i%3==0 and i%5!=0); if done return;
          printFizz(); i++; notify_all.

        Complexity: O(n) waits total across threads.
        """
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 3 == 0 and self.i % 5 != 0):
                    self.cv.wait()
                if self.i > self.n:
                    return
                printFizz()
                self.i += 1
                self.cv.notify_all()

    def buzz(self, printBuzz: Callable[[], None]) -> None:
        """
        Interview explanation:
        Print "buzz" when i divisible by 5 but not 3; advance i and notify.

        Algorithm:
        - Same Condition pattern for i%5==0 and i%3!=0.

        Complexity: O(n) waits total across threads.
        """
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 5 == 0 and self.i % 3 != 0):
                    self.cv.wait()
                if self.i > self.n:
                    return
                printBuzz()
                self.i += 1
                self.cv.notify_all()

    def fizzbuzz(self, printFizzBuzz: Callable[[], None]) -> None:
        """
        Interview explanation:
        Print "fizzbuzz" when i divisible by both 3 and 5; advance and notify.

        Algorithm:
        - Wait for i%15==0; print; i++; notify_all.

        Complexity: O(n) waits total across threads.
        """
        while True:
            with self.cv:
                while self.i <= self.n and self.i % 15 != 0:
                    self.cv.wait()
                if self.i > self.n:
                    return
                printFizzBuzz()
                self.i += 1
                self.cv.notify_all()

    def number(self, printNumber: Callable[[int], None]) -> None:
        """
        Interview explanation:
        Print i when not divisible by 3 or 5; advance and notify.

        Algorithm:
        - Wait for i%3!=0 and i%5!=0; printNumber(i); i++; notify_all.

        Complexity: O(n) waits total across threads.
        """
        while True:
            with self.cv:
                while self.i <= self.n and (self.i % 3 == 0 or self.i % 5 == 0):
                    self.cv.wait()
                if self.i > self.n:
                    return
                printNumber(self.i)
                self.i += 1
                self.cv.notify_all()
# @lc code=end
