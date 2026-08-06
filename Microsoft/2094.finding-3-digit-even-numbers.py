#
# @lc app=leetcode id=2094 lang=python3
#
# [2094] Finding 3-Digit Even Numbers
#
# https://leetcode.com/problems/finding-3-digit-even-numbers/description/
#
# algorithms
# Easy (78.62%)
# Likes:    1610
# Dislikes: 346
# Total Accepted:    190.2K
# Total Submissions: 241.9K
# Testcase Example:  "[2,1,3,0]"
#
# You are given an integer array digits, where each element is a digit. The
# array may contain duplicates.
#
# You need to find all the unique integers that follow the given requirements:
#
#
# The integer consists of the concatenation of three elements from digits in any
# arbitrary order.
#
#
# The integer does not have leading zeros.
#
#
# The integer is even.
#
# For example, if the given digits were [1, 2, 3], integers 132 and 312 follow
# the requirements.
#
# Return a sorted array of the unique integers.
#
#
#
# Example 1:
#
# Input: digits = [2,1,3,0]
# Output: [102,120,130,132,210,230,302,310,312,320]
# Explanation: All the possible integers that follow the requirements are in the
# output array.
# Notice that there are no odd integers or integers with leading zeros.
#
# Example 2:
#
# Input: digits = [2,2,8,8,2]
# Output: [222,228,282,288,822,828,882]
# Explanation: The same digit can be used as many times as it appears in digits.
# In this example, the digit 8 is used twice each time in 288, 828, and 882.
#
# Example 3:
#
# Input: digits = [3,7,5]
# Output: []
# Explanation: No even integers can be formed using the given digits.
#
#
#
# Constraints:
#
#
# 3 <= digits.length <= 100
#
#
# 0 <= digits[i] <= 9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def findEvenNumbers(self, digits: List[int]) -> List[int]:
        """
        Interview explanation:
        Form all unique 3-digit even numbers using digits without exceeding
        frequencies; no leading zero. Return sorted.

        Algorithm:
        - Enumerate hundreds/tens/units with counters, units even.

        Complexity: O(1) for digit space (900 candidates) / O(n) to count.
        """
        cnt = Counter(digits)
        ans = []
        for a in range(1, 10):
            if cnt[a] == 0:
                continue
            cnt[a] -= 1
            for b in range(10):
                if cnt[b] == 0:
                    continue
                cnt[b] -= 1
                for c in range(0, 10, 2):
                    if cnt[c]:
                        ans.append(100 * a + 10 * b + c)
                cnt[b] += 1
            cnt[a] += 1
        return ans
# @lc code=end
