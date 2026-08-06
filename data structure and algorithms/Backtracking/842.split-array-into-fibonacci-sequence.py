#
# @lc app=leetcode id=842 lang=python3
#
# [842] Split Array into Fibonacci Sequence
#
# https://leetcode.com/problems/split-array-into-fibonacci-sequence/description/
#
# algorithms
# Medium (40.35%)
# Likes:    1185
# Dislikes: 310
# Total Accepted:    47.3K
# Total Submissions: 117.3K
# Testcase Example:  '"1101111"'
#
# You are given a string of digits num, such as "123456579". We can split it
# into a Fibonacci-like sequence [123, 456, 579].
# 
# Formally, a Fibonacci-like sequence is a list f of non-negative integers such
# that:
# 
# 
# 0 <= f[i] < 2^31, (that is, each integer fits in a 32-bit signed integer
# type),
# f.length >= 3, and
# f[i] + f[i + 1] == f[i + 2] for all 0 <= i < f.length - 2.
# 
# 
# Note that when splitting the string into pieces, each piece must not have
# extra leading zeroes, except if the piece is the number 0 itself.
# 
# Return any Fibonacci-like sequence split from num, or return [] if it cannot
# be done.
# 
# 
# Example 1:
# 
# 
# Input: num = "1101111"
# Output: [11,0,11,11]
# Explanation: The output [110, 1, 111] would also be accepted.
# 
# 
# Example 2:
# 
# 
# Input: num = "112358130"
# Output: []
# Explanation: The task is impossible.
# 
# 
# Example 3:
# 
# 
# Input: num = "0123"
# Output: []
# Explanation: Leading zeroes are not allowed, so "01", "2", "3" is not
# valid.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= num.length <= 200
# num contains only digits.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def splitIntoFibonacci(self, num: str) -> List[int]:
        ans = []
        LIMIT = 2 ** 31 - 1

        def dfs(pos: int) -> bool:
            if pos == len(num):
                return len(ans) >= 3
            value = 0
            for end in range(pos, len(num)):
                if end > pos and num[pos] == '0':
                    break
                value = value * 10 + int(num[end])
                if value > LIMIT:
                    break
                if len(ans) >= 2:
                    expected = ans[-1] + ans[-2]
                    if value < expected:
                        continue
                    if value > expected:
                        break
                ans.append(value)
                if dfs(end + 1):
                    return True
                ans.pop()
            return False

        dfs(0)
        return ans
# @lc code=end

"""
Interview explanation:
Backtrack over possible next numbers. After two numbers are chosen, every following number is forced to equal the sum of the previous two, which prunes most branches. Stop exploring a number when it exceeds the expected sum or the 32-bit limit.

Data structure: ans is the current Fibonacci-like path.

Edge cases: leading zeros are allowed only for the number 0 itself. A valid sequence must contain at least three numbers. Values must fit in signed 32-bit range.

Complexity: the first two numbers determine the rest, so practical time is O(n^2) choices for their split positions, with O(n) recursion depth/output space.
"""
