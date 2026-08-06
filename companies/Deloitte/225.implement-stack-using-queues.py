#
# @lc app=leetcode id=225 lang=python3
#
# [225] Implement Stack using Queues
#
# https://leetcode.com/problems/implement-stack-using-queues/description/
#
# algorithms
# Easy (70.56%)
# Likes:    7061
# Dislikes: 1292
# Total Accepted:    1.2M
# Total Submissions: 1.8M
# Testcase Example:  "[\"MyStack\",\"push\",\"push\",\"top\",\"pop\",\"empty\"]"
#
# Implement a last-in-first-out (LIFO) stack using only two queues. The
# implemented stack should support all the functions of a normal stack (push,
# top, pop, and empty).
#
# Implement the MyStack class:
#
# void push(int x) Pushes element x to the top of the stack.
#
# int pop() Removes the element on the top of the stack and returns it.
#
# int top() Returns the element on the top of the stack.
#
# boolean empty() Returns true if the stack is empty, false otherwise.
#
# Notes:
#
# You must use only standard operations of a queue, which means that only push
# to back, peek/pop from front, size and is empty operations are valid.
#
# Depending on your language, the queue may not be supported natively. You may
# simulate a queue using a list or deque (double-ended queue) as long as you
# use only a queue's standard operations.
#
# Example 1:
#
# Input
# ["MyStack", "push", "push", "top", "pop", "empty"]
# [[], [1], [2], [], [], []]
# Output
# [null, null, null, 2, 2, false]
#
# Explanation
# MyStack myStack = new MyStack();
# myStack.push(1);
# myStack.push(2);
# myStack.top(); // return 2
# myStack.pop(); // return 2
# myStack.empty(); // return False
#
# Constraints:
#
# 1 <= x <= 9
#
# At most 100 calls will be made to push, pop, top, and empty.
#
# All the calls to pop and top are valid.
#
# Follow-up: Can you implement the stack using only one queue?
#

# @lc code=start
from collections import deque


class MyStack:
    """
    Interview explanation:
    Simulate a stack with one queue: on push, enqueue then rotate so the newest
    element sits at the front. pop/top/empty are then O(1) queue ops.

    Algorithm:
    - push(x): append x; rotate len-1 times (move front to back).
    - pop/top: dequeue / peek front.
    - empty: queue empty.

    Complexity: push O(n), pop/top/empty O(1); O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        One queue stores stack elements with the top always at the front.

        Algorithm:
        - q = empty deque; push maintains front = newest.

        Complexity: O(1) init, O(n) space for n elements.
        """
        self.q = deque()

    def push(self, x: int) -> None:
        """
        Interview explanation:
        Enqueue x then rotate older elements behind it so x becomes the front
        (stack top).

        Algorithm:
        - append x; for len-1 times: append(popleft()).

        Complexity: O(n) time, O(1) extra space.
        """
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())

    def pop(self) -> int:
        """
        Interview explanation:
        Front of the queue is the stack top after push rotations.

        Algorithm:
        - Return popleft().

        Complexity: O(1) time, O(1) space.
        """
        return self.q.popleft()

    def top(self) -> int:
        """
        Interview explanation:
        Peek the queue front without removing — that is the stack top.

        Algorithm:
        - Return q[0].

        Complexity: O(1) time, O(1) space.
        """
        return self.q[0]

    def empty(self) -> bool:
        """
        Interview explanation:
        Stack is empty iff the underlying queue is empty.

        Algorithm:
        - Return not q.

        Complexity: O(1) time, O(1) space.
        """
        return not self.q


# Your MyStack object will be instantiated and called as such:
# obj = MyStack()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.top()
# param_4 = obj.empty()
# @lc code=end
