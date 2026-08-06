#
# @lc app=leetcode id=3483 lang=python3
#
# [3483] Unique 3-Digit Even Numbers
#
# https://leetcode.com/problems/unique-3-digit-even-numbers/description/
#
# algorithms
# Easy (70.34%)
# Likes:    138
# Dislikes: 34
# Total Accepted:    49.9K
# Total Submissions: 71K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given an array of digits called digits. Your task is to
# determine the number of distinct three-digit even numbers that can be
# formed using these digits.
#
# Note: Each copy of a digit can only be used once per number, and there
# may not be leading zeros.
#
# Example 1:
#
# Input: digits = [1,2,3,4]
#
# Output: 12
#
# Explanation: The 12 distinct 3-digit even numbers that can be formed are
# 124, 132, 134, 142, 214, 234, 312, 314, 324, 342, 412, and 432. Note
# that 222 cannot be formed because there is only 1 copy of the digit 2.
#
# Example 2:
#
# Input: digits = [0,2,2]
#
# Output: 2
#
# Explanation: The only 3-digit even numbers that can be formed are 202
# and 220. Note that the digit 2 can be used twice because it appears
# twice in the array.
#
# Example 3:
#
# Input: digits = [6,6,6]
#
# Output: 1
#
# Explanation: Only 666 can be formed.
#
# Example 4:
#
# Input: digits = [1,3,5]
#
# Output: 0
#
# Explanation: No even 3-digit numbers can be formed.
#
# Constraints:
#
# 3 <= digits.length <= 10
#
# 0 <= digits[i] <= 9
#

# @lc code=start
from typing import List
from itertools import permutations


class Solution:
    def totalNumbers(self, digits: List[int]) -> int:
        """
        Interview explanation:
        Form distinct 3-digit even numbers without leading zeros, using each
        copy of a digit at most once (multiset).

        Algorithm:
        - Triple loop over distinct indices; keep even units and non-zero
          hundreds; store formed numbers in a set.

        Complexity: O(n^3) time (n ≤ 10), O(#answers) space.
        """
        seen = set()
        n = len(digits)
        for i in range(n):
            if digits[i] == 0:
                continue
            for j in range(n):
                if j == i:
                    continue
                for k in range(n):
                    if k == i or k == j:
                        continue
                    if digits[k] % 2 == 0:
                        seen.add(digits[i] * 100 + digits[j] * 10 + digits[k])
        return len(seen)

    def totalNumbers_permutations(self, digits: List[int]) -> int:
        """
        Interview explanation:
        Alternate: itertools.permutations over the multiset of digits.

        Algorithm:
        - Unique permutations of length 3; filter leading zero / odd units.

        Complexity: O(n P 3) time, O(#answers) space.
        """
        seen = set()
        for a, b, c in permutations(digits, 3):
            if a != 0 and c % 2 == 0:
                seen.add(a * 100 + b * 10 + c)
        return len(seen)
# @lc code=end
