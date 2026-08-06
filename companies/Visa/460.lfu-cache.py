#
# @lc app=leetcode id=460 lang=python3
#
# [460] LFU Cache
#
# https://leetcode.com/problems/lfu-cache/description/
#
# algorithms
# Hard (49.94%)
# Likes:    6472
# Dislikes: 355
# Total Accepted:    408K
# Total Submissions: 816K
# Testcase Example:  "[\"LFUCache\",\"put\",\"put\",\"get\",\"put\",\"get\",\"get\",\"put\",\"get\",\"get\",\"get\"]"
#
# Design and implement a data structure for a Least Frequently Used (LFU)
# cache.
#
# Implement the LFUCache class:
#
# LFUCache(int capacity) Initializes the object with the capacity of the data
# structure.
#
# int get(int key) Gets the value of the key if the key exists in the cache.
# Otherwise, returns -1.
#
# void put(int key, int value) Update the value of the key if present, or
# inserts the key if not already present. When the cache reaches its capacity,
# it should invalidate and remove the least frequently used key before
# inserting a new item. For this problem, when there is a tie (i.e., two or
# more keys with the same frequency), the least recently used key would be
# invalidated.
#
# To determine the least frequently used key, a use counter is maintained for
# each key in the cache. The key with the smallest use counter is the least
# frequently used key.
#
# When a key is first inserted into the cache, its use counter is set to 1 (due
# to the put operation). The use counter for a key in the cache is incremented
# either a get or put operation is called on it.
#
# The functions get and put must each run in O(1) average time complexity.
#
# Example 1:
#
# Input
# ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get",
# "get"]
# [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]
# Output
# [null, null, null, 1, null, -1, 3, null, -1, 3, 4]
#
# Explanation
# // cnt(x) = the use counter for key x
# // cache=[] will show the last used order for tiebreakers (leftmost element
# is most recent)
# LFUCache lfu = new LFUCache(2);
# lfu.put(1, 1); // cache=[1,_], cnt(1)=1
# lfu.put(2, 2); // cache=[2,1], cnt(2)=1, cnt(1)=1
# lfu.get(1); // return 1
# // cache=[1,2], cnt(2)=1, cnt(1)=2
# lfu.put(3, 3); // 2 is the LFU key because cnt(2)=1 is the smallest,
# invalidate 2.
# // cache=[3,1], cnt(3)=1, cnt(1)=2
# lfu.get(2); // return -1 (not found)
# lfu.get(3); // return 3
# // cache=[3,1], cnt(3)=2, cnt(1)=2
# lfu.put(4, 4); // Both 1 and 3 have the same cnt, but 1 is LRU, invalidate 1.
# // cache=[4,3], cnt(4)=1, cnt(3)=2
# lfu.get(1); // return -1 (not found)
# lfu.get(3); // return 3
# // cache=[3,4], cnt(4)=1, cnt(3)=3
# lfu.get(4); // return 4
# // cache=[4,3], cnt(4)=2, cnt(3)=3
#
# Constraints:
#
# 1 <= capacity <= 10^4
#
# 0 <= key <= 10^5
#
# 0 <= value <= 10^9
#
# At most 2 * 10^5 calls will be made to get and put.
#

# @lc code=start
from collections import defaultdict, OrderedDict


class LFUCache:
    """
    Interview explanation:
    O(1) LFU: key → (value, freq); freq → OrderedDict of keys at that freq
    (LRU order within a frequency). Track min_freq; on get/put bump freq and
    move key; on eviction remove oldest key in freq_map[min_freq].
    """

    def __init__(self, capacity: int):
        """
        Interview explanation:
        Initialize capacity, key map, frequency buckets, and min_freq.

        Algorithm:
        - key_map: key -> [value, freq]
        - freq_map: freq -> OrderedDict of keys (insertion = LRU order)
        - min_freq starts at 0.

        Complexity: O(1) init, O(capacity) space overall.
        """
        self.capacity = capacity
        self.key_map = {}
        self.freq_map = defaultdict(OrderedDict)
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        val, freq = self.key_map[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and freq == self.min_freq:
            self.min_freq += 1
        self.freq_map[freq + 1][key] = None
        self.key_map[key] = [val, freq + 1]

    def get(self, key: int) -> int:
        """
        Interview explanation:
        Return value if present and increment frequency (also updates LRU
        position within the new frequency bucket).

        Algorithm:
        - If key missing: -1; else _touch(key) and return value.

        Complexity: O(1) average time, O(1) space.
        """
        if key not in self.key_map:
            return -1
        self._touch(key)
        return self.key_map[key][0]

    def put(self, key: int, value: int) -> None:
        """
        Interview explanation:
        Insert or update. On update, set value and bump freq. On insert at
        capacity, evict LFU (and LRU within that freq), then insert at freq 1.

        Algorithm:
        - capacity 0: noop.
        - If key exists: update value, _touch.
        - Else if full: popitem(last=False) from freq_map[min_freq], delete.
        - Insert key with freq 1; min_freq = 1.

        Complexity: O(1) average time, O(1) space.
        """
        if self.capacity == 0:
            return
        if key in self.key_map:
            self.key_map[key][0] = value
            self._touch(key)
            return
        if len(self.key_map) >= self.capacity:
            old_key, _ = self.freq_map[self.min_freq].popitem(last=False)
            del self.key_map[old_key]
        self.key_map[key] = [value, 1]
        self.freq_map[1][key] = None
        self.min_freq = 1


# Your LFUCache object will be instantiated and called as such:
# obj = LFUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
# @lc code=end
