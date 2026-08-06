#
# @lc app=leetcode id=1495 lang=python3
#
# [1495] Friendly Movies Streamed Last Month
#
# https://leetcode.com/problems/friendly-movies-streamed-last-month/description/
#
# database
# Easy (48.93%)
# Likes:    92
# Dislikes: 43
# Total Accepted:    41.2K
# Total Submissions: 84.1K
# Testcase Example:  "{\"headers\": {\"TVProgram\": [\"program_date\", \"content_id\", \"channel\"], \"Content\": [\"content_id\", \"title\", \"Kids_content\", \"content_type\"]}, \"rows\": {\"TVProgram\": [[\"2020-06-10 08:00\", 1, \"LC-Channel\"], [\"2020-05-11 12:00\", 2, \"LC-Channel\"], [\"2020-05-12 12:00\", 3, \"LC-Channel\"], [\"2020-05-13 14:00\", 4, \"Disney Ch\"], [\"2020-06-18 14:00\", 4, \"Disney Ch\"], [\"2020-07-15 16:00\", 5, \"Disney Ch\"]], \"Content\": [[1, \"Leetcode Movie\", \"N\", \"Movies\"], [2, \"Alg. for Kids\", \"Y\", \"Series\"], [3, \"Database Sols\", \"N\", \"Series\"], [4, \"Aladdin\", \"Y\", \"Movies\"], [5, \"Cinderella\", \"Y\", \"Movies\"]]}}"
#
#
# Table: TVProgram
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | program_date  | date    |
# | content_id    | int     |
# | channel       | varchar |
# +---------------+---------+
# (program_date, content_id) is the primary key (combination of columns
# with unique values) for this table.
# This table contains information of the programs on the TV.
# content_id is the id of the program in some channel on the TV.
#
# Table: Content
#
# +------------------+---------+
# | Column Name      | Type    |
# +------------------+---------+
# | content_id       | varchar |
# | title            | varchar |
# | Kids_content     | enum    |
# | content_type     | varchar |
# +------------------+---------+
# content_id is the primary key (column with unique values) for this
# table.
# Kids_content is an ENUM (category) of types ('Y', 'N') where:
# 'Y' means is content for kids otherwise 'N' is not content for kids.
# content_type is the category of the content as movies, series, etc.
#
# Write a solution to report the distinct titles of the kid-friendly
# movies streamed in June 2020.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# TVProgram table:
# +--------------------+--------------+-------------+
# | program_date       | content_id   | channel     |
# +--------------------+--------------+-------------+
# | 2020-06-10 08:00   | 1            | LC-Channel  |
# | 2020-05-11 12:00   | 2            | LC-Channel  |
# | 2020-05-12 12:00   | 3            | LC-Channel  |
# | 2020-05-13 14:00   | 4            | Disney Ch   |
# | 2020-06-18 14:00   | 4            | Disney Ch   |
# | 2020-07-15 16:00   | 5            | Disney Ch   |
# +--------------------+--------------+-------------+
# Content table:
# +------------+----------------+---------------+---------------+
# | content_id | title          | Kids_content  | content_type  |
# +------------+----------------+---------------+---------------+
# | 1          | Leetcode Movie | N             | Movies        |
# | 2          | Alg. for Kids  | Y             | Series        |
# | 3          | Database Sols  | N             | Series        |
# | 4          | Aladdin        | Y             | Movies        |
# | 5          | Cinderella     | Y             | Movies        |
# +------------+----------------+---------------+---------------+
# Output:
# +--------------+
# | title        |
# +--------------+
# | Aladdin      |
# +--------------+
# Explanation:
# "Leetcode Movie" is not a content for kids.
# "Alg. for Kids" is not a movie.
# "Database Sols" is not a movie
# "Alladin" is a movie, content for kids and was streamed in June 2020.
# "Cinderella" was not streamed in June 2020.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. TVProgram(program_date, content_id, channel),
        Content(content_id, title, Kids_content, content_type). Report distinct
        titles of kid-friendly movies (Kids_content='Y', content_type='Movies')
        aired in June 2020.

        Algorithm:
        - JOIN Content and TVProgram; filter month/year and kids movies;
          SELECT DISTINCT title.

        Complexity: O(N) with hash distinct.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT c.title
    FROM Content c
    JOIN TVProgram t ON c.content_id = t.content_id
    WHERE c.Kids_content = 'Y'
      AND c.content_type = 'Movies'
      AND t.program_date >= '2020-06-01'
      AND t.program_date < '2020-07-01';
    """
# @lc code=end
