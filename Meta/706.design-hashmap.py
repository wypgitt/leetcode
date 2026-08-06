#
# @lc app=leetcode id=706 lang=python3
#
# [706] Design HashMap
#
# https://leetcode.com/problems/design-hashmap/description/
#
# algorithms
# Easy (66.75%)
# Likes:    5458
# Dislikes: 503
# Total Accepted:    793K
# Total Submissions: 1.2M
# Testcase Example:  "[\"MyHashMap\",\"put\",\"put\",\"get\",\"get\",\"put\",\"get\",\"remove\",\"get\"]"
#
# Design a HashMap without using any built-in hash table libraries.
#
# Implement the MyHashMap class:
#
# MyHashMap() initializes the object with an empty map.
#
# void put(int key, int value) inserts a (key, value) pair into the HashMap. If
# the key already exists in the map, update the corresponding value.
#
# int get(int key) returns the value to which the specified key is mapped, or
# -1 if this map contains no mapping for the key.
#
# void remove(key) removes the key and its corresponding value if the map
# contains the mapping for the key.
#
# Example 1:
#
# Input
# ["MyHashMap", "put", "put", "get", "get", "put", "get", "remove", "get"]
# [[], [1, 1], [2, 2], [1], [3], [2, 1], [2], [2], [2]]
# Output
# [null, null, null, 1, -1, null, 1, null, -1]
#
# Explanation
# MyHashMap myHashMap = new MyHashMap();
# myHashMap.put(1, 1); // The map is now [[1,1]]
# myHashMap.put(2, 2); // The map is now [[1,1], [2,2]]
# myHashMap.get(1); // return 1, The map is now [[1,1], [2,2]]
# myHashMap.get(3); // return -1 (i.e., not found), The map is now [[1,1],
# [2,2]]
# myHashMap.put(2, 1); // The map is now [[1,1], [2,1]] (i.e., update the
# existing value)
# myHashMap.get(2); // return 1, The map is now [[1,1], [2,1]]
# myHashMap.remove(2); // remove the mapping for 2, The map is now [[1,1]]
# myHashMap.get(2); // return -1 (i.e., not found), The map is now [[1,1]]
#
# Constraints:
#
# 0 <= key, value <= 10^6
#
# At most 10^4 calls will be made to put, get, and remove.
#

# @lc code=start
class MyHashMap:
    def __init__(self):
        """
        Interview explanation:
        Hash map with chaining: buckets hold (key, value) pairs; overwrite on
        put if key exists.

        Algorithm:
        - Fixed bucket array of lists; hash = key % size.

        Complexity: O(capacity) init.
        """
        self.size = 769
        self.buckets = [[] for _ in range(self.size)]

    def _idx(self, key: int) -> int:
        return key % self.size

    def put(self, key: int, value: int) -> None:
        """
        Interview explanation:
        Insert or update (key, value) in the hashed bucket.

        Algorithm:
        - Scan bucket for key; update value or append new pair.

        Complexity: O(n/B) average.
        """
        b = self.buckets[self._idx(key)]
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = (key, value)
                return
        b.append((key, value))

    def get(self, key: int) -> int:
        """
        Interview explanation:
        Return mapped value or -1 if absent.

        Algorithm:
        - Scan bucket for key.

        Complexity: O(n/B) average.
        """
        for k, v in self.buckets[self._idx(key)]:
            if k == key:
                return v
        return -1

    def remove(self, key: int) -> None:
        """
        Interview explanation:
        Delete key from map if present.

        Algorithm:
        - Find index in bucket and pop.

        Complexity: O(n/B) average.
        """
        b = self.buckets[self._idx(key)]
        for i, (k, _) in enumerate(b):
            if k == key:
                b.pop(i)
                return


# Your MyHashMap object will be instantiated and called as such:
# obj = MyHashMap()
# obj.put(key,value)
# param_2 = obj.get(key)
# obj.remove(key)
# @lc code=end
