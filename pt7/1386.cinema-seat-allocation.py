#
# @lc app=leetcode id=1386 lang=python3
#
# [1386] Cinema Seat Allocation
#
# https://leetcode.com/problems/cinema-seat-allocation/description/
#
# algorithms
# Medium (44.48%)
# Likes:    994
# Dislikes: 418
# Total Accepted:    65.9K
# Total Submissions: 148K
# Testcase Example:  '3\n[[1,2],[1,3],[1,8],[2,6],[3,1],[3,10]]'
#
# 
# 
# A cinema has n rows of seats, numbered from 1 to n and there are ten seats in
# each row, labelled from 1 to 10 as shown in the figure above.
# 
# Given the array reservedSeats containing the numbers of seats already
# reserved, for example, reservedSeats[i] = [3,8] means the seat located in row
# 3 and labelled with 8 is already reserved.
# 
# Return the maximum number of four-person groups you can assign on the cinema
# seats. A four-person group occupies four adjacent seats in one single row.
# Seats across an aisle (such as [3,3] and [3,4]) are not considered to be
# adjacent, but there is an exceptional case on which an aisle split a
# four-person group, in that case, the aisle split a four-person group in the
# middle, which means to have two people on each side.
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: n = 3, reservedSeats = [[1,2],[1,3],[1,8],[2,6],[3,1],[3,10]]
# Output: 4
# Explanation: The figure above shows the optimal allocation for four groups,
# where seats mark with blue are already reserved and contiguous seats mark
# with orange are for one group.
# 
# 
# Example 2:
# 
# 
# Input: n = 2, reservedSeats = [[2,1],[1,8],[2,6]]
# Output: 2
# 
# 
# Example 3:
# 
# 
# Input: n = 4, reservedSeats = [[4,3],[1,4],[4,6],[1,7]]
# Output: 4
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^9
# 1 <= reservedSeats.length <= min(10*n, 10^4)
# reservedSeats[i].length == 2
# 1 <= reservedSeats[i][0] <= n
# 1 <= reservedSeats[i][1] <= 10
# All reservedSeats[i] are distinct.
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import defaultdict
from typing import List


class Solution:
    def maxNumberOfFamilies(self, n: int, reservedSeats: List[List[int]]) -> int:
        reserved_by_row = defaultdict(int)

        for row, seat in reservedSeats:
            if 2 <= seat <= 9:
                reserved_by_row[row] |= 1 << (seat - 2)

        left_block = 0b00001111   # seats 2, 3, 4, 5
        middle_block = 0b00111100 # seats 4, 5, 6, 7
        right_block = 0b11110000  # seats 6, 7, 8, 9

        families = (n - len(reserved_by_row)) * 2

        for mask in reserved_by_row.values():
            can_left = (mask & left_block) == 0
            can_right = (mask & right_block) == 0

            if can_left and can_right:
                families += 2
            elif can_left or can_right or (mask & middle_block) == 0:
                families += 1

        return families
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Each row can seat at most two four-person families: seats 2-5 and 6-9. If
# those are blocked, one family might still fit in the middle block 4-7. Seats
# 1 and 10 never matter for a four-person family.
#
# Data structure:
# Use an 8-bit mask per row for seats 2 through 9. A 1 bit means that seat is
# reserved.
#
# Walkthrough:
# 1. Build reservation masks only for seats 2..9.
# 2. Rows without any relevant reservations contribute 2 families immediately.
# 3. For each reserved row, test the left, right, and middle four-seat blocks.
# 4. Add 2 if left and right are both free; otherwise add 1 if any valid block
#    is free.
#
# Edge cases:
# - Reservations in seats 1 or 10: ignored.
# - No reservations in a row: counted by the base formula.
# - Middle block is only used when two side families cannot both fit.
#
# Complexity:
# - Time: O(r), where r is number of reserved seats.
# - Space: O(min(n, r)), one mask per row with relevant reservations.
