#
# @lc app=leetcode id=380 lang=python3
#
# [380] Insert Delete GetRandom O(1)
#
# https://leetcode.com/problems/insert-delete-getrandom-o1/description/
#
# algorithms
# Medium (55.47%)
# Likes:    10036
# Dislikes: 699
# Total Accepted:    1.4M
# Total Submissions: 2.5M
# Testcase Example:  "[\"RandomizedSet\",\"insert\",\"remove\",\"insert\",\"getRandom\",\"remove\",\"insert\",\"getRandom\"]"
#
# Implement the RandomizedSet class:
#
# RandomizedSet() Initializes the RandomizedSet object.
#
# bool insert(int val) Inserts an item val into the set if not present. Returns
# true if the item was not present, false otherwise.
#
# bool remove(int val) Removes an item val from the set if present. Returns
# true if the item was present, false otherwise.
#
# int getRandom() Returns a random element from the current set of elements
# (it's guaranteed that at least one element exists when this method is
# called). Each element must have the same probability of being returned.
#
# You must implement the functions of the class such that each function works
# in average O(1) time complexity.
#
# Example 1:
#
# Input
# ["RandomizedSet", "insert", "remove", "insert", "getRandom", "remove",
# "insert", "getRandom"]
# [[], [1], [2], [2], [], [1], [2], []]
# Output
# [null, true, false, true, 2, true, false, 2]
#
# Explanation
# RandomizedSet randomizedSet = new RandomizedSet();
# randomizedSet.insert(1); // Inserts 1 to the set. Returns true as 1 was
# inserted successfully.
# randomizedSet.remove(2); // Returns false as 2 does not exist in the set.
# randomizedSet.insert(2); // Inserts 2 to the set, returns true. Set now
# contains [1,2].
# randomizedSet.getRandom(); // getRandom() should return either 1 or 2
# randomly.
# randomizedSet.remove(1); // Removes 1 from the set, returns true. Set now
# contains [2].
# randomizedSet.insert(2); // 2 was already in the set, so return false.
# randomizedSet.getRandom(); // Since 2 is the only number in the set,
# getRandom() will always return 2.
#
# Constraints:
#
# -2^31 <= val <= 2^31 - 1
#
# At most 2 * 10^5 calls will be made to insert, remove, and getRandom.
#
# There will be at least one element in the data structure when getRandom is
# called.
#

# @lc code=start
import random


class RandomizedSet:
    """
    Interview explanation:
    O(1) insert/remove/getRandom via dynamic array + value→index map.
    Remove swaps the target with the last element, then pops — avoids O(n) shift.

    Algorithm:
    - insert: if absent, append to list and record index; return True.
    - remove: swap with last, update last's index, pop, delete from map.
    - getRandom: random.choice(list).

    Complexity: amortized O(1) per op, O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Dynamic array of values plus value→index map for O(1) locate-and-swap
        removal.

        Algorithm:
        - vals = []; idx = {}.

        Complexity: O(1) init, O(n) space for n elements.
        """
        self.vals = []
        self.idx = {}

    def insert(self, val: int) -> bool:
        """
        Interview explanation:
        Insert if absent: append to list and record its index.

        Algorithm:
        - If val in idx: False; else idx[val]=len(vals), append, True.

        Complexity: Amortized O(1) time, O(1) amortized space.
        """
        if val in self.idx:
            return False
        self.idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        """
        Interview explanation:
        Swap-with-last then pop so removal stays O(1) without shifting.

        Algorithm:
        - Locate i; move last into i and update its index; pop; delete val from idx.

        Complexity: O(1) time, O(1) space.
        """
        if val not in self.idx:
            return False
        i = self.idx[val]
        last = self.vals[-1]
        self.vals[i] = last
        self.idx[last] = i
        self.vals.pop()
        del self.idx[val]
        return True

    def getRandom(self) -> int:
        """
        Interview explanation:
        Uniform random element via random index into the dense array.

        Algorithm:
        - Return random.choice(vals).

        Complexity: O(1) time, O(1) space.
        """
        return random.choice(self.vals)


# Your RandomizedSet object will be instantiated and called as such:
# obj = RandomizedSet()
# param_1 = obj.insert(val)
# param_2 = obj.remove(val)
# param_3 = obj.getRandom()
# @lc code=end
