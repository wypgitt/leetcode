#
# @lc app=leetcode id=381 lang=python3
#
# [381] Insert Delete GetRandom O(1) - Duplicates allowed
#
# https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/description/
#
# algorithms
# Hard (36.84%)
# Likes:    2446
# Dislikes: 160
# Total Accepted:    196K
# Total Submissions: 531K
# Testcase Example:  "[\"RandomizedCollection\",\"insert\",\"insert\",\"insert\",\"getRandom\",\"remove\",\"getRandom\"]"
#
# RandomizedCollection is a data structure that contains a collection of
# numbers, possibly duplicates (i.e., a multiset). It should support inserting
# and removing specific elements and also reporting a random element.
#
# Implement the RandomizedCollection class:
#
# RandomizedCollection() Initializes the empty RandomizedCollection object.
#
# bool insert(int val) Inserts an item val into the multiset, even if the item
# is already present. Returns true if the item is not present, false otherwise.
#
# bool remove(int val) Removes an item val from the multiset if present.
# Returns true if the item is present, false otherwise. Note that if val has
# multiple occurrences in the multiset, we only remove one of them.
#
# int getRandom() Returns a random element from the current multiset of
# elements. The probability of each element being returned is linearly related
# to the number of the same values the multiset contains.
#
# You must implement the functions of the class such that each function works
# on average O(1) time complexity.
#
# Note: The test cases are generated such that getRandom will only be called if
# there is at least one item in the RandomizedCollection.
#
# Example 1:
#
# Input
# ["RandomizedCollection", "insert", "insert", "insert", "getRandom", "remove",
# "getRandom"]
# [[], [1], [1], [2], [], [1], []]
# Output
# [null, true, false, true, 2, true, 1]
#
# Explanation
# RandomizedCollection randomizedCollection = new RandomizedCollection();
# randomizedCollection.insert(1); // return true since the collection does not
# contain 1.
# // Inserts 1 into the collection.
# randomizedCollection.insert(1); // return false since the collection contains
# 1.
# // Inserts another 1 into the collection. Collection now contains [1,1].
# randomizedCollection.insert(2); // return true since the collection does not
# contain 2.
# // Inserts 2 into the collection. Collection now contains [1,1,2].
# randomizedCollection.getRandom(); // getRandom should:
# // - return 1 with probability 2/3, or
# // - return 2 with probability 1/3.
# randomizedCollection.remove(1); // return true since the collection contains
# 1.
# // Removes 1 from the collection. Collection now contains [1,2].
# randomizedCollection.getRandom(); // getRandom should return 1 or 2, both
# equally likely.
#
# Constraints:
#
# -2^31 <= val <= 2^31 - 1
#
# At most 2 * 10^5 calls in total will be made to insert, remove, and
# getRandom.
#
# There will be at least one element in the data structure when getRandom is
# called.
#

# @lc code=start
import random
from collections import defaultdict


class RandomizedCollection:
    """
    Interview explanation:
    Multiset with O(1) avg insert/remove/getRandom: list of values + map from
    value → set of indices in the list. Remove swaps with last index carefully.

    Algorithm:
    - insert: append val; add new index to idx[val]; return whether first copy.
    - remove: take any index of val; swap with last; update index sets; pop.
    - getRandom: random.choice(vals) — frequency-weighted automatically.

    Complexity: amortized O(1) per op, O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Multiset: list of values plus map from value → set of indices so
        duplicates and O(1) swap-remove both work.

        Algorithm:
        - vals = []; idx = defaultdict(set).

        Complexity: O(1) init, O(n) space for n elements (with multiplicity).
        """
        self.vals = []
        self.idx = defaultdict(set)

    def insert(self, val: int) -> bool:
        """
        Interview explanation:
        Always append a new copy; return whether this was the first occurrence.

        Algorithm:
        - Add len(vals) into idx[val]; append val; return len(idx[val]) == 1.

        Complexity: Amortized O(1) time, O(1) amortized space.
        """
        self.idx[val].add(len(self.vals))
        self.vals.append(val)
        return len(self.idx[val]) == 1

    def remove(self, val: int) -> bool:
        """
        Interview explanation:
        Remove one occurrence: swap that index with the last element, carefully
        updating both values' index sets, then pop.

        Algorithm:
        - Pop any index i of val; move last into i; fix idx[last]; pop list;
          delete empty idx[val].

        Complexity: Amortized O(1) time, O(1) space.
        """
        if not self.idx[val]:
            return False
        i = self.idx[val].pop()
        last = self.vals[-1]
        self.vals[i] = last
        self.idx[last].add(i)
        self.idx[last].discard(len(self.vals) - 1)
        self.vals.pop()
        if not self.idx[val]:
            del self.idx[val]
        return True

    def getRandom(self) -> int:
        """
        Interview explanation:
        Uniform over list slots — automatically frequency-weighted for duplicates.

        Algorithm:
        - Return random.choice(vals).

        Complexity: O(1) time, O(1) space.
        """
        return random.choice(self.vals)


# Your RandomizedCollection object will be instantiated and called as such:
# obj = RandomizedCollection()
# param_1 = obj.insert(val)
# param_2 = obj.remove(val)
# param_3 = obj.getRandom()
# @lc code=end
