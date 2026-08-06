#
# @lc app=leetcode id=1115 lang=python3
#
# [1115] Print FooBar Alternately
#
# https://leetcode.com/problems/print-foobar-alternately/description/
#
# algorithms
# Medium (72.96%)
# Likes:    765
# Dislikes: 60
# Total Accepted:    149K
# Total Submissions: 204K
# Testcase Example:  "1"
#
# Suppose you are given the following code:
#
# class FooBar {
# public void foo() {
# for (int i = 0; i < n; i++) {
# print("foo");
# }
# }
#
# public void bar() {
# for (int i = 0; i < n; i++) {
# print("bar");
# }
# }
# }
#
# The same instance of FooBar will be passed to two different threads:
#
# thread A will call foo(), while
#
# thread B will call bar().
#
# Modify the given program to output "foobar" n times.
#
# Example 1:
#
# Input: n = 1
# Output: "foobar"
# Explanation: There are two threads being fired asynchronously. One of them
# calls foo(), while the other calls bar().
# "foobar" is being output 1 time.
#
# Example 2:
#
# Input: n = 2
# Output: "foobarfoobar"
# Explanation: "foobar" is being output 2 times.
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
import threading
from typing import Callable


class FooBar:
    def __init__(self, n):
        """
        Interview explanation:
        Two threads must print "foo" then "bar" alternately n times. Use two
        locks (or a Condition) so foo and bar take turns.

        Algorithm:
        - foo_ready Lock free; bar_ready Lock held.
        - foo: acquire foo_ready → print → release bar_ready.
        - bar: acquire bar_ready → print → release foo_ready.

        Complexity: O(n) synchronization steps.
        """
        self.n = n
        self.foo_ready = threading.Lock()
        self.bar_ready = threading.Lock()
        self.bar_ready.acquire()

    def foo(self, printFoo: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Print "foo" when it is foo's turn; then hand turn to bar.

        Algorithm:
        - For _ in range(n): acquire foo_ready; printFoo(); release bar_ready.

        Complexity: O(n).
        """
        for _ in range(self.n):
            self.foo_ready.acquire()
            printFoo()
            self.bar_ready.release()

    def bar(self, printBar: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Print "bar" after foo; hand turn back to foo.

        Algorithm:
        - For _ in range(n): acquire bar_ready; printBar(); release foo_ready.

        Complexity: O(n).
        """
        for _ in range(self.n):
            self.bar_ready.acquire()
            printBar()
            self.foo_ready.release()
# @lc code=end
