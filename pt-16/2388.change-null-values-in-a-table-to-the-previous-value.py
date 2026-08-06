#
# @lc app=leetcode id=2388 lang=python3
#
# [2388] Change Null Values in a Table to the Previous Value
#
# https://leetcode.com/problems/change-null-values-in-a-table-to-the-previous-value/description/
#
# database
# Medium (51.29%)
# Likes:    96
# Dislikes: 31
# Total Accepted:    7K
# Total Submissions: 13.7K
# Testcase Example:  "{\"headers\": {\"CoffeeShop\": [\"id\", \"drink\"]}, \"rows\": {\"CoffeeShop\": [[9, \"Rum and Coke\"], [6, null], [7, null], [3, \"St Germain Spritz\"], [1, \"Orange Margarita\"], [2, null]]}}"
#
#
# Table: CoffeeShop
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | id          | int     |
# | drink       | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row in this table shows the order id and the name of the drink
# ordered. Some drink rows are nulls.
#
# Write a solution to replace the null values of the drink with the name
# of the drink of the previous row that is not null. It is guaranteed that
# the drink on the first row of the table is not null.
#
# Return the result table in the same order as the input.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# CoffeeShop table:
# +----+-------------------+
# | id | drink             |
# +----+-------------------+
# | 9  | Rum and Coke      |
# | 6  | null              |
# | 7  | null              |
# | 3  | St Germain Spritz |
# | 1  | Orange Margarita  |
# | 2  | null              |
# +----+-------------------+
# Output:
# +----+-------------------+
# | id | drink             |
# +----+-------------------+
# | 9  | Rum and Coke      |
# | 6  | Rum and Coke      |
# | 7  | Rum and Coke      |
# | 3  | St Germain Spritz |
# | 1  | Orange Margarita  |
# | 2  | Orange Margarita  |
# +----+-------------------+
# Explanation:
# For ID 6, the previous value that is not null is from ID 9. We replace
# the null with "Rum and Coke".
# For ID 7, the previous value that is not null is from ID 9. We replace
# the null with "Rum and Coke;.
# For ID 2, the previous value that is not null is from ID 1. We replace
# the null with "Orange Margarita".
# Note that the rows in the output are the same as in the input.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: CoffeeShop(id, drink) with null drinks. Fill each null
        with previous non-null drink in table order (first row non-null).
        Preserve input order.

        Algorithm:
        - Session variable @cur: when drink non-null assign @cur:=drink else @cur.

        Complexity: O(N).
        """
        self.sql = """
SELECT
  id,
  CASE
    WHEN drink IS NOT NULL THEN @cur := drink
    ELSE @cur
  END AS drink
FROM CoffeeShop;
"""
        return self.sql

    def solve_window(self) -> str:
        """
        Interview explanation:
        Alternate SQL: assign row numbers; group by running count of non-nulls;
        MAX(drink) over group.

        Algorithm:
        - ROW_NUMBER; SUM(drink IS NOT NULL); MAX over partition gid.

        Complexity: O(N).
        """
        self.sql = """
WITH
  S AS (
    SELECT *, ROW_NUMBER() OVER () AS rk
    FROM CoffeeShop
  ),
  T AS (
    SELECT
      *,
      SUM(CASE WHEN drink IS NULL THEN 0 ELSE 1 END) OVER (ORDER BY rk) AS gid
    FROM S
  )
SELECT
  id,
  MAX(drink) OVER (PARTITION BY gid ORDER BY rk) AS drink
FROM T;
"""
        return self.sql
# @lc code=end
