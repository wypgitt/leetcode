#
# @lc app=leetcode id=716 lang=python3
#
# [716] Max Stack
#
# https://leetcode.com/problems/max-stack/description/
#
# algorithms
# Hard (45.99%)
# Likes:    2022
# Dislikes: 514
# Total Accepted:    187K
# Total Submissions: 406.6K
# Testcase Example:  "[\"MaxStack\",\"push\",\"push\",\"push\",\"top\",\"popMax\",\"top\",\"peekMax\",\"pop\",\"top\"]\n[[],[5],[1],[5],[],[],[],[],[],[]]"
#
#
# Design a max stack data structure that supports the stack operations and
# supports finding the stack's maximum element.
#
# Implement the MaxStack class:
#
# MaxStack() Initializes the stack object.
#
# void push(int x) Pushes element x onto the stack.
#
# int pop() Removes the element on top of the stack and returns it.
#
# int top() Gets the element on the top of the stack without removing it.
#
# int peekMax() Retrieves the maximum element in the stack without
# removing it.
#
# int popMax() Retrieves the maximum element in the stack and removes it.
# If there is more than one maximum element, only remove the top-most one.
#
# You must come up with a solution that supports O(1) for each top call
# and O(logn) for each other call.
#
# Example 1:
#
# Input
# ["MaxStack", "push", "push", "push", "top", "popMax", "top", "peekMax",
# "pop", "top"]
# [[], [5], [1], [5], [], [], [], [], [], []]
# Output
# [null, null, null, null, 5, 5, 1, 5, 1, 5]
#
# Explanation
# MaxStack stk = new MaxStack();
# stk.push(5);   // [5] the top of the stack and the maximum number is 5.
# stk.push(1);   // [5, 1] the top of the stack is 1, but the maximum is
# 5.
# stk.push(5);   // [5, 1, 5] the top of the stack is 5, which is also the
# maximum, because it is the top most one.
# stk.top();     // return 5, [5, 1, 5] the stack did not change.
# stk.popMax();  // return 5, [5, 1] the stack is changed now, and the top
# is different from the max.
# stk.top();     // return 1, [5, 1] the stack did not change.
# stk.peekMax(); // return 5, [5, 1] the stack did not change.
# stk.pop();     // return 1, [5] the top of the stack and the max element
# is now 5.
# stk.top();     // return 5, [5] the stack did not change.
#
# Constraints:
#
# -10^7 <= x <= 10^7
#
# At most 10^5 calls will be made to push, pop, top, peekMax, and popMax.
#
# There will be at least one element in the stack when pop, top, peekMax,
# or popMax is called.
#
# @lc code=start
class MaxStack:
    def __init__(self):
        """
        Interview explanation:
        Premium: stack with push/pop/top plus peekMax/popMax. Dual stack of
        values and running maxima; popMax uses a temporary buffer.

        Algorithm:
        - stack + max_stack where max_stack[i] = max(stack[0..i]).

        Complexity: O(1) init.
        """
        self.stack = []
        self.max_stack = []

    def push(self, x: int) -> None:
        """
        Interview explanation:
        Push x and update the running maximum.

        Algorithm:
        - Append x; append max(x, previous max or x).

        Complexity: O(1).
        """
        self.stack.append(x)
        self.max_stack.append(x if not self.max_stack else max(x, self.max_stack[-1]))

    def pop(self) -> int:
        """
        Interview explanation:
        Pop and return the top value.

        Algorithm:
        - Pop both stacks in tandem.

        Complexity: O(1).
        """
        self.max_stack.pop()
        return self.stack.pop()

    def top(self) -> int:
        """
        Interview explanation:
        Peek the top value without removal.

        Algorithm:
        - Return stack[-1].

        Complexity: O(1).
        """
        return self.stack[-1]

    def peekMax(self) -> int:
        """
        Interview explanation:
        Return the current maximum in the stack.

        Algorithm:
        - Return max_stack[-1].

        Complexity: O(1).
        """
        return self.max_stack[-1]

    def popMax(self) -> int:
        """
        Interview explanation:
        Remove and return the most recent occurrence of the current maximum.

        Algorithm:
        - Pop into a buffer until top equals max; pop max; re-push buffer.

        Complexity: O(n) time, O(n) space.
        """
        m = self.peekMax()
        buf = []
        while self.top() != m:
            buf.append(self.pop())
        self.pop()
        while buf:
            self.push(buf.pop())
        return m
# @lc code=end
