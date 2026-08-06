#
# @lc app=leetcode id=170 lang=python3
#
# [170] Two Sum III - Data structure design
#
# https://leetcode.com/problems/two-sum-iii-data-structure-design/description/
#
# algorithms
# Easy (39.23%)
# Likes:    714
# Dislikes: 462
# Total Accepted:    184.6K
# Total Submissions: 470.5K
# Testcase Example:  "[\"TwoSum\",\"add\",\"add\",\"add\",\"find\",\"find\"]\n[[],[1],[3],[5],[4],[7]]"
#
#
# Design a data structure that accepts a stream of integers and checks if
# it has a pair of integers that sum up to a particular value.
#
# Implement the TwoSum class:
#
# TwoSum() Initializes the TwoSum object, with an empty array initially.
#
# void add(int number) Adds number to the data structure.
#
# boolean find(int value) Returns true if there exists any pair of numbers
# whose sum is equal to value, otherwise, it returns false.
#
# Example 1:
#
# Input
# ["TwoSum", "add", "add", "add", "find", "find"]
# [[], [1], [3], [5], [4], [7]]
# Output
# [null, null, null, null, true, false]
#
# Explanation
# TwoSum twoSum = new TwoSum();
# twoSum.add(1);   // [] --> [1]
# twoSum.add(3);   // [1] --> [1,3]
# twoSum.add(5);   // [1,3] --> [1,3,5]
# twoSum.find(4);  // 1 + 3 = 4, return true
# twoSum.find(7);  // No two integers sum up to 7, return false
#
# Constraints:
#
# -10^5 <= number <= 10^5
#
# -2^31 <= value <= 2^31 - 1
#
# At most 10^4 calls will be made to add and find.
#
# @lc code=start
from collections import defaultdict


class TwoSum:
    """
    Interview explanation:
    Store frequency of each added number in a hash map. find(value) checks
    whether some stored number x has complement value - x also present
    (with multiplicity if x == complement).

    Algorithm:
    - add(number): increment counts[number].
    - find(value): for each num, complement = value - num; succeed if
      complement exists and (complement != num or count[num] > 1).

    Complexity: add O(1); find O(u) for u unique numbers; O(u) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Frequency map of added numbers so find can check complements with
        multiplicity in mind.

        Algorithm:
        - counts: defaultdict(int) mapping value → occurrence count.

        Complexity: O(1) init, O(u) space over the lifetime for u uniques.
        """
        self.counts = defaultdict(int)

    def add(self, number: int) -> None:
        """
        Interview explanation:
        Record one more occurrence of number for later two-sum queries.

        Algorithm:
        - Increment counts[number].

        Complexity: O(1) time, O(1) amortized space.
        """
        self.counts[number] += 1

    def find(self, value: int) -> bool:
        """
        Interview explanation:
        Check whether any stored number and its complement sum to value,
        handling the equal-pair case via count > 1.

        Algorithm:
        - For each num, complement = value - num.
        - Succeed if complement is present and (complement != num or count > 1).

        Complexity: O(u) time for u unique numbers, O(1) extra space.
        """
        for num, count in self.counts.items():
            complement = value - num
            if complement in self.counts and (complement != num or count > 1):
                return True
        return False
# @lc code=end
