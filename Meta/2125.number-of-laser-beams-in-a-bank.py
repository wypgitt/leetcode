#
# @lc app=leetcode id=2125 lang=python3
#
# [2125] Number of Laser Beams in a Bank
#
# https://leetcode.com/problems/number-of-laser-beams-in-a-bank/description/
#
# algorithms
# Medium (86.97%)
# Likes:    2256
# Dislikes: 223
# Total Accepted:    354.3K
# Total Submissions: 407.3K
# Testcase Example:  "[\"011001\",\"000000\",\"010100\",\"001000\"]"
#
# Anti-theft security devices are activated inside a bank. You are given a
# 0-indexed binary string array bank representing the floor plan of the bank,
# which is an m x n 2D matrix. bank[i] represents the i^th row, consisting of
# '0's and '1's. '0' means the cell is empty, while'1' means the cell has a
# security device.
#
# There is one laser beam between any two security devices if both conditions
# are met:
#
#
# The two devices are located on two different rows: r_1 and r_2, where r_1 <
# r_2.
#
#
# For each row i where r_1 < i < r_2, there are no security devices in the i^th
# row.
#
# Laser beams are independent, i.e., one beam does not interfere nor join with
# another.
#
# Return the total number of laser beams in the bank.
#
#
#
# Example 1:
#
# Input: bank = ["011001","000000","010100","001000"]
# Output: 8
# Explanation: Between each of the following device pairs, there is one beam. In
# total, there are 8 beams:
#  * bank[0][1] -- bank[2][1]
#  * bank[0][1] -- bank[2][3]
#  * bank[0][2] -- bank[2][1]
#  * bank[0][2] -- bank[2][3]
#  * bank[0][5] -- bank[2][1]
#  * bank[0][5] -- bank[2][3]
#  * bank[2][1] -- bank[3][2]
#  * bank[2][3] -- bank[3][2]
# Note that there is no beam between any device on the 0^th row with any on the
# 3^rd row.
# This is because the 2^nd row contains security devices, which breaks the
# second condition.
#
# Example 2:
#
# Input: bank = ["000","111","000"]
# Output: 0
# Explanation: There does not exist two devices located on two different rows.
#
#
#
# Constraints:
#
#
# m == bank.length
#
#
# n == bank[i].length
#
#
# 1 <= m, n <= 500
#
#
# bank[i][j] is either '0' or '1'.
#


# @lc code=start
from typing import List


class Solution:
    def numberOfBeams(self, bank: List[str]) -> int:
        """
        Interview explanation:
        Beam between security devices on two different rows if no devices on
        rows between them. Total beams = sum over consecutive non-empty rows
        of count[i]*count[j].

        Algorithm:
        - Count '1's per row; skip empty; multiply consecutive nonzero counts.

        Complexity: O(mn) time, O(1) space.
        """
        ans = 0
        prev = 0
        for row in bank:
            cur = row.count('1')
            if cur:
                ans += prev * cur
                prev = cur
        return ans
# @lc code=end

