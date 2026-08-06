#
# @lc app=leetcode id=622 lang=python3
#
# [622] Design Circular Queue
#
# https://leetcode.com/problems/design-circular-queue/description/
#
# algorithms
# Medium (55.17%)
# Likes:    3877
# Dislikes: 361
# Total Accepted:    507K
# Total Submissions: 918K
# Testcase Example:  "[\"MyCircularQueue\",\"enQueue\",\"enQueue\",\"enQueue\",\"enQueue\",\"Rear\",\"isFull\",\"deQueue\",\"enQueue\",\"Rear\"]"
#
# Design your implementation of the circular queue. The circular queue is a
# linear data structure in which the operations are performed based on FIFO
# (First In First Out) principle, and the last position is connected back to
# the first position to make a circle. It is also called "Ring Buffer".
#
# One of the benefits of the circular queue is that we can make use of the
# spaces in front of the queue. In a normal queue, once the queue becomes full,
# we cannot insert the next element even if there is a space in front of the
# queue. But using the circular queue, we can use the space to store new
# values.
#
# Implement the MyCircularQueue class:
#
# MyCircularQueue(k) Initializes the object with the size of the queue to be k.
#
# int Front() Gets the front item from the queue. If the queue is empty, return
# -1.
#
# int Rear() Gets the last item from the queue. If the queue is empty, return
# -1.
#
# boolean enQueue(int value) Inserts an element into the circular queue. Return
# true if the operation is successful.
#
# boolean deQueue() Deletes an element from the circular queue. Return true if
# the operation is successful.
#
# boolean isEmpty() Checks whether the circular queue is empty or not.
#
# boolean isFull() Checks whether the circular queue is full or not.
#
# You must solve the problem without using the built-in queue data structure in
# your programming language.
#
# Example 1:
#
# Input
# ["MyCircularQueue", "enQueue", "enQueue", "enQueue", "enQueue", "Rear",
# "isFull", "deQueue", "enQueue", "Rear"]
# [[3], [1], [2], [3], [4], [], [], [], [4], []]
# Output
# [null, true, true, true, false, 3, true, true, true, 4]
#
# Explanation
# MyCircularQueue myCircularQueue = new MyCircularQueue(3);
# myCircularQueue.enQueue(1); // return True
# myCircularQueue.enQueue(2); // return True
# myCircularQueue.enQueue(3); // return True
# myCircularQueue.enQueue(4); // return False
# myCircularQueue.Rear(); // return 3
# myCircularQueue.isFull(); // return True
# myCircularQueue.deQueue(); // return True
# myCircularQueue.enQueue(4); // return True
# myCircularQueue.Rear(); // return 4
#
# Constraints:
#
# 1 <= k <= 1000
#
# 0 <= value <= 1000
#
# At most 3000 calls will be made to enQueue, deQueue, Front, Rear, isEmpty,
# and isFull.
#

# @lc code=start

class MyCircularQueue:
    def __init__(self, k: int):
        """
        Interview explanation:
        Fixed-capacity ring buffer with head/tail indices (or head + size).

        Algorithm:
        - Array of size k; head index of front; size current count.
        - Rear at (head + size - 1) % k.

        Complexity: O(k) space; O(1) per op.
        """
        self.cap = k
        self.data = [0] * k
        self.head = 0
        self.size = 0

    def enQueue(self, value: int) -> bool:
        """
        Interview explanation:
        Insert at rear if not full.

        Algorithm:
        - If full return False.
        - Write at (head + size) % cap; size++.

        Complexity: O(1).
        """
        if self.isFull():
            return False
        self.data[(self.head + self.size) % self.cap] = value
        self.size += 1
        return True

    def deQueue(self) -> bool:
        """
        Interview explanation:
        Remove front if not empty.

        Algorithm:
        - If empty return False.
        - head = (head + 1) % cap; size--.

        Complexity: O(1).
        """
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.cap
        self.size -= 1
        return True

    def Front(self) -> int:
        """
        Interview explanation:
        Peek front element or -1 if empty.

        Algorithm:
        - Return data[head] if size > 0 else -1.

        Complexity: O(1).
        """
        return -1 if self.isEmpty() else self.data[self.head]

    def Rear(self) -> int:
        """
        Interview explanation:
        Peek rear element or -1 if empty.

        Algorithm:
        - Index (head + size - 1) % cap.

        Complexity: O(1).
        """
        if self.isEmpty():
            return -1
        return self.data[(self.head + self.size - 1) % self.cap]

    def isEmpty(self) -> bool:
        """
        Interview explanation:
        Empty iff size == 0.

        Algorithm:
        - Return size == 0.

        Complexity: O(1).
        """
        return self.size == 0

    def isFull(self) -> bool:
        """
        Interview explanation:
        Full iff size == capacity.

        Algorithm:
        - Return size == cap.

        Complexity: O(1).
        """
        return self.size == self.cap


# Your MyCircularQueue object will be instantiated and called as such:
# obj = MyCircularQueue(k)
# param_1 = obj.enQueue(value)
# param_2 = obj.deQueue()
# param_3 = obj.Front()
# param_4 = obj.Rear()
# param_5 = obj.isEmpty()
# param_6 = obj.isFull()
# @lc code=end
