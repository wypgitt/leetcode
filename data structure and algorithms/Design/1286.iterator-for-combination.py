#
# @lc app=leetcode id=1286 lang=python3
#
# [1286] Iterator for Combination
#
# https://leetcode.com/problems/iterator-for-combination/description/
#
# algorithms
# Medium (72.71%)
# Likes:    1397
# Dislikes: 109
# Total Accepted:    83.7K
# Total Submissions: 115K
# Testcase Example:  "[\"CombinationIterator\",\"next\",\"hasNext\",\"next\",\"hasNext\",\"next\",\"hasNext\"]"
#
# Design the CombinationIterator class:
#
# CombinationIterator(string characters, int combinationLength) Initializes the
# object with a string characters of sorted distinct lowercase English letters
# and a number combinationLength as arguments.
#
# next() Returns the next combination of length combinationLength in
# lexicographical order.
#
# hasNext() Returns true if and only if there exists a next combination.
#
# Example 1:
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
# itr.next(); // return "ab"
# itr.hasNext(); // return True
# itr.next(); // return "ac"
# itr.hasNext(); // return True
# itr.next(); // return "bc"
# itr.hasNext(); // return False
#
# Constraints:
#
# 1 <= combinationLength <= characters.length <= 15
#
# All the characters of characters are unique.
#
# At most 10^4 calls will be made to next and hasNext.
#
# It is guaranteed that all calls of the function next are valid.
#

# @lc code=start

from itertools import combinations


class CombinationIterator:
    def __init__(self, characters: str, combinationLength: int):
        """
        Interview explanation:
        Precompute all length-k combinations of sorted distinct characters in
        lex order (itertools.combinations already does), store as list/index
        cursor. characters already sorted per problem statement.

        Algorithm:
        - combos = list(combinations(characters, combinationLength)) joined.
        - idx = 0.

        Complexity: O(C(n,k)*k) init time/space.
        """
        self.combos = ["".join(c) for c in combinations(characters, combinationLength)]
        self.idx = 0

    def next(self) -> str:
        """
        Interview explanation:
        Return next combination and advance cursor. Guaranteed valid.

        Algorithm:
        - ans = combos[idx]; idx += 1; return ans.

        Complexity: O(1) time (string already built).
        """
        ans = self.combos[self.idx]
        self.idx += 1
        return ans

    def hasNext(self) -> bool:
        """
        Interview explanation:
        True iff unused combinations remain.

        Algorithm:
        - return idx < len(combos)

        Complexity: O(1) time.
        """
        return self.idx < len(self.combos)


# Your CombinationIterator object will be instantiated and called as such:
# obj = CombinationIterator(characters, combinationLength)
# param_1 = obj.next()
# param_2 = obj.hasNext()
# @lc code=end
