#
# @lc app=leetcode id=3491 lang=python3
#
# [3491] Phone Number Prefix
#
# https://leetcode.com/problems/phone-number-prefix/description/
#
# algorithms
# Easy (69.84%)
# Likes:    11
# Dislikes: 1
# Total Accepted:    2.1K
# Total Submissions: 3K
# Testcase Example:  "[\"1\",\"2\",\"4\",\"3\"]"
#
#
# You are given a string array numbers that represents phone numbers.
# Return true if no phone number is a prefix of any other phone number;
# otherwise, return false.
#
# Example 1:
#
# Input: numbers = ["1","2","4","3"]
#
# Output: true
#
# Explanation:
#
# No number is a prefix of another number, so the output is true.
#
# Example 2:
#
# Input: numbers = ["001","007","15","00153"]
#
# Output: false
#
# Explanation:
#
# The string "001" is a prefix of the string "00153". Thus, the output is
# false.
#
# Constraints:
#
# 2 <= numbers.length <= 50
#
# 1 <= numbers[i].length <= 50
#
# All numbers contain only digits '0' to '9'.
#

# @lc code=start
from typing import List


class Solution:
    def phonePrefix(self, numbers: List[str]) -> bool:
        """
        Interview explanation:
        Return false iff some number is a prefix of another.

        Algorithm:
        - Sort lexicographically; then a prefix of another must be adjacent
          (only need to check numbers[i] vs numbers[i+1].startswith(...)).

        Complexity: O(n log n * L) time, O(1) extra space.
        """
        numbers = sorted(numbers)
        for i in range(len(numbers) - 1):
            if numbers[i + 1].startswith(numbers[i]):
                return False
        return True

    def phonePrefix_trie(self, numbers: List[str]) -> bool:
        """
        Interview explanation:
        Alternate: insert into a trie; fail if we pass through / end on a
        terminal, or a new number ends inside an existing path that continues.

        Algorithm:
        - Trie with end marks; check conflicts on insert.

        Complexity: O(Σ lengths) time/space.
        """
        root = {}
        for num in numbers:
            node = root
            for i, c in enumerate(num):
                if c not in node:
                    node[c] = {}
                node = node[c]
                if node.get('$'):
                    return False
                if i == len(num) - 1 and node:
                    # ends here but path continues with other digits
                    if any(k != '$' for k in node):
                        return False
            if any(k != '$' for k in node):
                return False
            node['$'] = True
        return True
# @lc code=end
