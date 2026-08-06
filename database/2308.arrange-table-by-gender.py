#
# @lc app=leetcode id=2308 lang=python3
#
# [2308] Arrange Table by Gender
#
# https://leetcode.com/problems/arrange-table-by-gender/description/
#
# database
# Medium (70.94%)
# Likes:    91
# Dislikes: 15
# Total Accepted:    8.9K
# Total Submissions: 12.5K
# Testcase Example:  "{\"headers\": {\"Genders\": [\"user_id\", \"gender\"]}, \"rows\": {\"Genders\": [[4, \"male\"], [7, \"female\"], [2, \"other\"], [5, \"male\"], [3, \"female\"], [8, \"male\"], [6, \"other\"], [1, \"other\"], [9, \"female\"]]}}"
#
#
# Table: Genders
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | gender      | varchar |
# +-------------+---------+
# user_id is the primary key (column with unique values) for this table.
# gender is ENUM (category) of type 'female', 'male', or 'other'.
# Each row in this table contains the ID of a user and their gender.
# The table has an equal number of 'female', 'male', and 'other'.
#
# Write a solution to rearrange the Genders table such that the rows
# alternate between 'female', 'other', and 'male' in order. The table
# should be rearranged such that the IDs of each gender are sorted in
# ascending order.
#
# Return the result table in the mentioned order.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# Genders table:
# +---------+--------+
# | user_id | gender |
# +---------+--------+
# | 4       | male   |
# | 7       | female |
# | 2       | other  |
# | 5       | male   |
# | 3       | female |
# | 8       | male   |
# | 6       | other  |
# | 1       | other  |
# | 9       | female |
# +---------+--------+
# Output:
# +---------+--------+
# | user_id | gender |
# +---------+--------+
# | 3       | female |
# | 1       | other  |
# | 4       | male   |
# | 7       | female |
# | 2       | other  |
# | 5       | male   |
# | 9       | female |
# | 6       | other  |
# | 8       | male   |
# +---------+--------+
# Explanation:
# Female gender: IDs 3, 7, and 9.
# Other gender: IDs 1, 2, and 6.
# Male gender: IDs 4, 5, and 8.
# We arrange the table alternating between 'female', 'other', and 'male'.
# Note that the IDs of each gender are sorted in ascending order.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Genders(user_id, gender) with equal counts of female/other/male.
        Rearrange rows alternating female, other, male; IDs ascending within
        each gender.

        Algorithm:
        - RANK() per gender by user_id; order by that rank then gender order
          (female=0, other=1, male=2).

        Complexity: O(N log N).
        """
        self.sql = """
WITH t AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY gender ORDER BY user_id) AS rk1,
        CASE
            WHEN gender = 'female' THEN 0
            WHEN gender = 'other' THEN 1
            ELSE 2
        END AS rk2
    FROM Genders
)
SELECT user_id, gender
FROM t
ORDER BY rk1, rk2;
"""
        return self.sql
# @lc code=end
