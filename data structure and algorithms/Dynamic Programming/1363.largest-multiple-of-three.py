#
# @lc app=leetcode id=1363 lang=python3
#
# [1363] Largest Multiple of Three
#
# https://leetcode.com/problems/largest-multiple-of-three/description/
#
# algorithms
# Hard (33.44%)
# Likes:    635
# Dislikes: 92
# Total Accepted:    27.3K
# Total Submissions: 81.5K
# Testcase Example:  "[8,1,9]"
#
# Given an array of digits digits, return the largest multiple of three that
# can be formed by concatenating some of the given digits in any order. If
# there is no answer return an empty string.
#
# Since the answer may not fit in an integer data type, return the answer as a
# string. Note that the returning answer must not contain unnecessary leading
# zeros.
#
# Example 1:
#
# Input: digits = [8,1,9]
# Output: "981"
#
# Example 2:
#
# Input: digits = [8,6,7,1,0]
# Output: "8760"
#
# Example 3:
#
# Input: digits = [1]
# Output: ""
#
# Constraints:
#
# 1 <= digits.length <= 10^4
#
# 0 <= digits[i] <= 9
#

# @lc code=start

from typing import List


class Solution:
    def largestMultipleOfThree(self, digits: List[int]) -> str:
        """
        Interview explanation:
        Largest number divisible by 3 uses as many largest digits as possible
        with digit-sum %3==0. If residue r≠0, drop the smallest digit ≡r, else
        two smallest digits ≡3-r.

        Algorithm:
        - Sort ascending for removals; try remove one then two digits
        - Remaining digits sorted descending form the answer; handle zeros

        Complexity: O(n log n) time, O(n) space.
        """
        digits = sorted(digits)
        s = sum(digits)
        r = s % 3
        if r != 0:
            removed = False
            for i, d in enumerate(digits):
                if d % 3 == r:
                    digits.pop(i)
                    removed = True
                    break
            if not removed:
                need = 2
                new = []
                for d in digits:
                    if need and d % 3 == 3 - r:
                        need -= 1
                        continue
                    new.append(d)
                if need:
                    return ""
                digits = new
        if not digits:
            return ""
        digits.sort(reverse=True)
        if digits[0] == 0:
            return "0"
        return "".join(map(str, digits))
# @lc code=end
