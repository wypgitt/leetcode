#
# @lc app=leetcode id=707 lang=python3
#
# [707] Design Linked List
#
# https://leetcode.com/problems/design-linked-list/description/
#
# algorithms
# Medium (30.62%)
# Likes:    3112
# Dislikes: 1686
# Total Accepted:    513K
# Total Submissions: 1.7M
# Testcase Example:  "[\"MyLinkedList\",\"addAtHead\",\"deleteAtIndex\",\"addAtTail\",\"get\"]"
#
# Design your implementation of the linked list. You can choose to use a singly
# or doubly linked list.
#
# A node in a singly linked list should have two attributes: val and next. val
# is the value of the current node, and next is a pointer/reference to the next
# node.
#
# If you want to use the doubly linked list, you will need one more attribute
# prev to indicate the previous node in the linked list. Assume all nodes in
# the linked list are 0-indexed.
#
# Implement the MyLinkedList class:
#
# MyLinkedList() Initializes the MyLinkedList object.
#
# int get(int index) Get the value of the index^th node in the linked list. If
# the index is invalid, return -1.
#
# void addAtHead(int val) Add a node of value val before the first element of
# the linked list. After the insertion, the new node will be the first node of
# the linked list.
#
# void addAtTail(int val) Append a node of value val as the last element of the
# linked list.
#
# void addAtIndex(int index, int val) Add a node of value val before the
# index^th node in the linked list. If index equals the length of the linked
# list, the node will be appended to the end of the linked list. If index is
# greater than the length, the node will not be inserted.
#
# void deleteAtIndex(int index) Delete the index^th node in the linked list, if
# the index is valid.
#
# Example 1:
#
# Input
# ["MyLinkedList", "addAtHead", "addAtTail", "addAtIndex", "get",
# "deleteAtIndex", "get"]
# [[], [1], [3], [1, 2], [1], [1], [1]]
# Output
# [null, null, null, null, 2, null, 3]
#
# Explanation
# MyLinkedList myLinkedList = new MyLinkedList();
# myLinkedList.addAtHead(1);
# myLinkedList.addAtTail(3);
# myLinkedList.addAtIndex(1, 2); // linked list becomes 1->2->3
# myLinkedList.get(1); // return 2
# myLinkedList.deleteAtIndex(1); // now the linked list is 1->3
# myLinkedList.get(1); // return 3
#
# Constraints:
#
# 0 <= index, val <= 1000
#
# Please do not use the built-in LinkedList library.
#
# At most 2000 calls will be made to get, addAtHead, addAtTail, addAtIndex and
# deleteAtIndex.
#

# @lc code=start
class _Node:
    def __init__(self, val: int = 0):
        self.val = val
        self.next = None


class MyLinkedList:
    def __init__(self):
        """
        Interview explanation:
        Singly linked list with sentinel head and size counter for O(1) length
        checks and simpler index operations.

        Algorithm:
        - dummy head; size = 0.

        Complexity: O(1).
        """
        self.head = _Node(0)
        self.size = 0

    def get(self, index: int) -> int:
        """
        Interview explanation:
        Return value at 0-based index, or -1 if invalid.

        Algorithm:
        - Walk index+1 steps from sentinel.

        Complexity: O(index).
        """
        if index < 0 or index >= self.size:
            return -1
        cur = self.head.next
        for _ in range(index):
            cur = cur.next
        return cur.val

    def addAtHead(self, val: int) -> None:
        """
        Interview explanation:
        Insert new node at the front (index 0).

        Algorithm:
        - addAtIndex(0, val).

        Complexity: O(1).
        """
        self.addAtIndex(0, val)

    def addAtTail(self, val: int) -> None:
        """
        Interview explanation:
        Append node at the end.

        Algorithm:
        - addAtIndex(size, val).

        Complexity: O(n).
        """
        self.addAtIndex(self.size, val)

    def addAtIndex(self, index: int, val: int) -> None:
        """
        Interview explanation:
        Insert before index; if index == size append; if index > size no-op.

        Algorithm:
        - Walk to predecessor; splice new node; size++.

        Complexity: O(index).
        """
        if index < 0 or index > self.size:
            return
        pred = self.head
        for _ in range(index):
            pred = pred.next
        node = _Node(val)
        node.next = pred.next
        pred.next = node
        self.size += 1

    def deleteAtIndex(self, index: int) -> None:
        """
        Interview explanation:
        Delete node at index if valid.

        Algorithm:
        - Walk to predecessor; bypass node; size--.

        Complexity: O(index).
        """
        if index < 0 or index >= self.size:
            return
        pred = self.head
        for _ in range(index):
            pred = pred.next
        pred.next = pred.next.next
        self.size -= 1


# Your MyLinkedList object will be instantiated and called as such:
# obj = MyLinkedList()
# param_1 = obj.get(index)
# obj.addAtHead(val)
# obj.addAtTail(val)
# obj.addAtIndex(index,val)
# obj.deleteAtIndex(index)
# @lc code=end
