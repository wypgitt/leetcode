#
# @lc app=leetcode id=705 lang=python3
#
# [705] Design HashSet
#
# https://leetcode.com/problems/design-hashset/description/
#
# algorithms
# Easy (68.34%)
# Likes:    4074
# Dislikes: 330
# Total Accepted:    598K
# Total Submissions: 876K
# Testcase Example:  "[\"MyHashSet\",\"add\",\"add\",\"add\",\"remove\",\"contains\",\"add\",\"add\",\"add\",\"remove\",\"contains\",\"add\",\"add\",\"add\",\"remove\",\"contains\",\"add\",\"add\",\"add\",\"remove\",\"contains\"]"
#
# Design a HashSet without using any built-in hash table libraries.
#
# Implement MyHashSet class:
#
# void add(key) Inserts the value key into the HashSet.
#
# bool contains(key) Returns whether the value key exists in the HashSet or
# not.
#
# void remove(key) Removes the value key in the HashSet. If key does not exist
# in the HashSet, do nothing.
#
# Example 1:
#
# Input
# ["MyHashSet", "add", "add", "contains", "contains", "add", "contains",
# "remove", "contains"]
# [[], [1], [2], [1], [3], [2], [2], [2], [2]]
# Output
# [null, null, null, true, false, null, true, null, false]
#
# Explanation
# MyHashSet myHashSet = new MyHashSet();
# myHashSet.add(1); // set = [1]
# myHashSet.add(2); // set = [1, 2]
# myHashSet.contains(1); // return True
# myHashSet.contains(3); // return False, (not found)
# myHashSet.add(2); // set = [1, 2]
# myHashSet.contains(2); // return True
# myHashSet.remove(2); // set = [1]
# myHashSet.contains(2); // return False, (already removed)
#
# Constraints:
#
# 0 <= key <= 10^6
#
# At most 10^4 calls will be made to add, remove, and contains.
#

# @lc code=start
class MyHashSet:
    def __init__(self):
        """
        Interview explanation:
        Hash set via chaining: fixed bucket array; each bucket is a list of keys.
        hash(key) = key % capacity.

        Algorithm:
        - Choose prime-ish capacity (e.g. 769); empty lists per bucket.

        Complexity: O(capacity) init space.
        """
        self.size = 769
        self.buckets = [[] for _ in range(self.size)]

    def _idx(self, key: int) -> int:
        return key % self.size

    def add(self, key: int) -> None:
        """
        Interview explanation:
        Insert key if not already present in its bucket chain.

        Algorithm:
        - Locate bucket; append if missing.

        Complexity: O(n/B) average ~ O(1), O(n) worst.
        """
        b = self.buckets[self._idx(key)]
        if key not in b:
            b.append(key)

    def remove(self, key: int) -> None:
        """
        Interview explanation:
        Remove key from its bucket if present.

        Algorithm:
        - If key in bucket, remove it.

        Complexity: O(n/B) average.
        """
        b = self.buckets[self._idx(key)]
        if key in b:
            b.remove(key)

    def contains(self, key: int) -> bool:
        """
        Interview explanation:
        Membership test via bucket chain scan.

        Algorithm:
        - Return key in bucket.

        Complexity: O(n/B) average.
        """
        return key in self.buckets[self._idx(key)]


# Your MyHashSet object will be instantiated and called as such:
# obj = MyHashSet()
# obj.add(key)
# obj.remove(key)
# param_3 = obj.contains(key)
# @lc code=end
