#
# @lc app=leetcode id=390 lang=python3
#
# [390] Elimination Game
#
# https://leetcode.com/problems/elimination-game/description/
#
# algorithms
# Medium (46.32%)
# Likes:    1748
# Dislikes: 763
# Total Accepted:    108.6K
# Total Submissions: 234.5K
# Testcase Example:  '9'
#
# You have a list arr of all integers in the range [1, n] sorted in a strictly
# increasing order. Apply the following algorithm on arr:
# 
# 
# Starting from left to right, remove the first number and every other number
# afterward until you reach the end of the list.
# Repeat the previous step again, but this time from right to left, remove the
# rightmost number and every other number from the remaining numbers.
# Keep repeating the steps again, alternating left to right and right to left,
# until a single number remains.
# 
# 
# Given the integer n, return the last number that remains in arr.
# 
# 
# Example 1:
# 
# 
# Input: n = 9
# Output: 6
# Explanation:
# arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]
# arr = [2, 4, 6, 8]
# arr = [2, 6]
# arr = [6]
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^9
# 
# 
#

# @lc code=start
class Solution:
    def lastRemaining(self, n: int) -> int:
        head = 1
        step = 1
        remaining = n
        left_to_right = True

        while remaining > 1:
            if left_to_right or remaining % 2 == 1:
                head += step
            remaining //= 2
            step *= 2
            left_to_right = not left_to_right
        return head
# @lc code=end

"""
Interview explanation:
Track only the first remaining number, the gap between remaining numbers, the count left, and the current direction. A full list is unnecessary. After each deletion round, the gap doubles and the count halves. The first number moves whenever we delete left-to-right, and also when deleting right-to-left with an odd count.

Why this works: after every round the remaining sequence is still arithmetic, so head + k * step fully describes it.

Edge cases: n = 1 skips the loop and returns 1. Odd counts on right-to-left rounds advance the head because the leftmost element is also removed.

Complexity: the count halves each round, giving O(log n) time and O(1) space.
"""
