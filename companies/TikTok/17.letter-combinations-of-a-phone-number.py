#
# @lc app=leetcode id=17 lang=python3
#
# [17] Letter Combinations of a Phone Number
#
# https://leetcode.com/problems/letter-combinations-of-a-phone-number/description/
#
# algorithms
# Medium (65.99%)
# Likes:    21019
# Dislikes: 1137
# Total Accepted:    3M
# Total Submissions: 4.6M
# Testcase Example:  '"23"'
#
# Given a string containing digits from 2-9 inclusive, return all possible
# letter combinations that the number could represent. Return the answer in any
# order.
# 
# A mapping of digits to letters (just like on the telephone buttons) is given
# below. Note that 1 does not map to any letters.
# 
# 
# Example 1:
# 
# 
# Input: digits = "23"
# Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]
# 
# 
# Example 2:
# 
# 
# Input: digits = "2"
# Output: ["a","b","c"]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= digits.length <= 4
# digits[i] is a digit in the range ['2', '9'].
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        """
        Interview explanation:
        Each digit represents a small set of choices, so this is a classic
        backtracking/cartesian-product problem. The path list stores the current
        partial string; when its length equals the number of digits, it becomes
        one answer.

        Edge cases and tests:
        - Empty input returns [] by problem convention.
        - Digits 7 and 9 have four choices; others have three.
        - Ordering follows the phone mapping and input order.

        Complexity: O(4^n * n) time to build strings, O(n) recursion space plus
        output size.
        """
        if not digits:
            return []

        phone = {
            '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
            '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz',
        }
        ans = []
        path = []

        def backtrack(index: int) -> None:
            if index == len(digits):
                ans.append(''.join(path))
                return
            for ch in phone[digits[index]]:
                path.append(ch)
                backtrack(index + 1)
                path.pop()

        backtrack(0)
        return ans
# @lc code=end


