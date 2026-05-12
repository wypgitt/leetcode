#
# @lc app=leetcode id=1286 lang=python3
#
# [1286] Iterator for Combination
#
# https://leetcode.com/problems/iterator-for-combination/description/
#
# algorithms
# Medium (72.64%)
# Likes:    1395
# Dislikes: 109
# Total Accepted:    82.8K
# Total Submissions: 113.9K
# Testcase Example:  '["CombinationIterator","next","hasNext","next","hasNext","next","hasNext"]\n' +
# '[["abc",2],[],[],[],[],[],[]]'
#
# Design the CombinationIterator class:
# 
# 
# CombinationIterator(string characters, int combinationLength) Initializes the
# object with a string characters of sorted distinct lowercase English letters
# and a number combinationLength as arguments.
# next() Returns the next combination of length combinationLength in
# lexicographical order.
# hasNext() Returns true if and only if there exists a next combination.
# 
# 
# 
# Example 1:
# 
# 
# Input
# ["CombinationIterator", "next", "hasNext", "next", "hasNext", "next",
# "hasNext"]
# [["abc", 2], [], [], [], [], [], []]
# Output
# [null, "ab", true, "ac", true, "bc", false]
# 
# Explanation
# CombinationIterator itr = new CombinationIterator("abc", 2);
# itr.next();    // return "ab"
# itr.hasNext(); // return True
# itr.next();    // return "ac"
# itr.hasNext(); // return True
# itr.next();    // return "bc"
# itr.hasNext(); // return False
# 
# 
# 
# Constraints:
# 
# 
# 1 <= combinationLength <= characters.length <= 15
# All the characters of characters are unique.
# At most 10^4 calls will be made to next and hasNext.
# It is guaranteed that all calls of the function next are valid.
# 
# 
#

# @lc code=start
from itertools import combinations


class CombinationIterator:

    def __init__(self, characters: str, combinationLength: int):
        self.combinations = ["".join(combo) for combo in combinations(characters, combinationLength)]
        self.index = 0

    def next(self) -> str:
        combination = self.combinations[self.index]
        self.index += 1
        return combination

    def hasNext(self) -> bool:
        return self.index < len(self.combinations)


# Your CombinationIterator object will be instantiated and called as such:
# obj = CombinationIterator(characters, combinationLength)
# param_1 = obj.next()
# param_2 = obj.hasNext()
# @lc code=end

# Explanation
# -----------
# itertools.combinations emits combinations in lexicographic order when the
# input characters are sorted, which the problem guarantees. Precompute those
# strings and keep an index into the list.
#
# Precomputation is a clean design choice for the constraints: next and
# hasNext become simple O(1) operations, and the maximum number of combinations
# is small enough for memory.
#
# Edge cases: only one combination; repeated hasNext calls do not advance the
# iterator; next advances exactly once.
#
# Constructor time/space: O(C * L), where C is the number of combinations and L
# is combinationLength.
# next: O(1) to return the stored string. hasNext: O(1).
