#
# @lc app=leetcode id=1206 lang=python3
#
# [1206] Design Skiplist
#
# https://leetcode.com/problems/design-skiplist/description/
#
# algorithms
# Hard (59.78%)
# Likes:    732
# Dislikes: 112
# Total Accepted:    38.4K
# Total Submissions: 64.2K
# Testcase Example:  "[\"Skiplist\",\"add\",\"add\",\"add\",\"search\",\"add\",\"search\",\"erase\",\"erase\",\"search\"]"
#
# Design a Skiplist without using any built-in libraries.
#
# A skiplist is a data structure that takes O(log(n)) time to add, erase and
# search. Comparing with treap and red-black tree which has the same function
# and performance, the code length of Skiplist can be comparatively short and
# the idea behind Skiplists is just simple linked lists.
#
# For example, we have a Skiplist containing [30,40,50,60,70,90] and we want to
# add 80 and 45 into it. The Skiplist works this way:
#
# Artyom Kalinin [CC BY-SA 3.0], via Wikimedia Commons
#
# You can see there are many layers in the Skiplist. Each layer is a sorted
# linked list. With the help of the top layers, add, erase and search can be
# faster than O(n). It can be proven that the average time complexity for each
# operation is O(log(n)) and space complexity is O(n).
#
# See more about Skiplist: https://en.wikipedia.org/wiki/Skip_list
#
# Implement the Skiplist class:
#
# Skiplist() Initializes the object of the skiplist.
#
# bool search(int target) Returns true if the integer target exists in the
# Skiplist or false otherwise.
#
# void add(int num) Inserts the value num into the SkipList.
#
# bool erase(int num) Removes the value num from the Skiplist and returns true.
# If num does not exist in the Skiplist, do nothing and return false. If there
# exist multiple num values, removing any one of them is fine.
#
# Note that duplicates may exist in the Skiplist, your code needs to handle
# this situation.
#
# Example 1:
#
# Input
# ["Skiplist", "add", "add", "add", "search", "add", "search", "erase",
# "erase", "search"]
# [[], [1], [2], [3], [0], [4], [1], [0], [1], [1]]
# Output
# [null, null, null, null, false, null, true, false, true, false]
#
# Explanation
# Skiplist skiplist = new Skiplist();
# skiplist.add(1);
# skiplist.add(2);
# skiplist.add(3);
# skiplist.search(0); // return False
# skiplist.add(4);
# skiplist.search(1); // return True
# skiplist.erase(0); // return False, 0 is not in skiplist.
# skiplist.erase(1); // return True
# skiplist.search(1); // return False, 1 has already been erased.
#
# Constraints:
#
# 0 <= num, target <= 2 * 10^4
#
# At most 5 * 10^4 calls will be made to search, add, and erase.
#


# @lc code=start
import random

class Skiplist:
    class Node:
        def __init__(self, val: int, level: int):
            self.val = val
            self.next = [None] * (level + 1)

    def __init__(self):
        """
        Interview explanation:
        Probabilistic multi-level linked list. Each node has random height;
        search/insert/erase walk from top level down like a skip list.

        Algorithm:
        - maxLevel=16, p=0.5; sentinel head with all levels
        - randomLevel: geometric height

        Complexity: O(1) init; expected O(log n) ops.
        """
        self.max_level = 16
        self.p = 0.5
        self.head = Skiplist.Node(-1, self.max_level)
        self.level = 0

    def _random_level(self) -> int:
        lvl = 0
        while lvl < self.max_level and random.random() < self.p:
            lvl += 1
        return lvl

    def search(self, target: int) -> bool:
        """
        Interview explanation:
        Walk from highest level; at each level advance while next.val < target;
        drop a level; succeed if next equals target.

        Algorithm:
        - cur=head; for lvl from level..0: while next and next.val < target advance
        - return cur.next[0] exists and val==target

        Complexity: Expected O(log n).
        """
        cur = self.head
        for i in range(self.level, -1, -1):
            while cur.next[i] and cur.next[i].val < target:
                cur = cur.next[i]
        cur = cur.next[0]
        return cur is not None and cur.val == target

    def add(self, num: int) -> None:
        """
        Interview explanation:
        Find predecessors at each level, create node with random height, splice
        into all levels up to that height.

        Algorithm:
        - update[i]=pred at level i; create node; link update[i].next[i]

        Complexity: Expected O(log n).
        """
        update = [None] * (self.max_level + 1)
        cur = self.head
        for i in range(self.level, -1, -1):
            while cur.next[i] and cur.next[i].val < num:
                cur = cur.next[i]
            update[i] = cur
        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.head
            self.level = lvl
        node = Skiplist.Node(num, lvl)
        for i in range(lvl + 1):
            node.next[i] = update[i].next[i]
            update[i].next[i] = node

    def erase(self, num: int) -> bool:
        """
        Interview explanation:
        Find predecessors; if next is num, unlink at all levels where it appears.

        Algorithm:
        - Same update walk; if next[0].val==num unlink across levels; shrink level

        Complexity: Expected O(log n).
        """
        update = [None] * (self.max_level + 1)
        cur = self.head
        for i in range(self.level, -1, -1):
            while cur.next[i] and cur.next[i].val < num:
                cur = cur.next[i]
            update[i] = cur
        target = cur.next[0]
        if target is None or target.val != num:
            return False
        for i in range(self.level + 1):
            if update[i].next[i] != target:
                break
            update[i].next[i] = target.next[i]
        while self.level > 0 and self.head.next[self.level] is None:
            self.level -= 1
        return True
# @lc code=end
