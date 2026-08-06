#
# @lc app=leetcode id=432 lang=python3
#
# [432] All O`one Data Structure
#
# https://leetcode.com/problems/all-oone-data-structure/description/
#
# algorithms
# Hard (44.45%)
# Likes:    2254
# Dislikes: 224
# Total Accepted:    212K
# Total Submissions: 477K
# Testcase Example:  "[\"AllOne\",\"inc\",\"inc\",\"getMaxKey\",\"getMinKey\",\"inc\",\"getMaxKey\",\"getMinKey\"]"
#
# Design a data structure to store the strings' count with the ability to
# return the strings with minimum and maximum counts.
#
# Implement the AllOne class:
#
# AllOne() Initializes the object of the data structure.
#
# inc(String key) Increments the count of the string key by 1. If key does not
# exist in the data structure, insert it with count 1.
#
# dec(String key) Decrements the count of the string key by 1. If the count of
# key is 0 after the decrement, remove it from the data structure. It is
# guaranteed that key exists in the data structure before the decrement.
#
# getMaxKey() Returns one of the keys with the maximal count. If no element
# exists, return an empty string "".
#
# getMinKey() Returns one of the keys with the minimum count. If no element
# exists, return an empty string "".
#
# Note that each function must run in O(1) average time complexity.
#
# Example 1:
#
# Input
# ["AllOne", "inc", "inc", "getMaxKey", "getMinKey", "inc", "getMaxKey",
# "getMinKey"]
# [[], ["hello"], ["hello"], [], [], ["leet"], [], []]
# Output
# [null, null, null, "hello", "hello", null, "hello", "leet"]
#
# Explanation
# AllOne allOne = new AllOne();
# allOne.inc("hello");
# allOne.inc("hello");
# allOne.getMaxKey(); // return "hello"
# allOne.getMinKey(); // return "hello"
# allOne.inc("leet");
# allOne.getMaxKey(); // return "hello"
# allOne.getMinKey(); // return "leet"
#
# Constraints:
#
# 1 <= key.length <= 10
#
# key consists of lowercase English letters.
#
# It is guaranteed that for each call to dec, key is existing in the data
# structure.
#
# At most 5 * 10^4 calls will be made to inc, dec, getMaxKey, and getMinKey.
#

# @lc code=start

from collections import defaultdict
from typing import Dict, Optional, Set


class _Node:
    __slots__ = ("count", "keys", "prev", "next")

    def __init__(self, count: int):
        self.count = count
        self.keys: Set[str] = set()
        self.prev: Optional["_Node"] = None
        self.next: Optional["_Node"] = None


class AllOne:
    """
    Interview explanation:
    O(1) inc/dec/getMax/getMin via doubly linked list of frequency buckets and
    a map from key → bucket node. Adjacent buckets differ by one in count.
    """

    def __init__(self):
        """
        Interview explanation:
        Sentinel head/tail DLL of count buckets; key_node maps key to its bucket.

        Algorithm:
        - head <-> tail empty sentinels; key_node = {}.

        Complexity: O(1) init.
        """
        self.head = _Node(0)
        self.tail = _Node(0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.key_node: Dict[str, _Node] = {}

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_after(self, prev: _Node, node: _Node) -> None:
        nxt = prev.next
        prev.next = node
        node.prev = prev
        node.next = nxt
        nxt.prev = node

    def inc(self, key: str) -> None:
        """
        Interview explanation:
        Move key from count bucket c to c+1 (create bucket if needed). New keys
        start at count 1 after head.

        Algorithm:
        - If new: ensure bucket 1 after head; add key.
        - Else: move to next bucket with count+1; remove empty old bucket.

        Complexity: O(1) time.
        """
        if key not in self.key_node:
            # insert into count=1 bucket
            if self.head.next == self.tail or self.head.next.count != 1:
                node = _Node(1)
                self._insert_after(self.head, node)
            else:
                node = self.head.next
            node.keys.add(key)
            self.key_node[key] = node
            return
        cur = self.key_node[key]
        nxt = cur.next
        if nxt == self.tail or nxt.count != cur.count + 1:
            node = _Node(cur.count + 1)
            self._insert_after(cur, node)
        else:
            node = nxt
        node.keys.add(key)
        self.key_node[key] = node
        cur.keys.remove(key)
        if not cur.keys:
            self._remove(cur)

    def dec(self, key: str) -> None:
        """
        Interview explanation:
        Move key from count c to c-1, or remove if c==1.

        Algorithm:
        - If count==1: delete key and maybe bucket.
        - Else move to prev bucket with count-1; remove empty old bucket.

        Complexity: O(1) time.
        """
        cur = self.key_node[key]
        if cur.count == 1:
            cur.keys.remove(key)
            del self.key_node[key]
            if not cur.keys:
                self._remove(cur)
            return
        prev = cur.prev
        if prev == self.head or prev.count != cur.count - 1:
            node = _Node(cur.count - 1)
            self._insert_after(prev, node)
        else:
            node = prev
        node.keys.add(key)
        self.key_node[key] = node
        cur.keys.remove(key)
        if not cur.keys:
            self._remove(cur)

    def getMaxKey(self) -> str:
        """
        Interview explanation:
        Max frequency bucket is immediately before the tail sentinel.

        Algorithm:
        - If no buckets return ""; else return any key from tail.prev.

        Complexity: O(1) time.
        """
        if self.tail.prev == self.head:
            return ""
        return next(iter(self.tail.prev.keys))

    def getMinKey(self) -> str:
        """
        Interview explanation:
        Min frequency bucket is immediately after the head sentinel.

        Algorithm:
        - If no buckets return ""; else return any key from head.next.

        Complexity: O(1) time.
        """
        if self.head.next == self.tail:
            return ""
        return next(iter(self.head.next.keys))


# Your AllOne object will be instantiated and called as such:
# obj = AllOne()
# obj.inc(key)
# obj.dec(key)
# param_3 = obj.getMaxKey()
# param_4 = obj.getMinKey()
# @lc code=end
