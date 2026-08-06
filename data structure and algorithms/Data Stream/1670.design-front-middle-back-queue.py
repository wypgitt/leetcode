#
# @lc app=leetcode id=1670 lang=python3
#
# [1670] Design Front Middle Back Queue
#
# https://leetcode.com/problems/design-front-middle-back-queue/description/
#
# algorithms
# Medium (58.37%)
# Likes:    834
# Dislikes: 116
# Total Accepted:    48.5K
# Total Submissions: 83.1K
# Testcase Example:  "[\"FrontMiddleBackQueue\",\"pushFront\",\"pushBack\",\"pushMiddle\",\"pushMiddle\",\"popFront\",\"popMiddle\",\"popMiddle\",\"popBack\",\"popFront\"]"
#
# Design a queue that supports push and pop operations in the front, middle,
# and back.
#
# Implement the FrontMiddleBack class:
#
# FrontMiddleBack() Initializes the queue.
#
# void pushFront(int val) Adds val to the front of the queue.
#
# void pushMiddle(int val) Adds val to the middle of the queue.
#
# void pushBack(int val) Adds val to the back of the queue.
#
# int popFront() Removes the front element of the queue and returns it. If the
# queue is empty, return -1.
#
# int popMiddle() Removes the middle element of the queue and returns it. If
# the queue is empty, return -1.
#
# int popBack() Removes the back element of the queue and returns it. If the
# queue is empty, return -1.
#
# Notice that when there are two middle position choices, the operation is
# performed on the frontmost middle position choice. For example:
#
# Pushing 6 into the middle of [1, 2, 3, 4, 5] results in [1, 2, 6, 3, 4, 5].
#
# Popping the middle from [1, 2, 3, 4, 5, 6] returns 3 and results in [1, 2, 4,
# 5, 6].
#
# Example 1:
#
# Input:
# ["FrontMiddleBackQueue", "pushFront", "pushBack", "pushMiddle", "pushMiddle",
# "popFront", "popMiddle", "popMiddle", "popBack", "popFront"]
# [[], [1], [2], [3], [4], [], [], [], [], []]
# Output:
# [null, null, null, null, null, 1, 3, 4, 2, -1]
#
# Explanation:
# FrontMiddleBackQueue q = new FrontMiddleBackQueue();
# q.pushFront(1); // [1]
# q.pushBack(2); // [1, 2]
# q.pushMiddle(3); // [1, 3, 2]
# q.pushMiddle(4); // [1, 4, 3, 2]
# q.popFront(); // return 1 -> [4, 3, 2]
# q.popMiddle(); // return 3 -> [4, 2]
# q.popMiddle(); // return 4 -> [2]
# q.popBack(); // return 2 -> []
# q.popFront(); // return -1 -> [] (The queue is empty)
#
# Constraints:
#
# 1 <= val <= 10^9
#
# At most 1000 calls will be made to pushFront, pushMiddle, pushBack, popFront,
# popMiddle, and popBack.
#

# @lc code=start
from collections import deque


class FrontMiddleBackQueue:
    def __init__(self):
        """
        Interview explanation:
        Queue supporting push/pop at front, middle, and back. Two deques
        (A=front half, B=back half) with invariant len(B)==len(A) or
        len(B)==len(A)+1 so frontmost middle is A[-1] (even) or B[0] (odd).

        Algorithm:
        - A, B = deque(), deque(); balance after each op.

        Complexity: O(1) init.
        """
        self.A = deque()
        self.B = deque()

    def _balance(self) -> None:
        if len(self.A) > len(self.B):
            self.B.appendleft(self.A.pop())
        elif len(self.B) > len(self.A) + 1:
            self.A.append(self.B.popleft())

    def pushFront(self, val: int) -> None:
        """
        Interview explanation:
        Insert at front of the queue.

        Algorithm:
        - A.appendleft(val); balance.

        Complexity: O(1) amortized.
        """
        self.A.appendleft(val)
        self._balance()

    def pushMiddle(self, val: int) -> None:
        """
        Interview explanation:
        Insert at frontmost middle (before current middle when even length).

        Algorithm:
        - A.append(val); balance so new middle is correct.

        Complexity: O(1) amortized.
        """
        self.A.append(val)
        self._balance()

    def pushBack(self, val: int) -> None:
        """
        Interview explanation:
        Insert at back of the queue.

        Algorithm:
        - B.append(val); balance.

        Complexity: O(1) amortized.
        """
        self.B.append(val)
        self._balance()

    def popFront(self) -> int:
        """
        Interview explanation:
        Remove and return front; -1 if empty.

        Algorithm:
        - Prefer A.popleft else B.popleft; balance.

        Complexity: O(1) amortized.
        """
        if not self.A and not self.B:
            return -1
        val = self.A.popleft() if self.A else self.B.popleft()
        self._balance()
        return val

    def popMiddle(self) -> int:
        """
        Interview explanation:
        Remove frontmost middle: even size → A[-1]; odd size → B[0].

        Algorithm:
        - if len(A)==len(B): A.pop else B.popleft; balance.

        Complexity: O(1) amortized.
        """
        if not self.A and not self.B:
            return -1
        val = self.A.pop() if len(self.A) == len(self.B) else self.B.popleft()
        self._balance()
        return val

    def popBack(self) -> int:
        """
        Interview explanation:
        Remove and return back; -1 if empty.

        Algorithm:
        - Prefer B.pop else A.pop; balance.

        Complexity: O(1) amortized.
        """
        if not self.A and not self.B:
            return -1
        val = self.B.pop() if self.B else self.A.pop()
        self._balance()
        return val


# Your FrontMiddleBackQueue object will be instantiated and called as such:
# obj = FrontMiddleBackQueue()
# obj.pushFront(val)
# obj.pushMiddle(val)
# obj.pushBack(val)
# param_4 = obj.popFront()
# param_5 = obj.popMiddle()
# param_6 = obj.popBack()
# @lc code=end
