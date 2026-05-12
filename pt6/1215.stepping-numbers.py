#
# @lc app=leetcode id=1215 lang=python3
#
# [1215] Stepping Numbers
#
# https://leetcode.com/problems/stepping-numbers/description/
#
# algorithms
# Medium (48.41%)
# Likes:    188
# Dislikes: 21
# Total Accepted:    11.3K
# Total Submissions: 23.3K
# Testcase Example:  '0\n21'
#
# A stepping number is an integer such that all of its adjacent digits have an
# absolute difference of exactly 1.
# 
# 
# For example, 321 is a stepping number while 421 is not.
# 
# 
# Given two integers low and high, return a sorted list of all the stepping
# numbers in the inclusive range [low, high].
# 
# 
# Example 1:
# 
# 
# Input: low = 0, high = 21
# Output: [0,1,2,3,4,5,6,7,8,9,10,12,21]
# 
# 
# Example 2:
# 
# 
# Input: low = 10, high = 15
# Output: [10,12]
# 
# 
# 
# Constraints:
# 
# 
# 0 <= low <= high <= 2 * 10^9
# 
# 
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def countSteppingNumbers(self, low: int, high: int) -> List[int]:
        ans = []
        queue = deque(range(10))

        while queue:
            num = queue.popleft()

            if num > high:
                continue
            if num >= low:
                ans.append(num)

            if num == 0:
                continue

            last = num % 10
            if last > 0:
                queue.append(num * 10 + last - 1)
            if last < 9:
                queue.append(num * 10 + last + 1)

        return sorted(ans)
# @lc code=end

# Explanation
# -----------
# A stepping number can be generated from its last digit: if the last digit is
# d, the next digit may be d - 1 or d + 1. Start BFS from digits 0 through 9,
# append valid numbers in range, and stop extending a branch once it exceeds
# high.
#
# BFS is a natural data structure choice because each queue item is a valid
# stepping-number prefix. We never generate invalid candidates, unlike scanning
# every integer from low to high.
#
# Zero is special: it is a valid answer when low <= 0, but we do not extend it
# to 01 or similar leading-zero numbers.
#
# Edge cases: ranges containing 0; high below 10; last digit 0 only extends to
# 1, and last digit 9 only extends to 8. The final sort gives increasing order
# because BFS from multiple roots can produce values slightly out of order.
#
# Time complexity: O(k log k), where k is the number of generated stepping
# numbers up to high. Space complexity: O(k).
