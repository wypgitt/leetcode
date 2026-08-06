#
# @lc app=leetcode id=595 lang=python3
#
# [595] Big Countries
#
# https://leetcode.com/problems/big-countries/description/
#
# algorithms
# Easy (68.71%)
# Likes:    3439
# Dislikes: 1383
# Total Accepted:    2.5M
# Total Submissions: 3.6M
# Testcase Example:  "{\"headers\": {\"World\": [\"name\", \"continent\",\t\"area\",\t\"population\", \"gdp\"]}, \"rows\": {\"World\": [[\"Afghanistan\", \"Asia\", 652230, 25500100, 20343000000], [\"Albania\", \"Europe\", 28748, 2831741, 12960000000], [\"Algeria\", \"Africa\", 2381741, 37100000, 188681000000], [\"Andorra\", \"Europe\", 468, 78115,\t3712000000], [\"Angola\", \"Africa\", 1246700, 20609294, 100990000000]]}}"
#
# Table: World
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | name | varchar |
# | continent | varchar |
# | area | int |
# | population | int |
# | gdp | bigint |
# +-------------+---------+
# name is the primary key (column with unique values) for this table.
# Each row of this table gives information about the name of a country, the
# continent to which it belongs, its area, the population, and its GDP value.
#
# A country is big if:
#
# it has an area of at least three million (i.e., 3000000 km^2), or
#
# it has a population of at least twenty-five million (i.e., 25000000).
#
# Write a solution to find the name, population, and area of the big countries.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# World table:
# +-------------+-----------+---------+------------+--------------+
# | name | continent | area | population | gdp |
# +-------------+-----------+---------+------------+--------------+
# | Afghanistan | Asia | 652230 | 25500100 | 20343000000 |
# | Albania | Europe | 28748 | 2831741 | 12960000000 |
# | Algeria | Africa | 2381741 | 37100000 | 188681000000 |
# | Andorra | Europe | 468 | 78115 | 3712000000 |
# | Angola | Africa | 1246700 | 20609294 | 100990000000 |
# +-------------+-----------+---------+------------+--------------+
# Output:
# +-------------+------------+---------+
# | name | population | area |
# +-------------+------------+---------+
# | Afghanistan | 25500100 | 652230 |
# | Algeria | 37100000 | 2381741 |
# +-------------+------------+---------+
#


# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        A country is big if area >= 3000000 or population >= 25000000. Filter
        World and project name, population, area.

        Algorithm:
        - SELECT name, population, area FROM World
          WHERE area >= 3000000 OR population >= 25000000.

        Complexity: O(W) scan of World.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT name, population, area
    FROM World
    WHERE area >= 3000000 OR population >= 25000000;
    """
# @lc code=end

