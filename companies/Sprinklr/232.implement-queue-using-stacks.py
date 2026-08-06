#
# @lc app=leetcode id=232 lang=python3
#
# [232] Implement Queue using Stacks
#
# https://leetcode.com/problems/implement-queue-using-stacks/description/
#
# algorithms
# Easy (70.22%)
# Likes:    8742
# Dislikes: 497
# Total Accepted:    1.6M
# Total Submissions: 2.3M
# Testcase Example:  "[\"MyQueue\",\"push\",\"push\",\"peek\",\"pop\",\"empty\"]"
#
# Implement a first in first out (FIFO) queue using only two stacks. The
# implemented queue should support all the functions of a normal queue (push,
# peek, pop, and empty).
#
# Implement the MyQueue class:
#
# void push(int x) Pushes element x to the back of the queue.
#
# int pop() Removes the element from the front of the queue and returns it.
#
# int peek() Returns the element at the front of the queue.
#
# boolean empty() Returns true if the queue is empty, false otherwise.
#
# Notes:
#
# You must use only standard operations of a stack, which means only push to
# top, peek/pop from top, size, and is empty operations are valid.
#
# Depending on your language, the stack may not be supported natively. You may
# simulate a stack using a list or deque (double-ended queue) as long as you
# use only a stack's standard operations.
#
# Example 1:
#
# Input
# ["MyQueue", "push", "push", "peek", "pop", "empty"]
# [[], [1], [2], [], [], []]
# Output
# [null, null, null, 1, 1, false]
#
# Explanation
# MyQueue myQueue = new MyQueue();
# myQueue.push(1); // queue is: [1]
# myQueue.push(2); // queue is: [1, 2] (leftmost is front of the queue)
# myQueue.peek(); // return 1
# myQueue.pop(); // return 1, queue is [2]
# myQueue.empty(); // return false
#
# Constraints:
#
# 1 <= x <= 9
#
# At most 100 calls will be made to push, pop, peek, and empty.
#
# All the calls to pop and peek are valid.
#
# Follow-up: Can you implement the queue such that each operation is amortized
# O(1) time complexity? In other words, performing n operations will take
# overall O(n) time even if one of those operations may take longer.
#

# @lc code=start
class MyQueue:
    """
    Interview explanation:
    Two stacks: inbound for push, outbound for pop/peek. Lazy transfer from
    inbound to outbound only when outbound is empty — amortized O(1) per op.

    Algorithm:
        - push: append to inbound.
        - pop/peek: if outbound empty, pour inbound into outbound; then pop/peek outbound.
        - empty: both stacks empty.

    Complexity: Amortized O(1) per operation, O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Two stacks split input and output; lazy transfer yields amortized O(1)
        queue operations.

        Algorithm:
        - inbound collects pushes; outbound serves pop/peek after a pour.

        Complexity: O(1) init, O(n) space for n elements.
        """
        self.inbound = []
        self.outbound = []

    def push(self, x: int) -> None:
        """
        Interview explanation:
        Always push onto the inbound stack; order is reversed later on transfer.

        Algorithm:
        - inbound.append(x).

        Complexity: O(1) time, O(1) amortized space.
        """
        self.inbound.append(x)

    def _move(self) -> None:
        if not self.outbound:
            while self.inbound:
                self.outbound.append(self.inbound.pop())

    def pop(self) -> int:
        """
        Interview explanation:
        Ensure outbound has the queue front on top, then pop it.

        Algorithm:
        - If outbound empty, pour inbound → outbound; return outbound.pop().

        Complexity: Amortized O(1) time, O(1) space.
        """
        self._move()
        return self.outbound.pop()

    def peek(self) -> int:
        """
        Interview explanation:
        Same lazy transfer as pop, but only read the outbound top.

        Algorithm:
        - _move(); return outbound[-1].

        Complexity: Amortized O(1) time, O(1) space.
        """
        self._move()
        return self.outbound[-1]

    def empty(self) -> bool:
        """
        Interview explanation:
        Queue is empty only when both stacks hold nothing.

        Algorithm:
        - Return not inbound and not outbound.

        Complexity: O(1) time, O(1) space.
        """
        return not self.inbound and not self.outbound


# Your MyQueue object will be instantiated and called as such:
# obj = MyQueue()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.peek()
# param_4 = obj.empty()
# @lc code=end
