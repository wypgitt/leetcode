#
# @lc app=leetcode id=618 lang=python3
#
# [618] Students Report By Geography
#
# https://leetcode.com/problems/students-report-by-geography/description/
#
# database
# Hard (63.52%)
# Likes:    193
# Dislikes: 170
# Total Accepted:    29.9K
# Total Submissions: 47.1K
# Testcase Example:  "{\"headers\":{\"Student\":[\"name\",\"continent\"]},\"rows\":{\"Student\":[[\"Jane\",\"America\"],[\"Pascal\",\"Europe\"],[\"Xi\",\"Asia\"],[\"Jack\",\"America\"]]}}"
#
#
# Table: Student
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | name        | varchar |
# | continent   | varchar |
# +-------------+---------+
# This table may contain duplicate rows.
# Each row of this table indicates the name of a student and the continent
# they came from.
#
# A school has students from Asia, Europe, and America.
#
# Write a solution to pivot the continent column in the Student table so
# that each name is sorted alphabetically and displayed underneath its
# corresponding continent. The output headers should be America, Asia, and
# Europe, respectively.
#
# The test cases are generated so that the student number from America is
# not less than either Asia or Europe.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Student table:
# +--------+-----------+
# | name   | continent |
# +--------+-----------+
# | Jane   | America   |
# | Pascal | Europe    |
# | Xi     | Asia      |
# | Jack   | America   |
# +--------+-----------+
# Output:
# +---------+------+--------+
# | America | Asia | Europe |
# +---------+------+--------+
# | Jack    | Xi   | Pascal |
# | Jane    | null | null   |
# +---------+------+--------+
#
# Follow up: If it is unknown which continent has the most students, could
# you write a solution to generate the student report?
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Pivot student names by continent into America/Asia/Europe columns, alphabetically aligned by row number.

        Algorithm:
        - ROW_NUMBER() PARTITION BY continent ORDER BY name.
        - GROUP BY rn with conditional MAX(CASE continent ...) pivots columns.

        Complexity: O(N log N) for ranking.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        MAX(CASE WHEN continent = 'America' THEN name END) AS America,
        MAX(CASE WHEN continent = 'Asia' THEN name END) AS Asia,
        MAX(CASE WHEN continent = 'Europe' THEN name END) AS Europe
    FROM (
        SELECT name, continent,
               ROW_NUMBER() OVER (PARTITION BY continent ORDER BY name) AS rn
        FROM Student
    ) t
    GROUP BY rn;
    """
# @lc code=end
