#
# @lc app=leetcode id=603 lang=python3
#
# [603] Consecutive Available Seats
#
# https://leetcode.com/problems/consecutive-available-seats/description/
#
# database
# Easy (64.94%)
# Likes:    659
# Dislikes: 80
# Total Accepted:    104.4K
# Total Submissions: 160.7K
# Testcase Example:  "{\"headers\":{\"Cinema\":[\"seat_id\",\"free\"]},\"rows\":{\"Cinema\":[[1,1],[2,0],[3,1],[4,1],[5,1]]}}"
#
#
# Table: Cinema
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | seat_id     | int  |
# | free        | bool |
# +-------------+------+
# seat_id is an auto-increment column for this table.
# Each row of this table indicates whether the i^th seat is free or not. 1
# means free while 0 means occupied.
#
# Find all the consecutive available seats in the cinema.
#
# Return the result table ordered by seat_id in ascending order.
#
# The test cases are generated so that more than two seats are
# consecutively available.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Cinema table:
# +---------+------+
# | seat_id | free |
# +---------+------+
# | 1       | 1    |
# | 2       | 0    |
# | 3       | 1    |
# | 4       | 1    |
# | 5       | 1    |
# +---------+------+
# Output:
# +---------+
# | seat_id |
# +---------+
# | 3       |
# | 4       |
# | 5       |
# +---------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Find free seats that have at least one adjacent free seat (consecutive available).

        Algorithm:
        - Self-join Cinema where |seat_id diff| = 1 and both free = 1.
        - SELECT DISTINCT seat_id ORDER BY seat_id.

        Complexity: O(N) with join/index on seat_id.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT c1.seat_id
    FROM Cinema c1
    JOIN Cinema c2
      ON ABS(c1.seat_id - c2.seat_id) = 1
    WHERE c1.free = 1 AND c2.free = 1
    ORDER BY c1.seat_id;
    """
# @lc code=end
