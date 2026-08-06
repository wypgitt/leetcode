#
# @lc app=leetcode id=2504 lang=python3
#
# [2504] Concatenate the Name and the Profession
#
# https://leetcode.com/problems/concatenate-the-name-and-the-profession/description/
#
# database
# Easy (80.37%)
# Likes:    32
# Dislikes: 4
# Total Accepted:    7.4K
# Total Submissions: 9.2K
# Testcase Example:  "{\"headers\": {\"Person\": [\"person_id\", \"name\", \"profession\"]}, \"rows\": {\"Person\": [[1, \"Alex\", \"Singer\"], [3, \"Alice\", \"Actor\"], [2, \"Bob\", \"Player\"], [4, \"Messi\", \"Doctor\"], [6, \"Tyson\", \"Engineer\"], [5, \"Meir\", \"Lawyer\"]]}}"
#
#
# Table: Person
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | person_id   | int     |
# | name        | varchar |
# | profession  | ENUM    |
# +-------------+---------+
# person_id is the primary key (column with a unique value) for this
# table.
# Each row in this table contains a person's ID, name, and profession.
# The profession column in an enum of the type ('Doctor', 'Singer',
# 'Actor', 'Player', 'Engineer', or 'Lawyer')
#
# Write a solution to report each person's name followed by the first
# letter of their profession enclosed in parentheses.
#
# Return the result table ordered by person_id in descending order.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# Person table:
# +-----------+-------+------------+
# | person_id | name  | profession |
# +-----------+-------+------------+
# | 1         | Alex  | Singer     |
# | 3         | Alice | Actor      |
# | 2         | Bob   | Player     |
# | 4         | Messi | Doctor     |
# | 6         | Tyson | Engineer   |
# | 5         | Meir  | Lawyer     |
# +-----------+-------+------------+
# Output:
# +-----------+----------+
# | person_id | name     |
# +-----------+----------+
# | 6         | Tyson(E) |
# | 5         | Meir(L)  |
# | 4         | Messi(D) |
# | 3         | Alice(A) |
# | 2         | Bob(P)   |
# | 1         | Alex(S)  |
# +-----------+----------+
# Explanation: Note that there should not be any white space between the
# name and the first letter of the profession.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL premium. Person(person_id, name, profession). Return person_id and
        name concatenated with first letter of profession in parentheses, ordered
        by person_id descending.

        Algorithm:
        - SELECT person_id, CONCAT(name, '(', SUBSTRING(profession,1,1), ')') AS
          name FROM Person ORDER BY person_id DESC.

        Complexity: O(N log N) for sort.
        """
        self.sql = """
SELECT person_id, CONCAT(name, '(', SUBSTRING(profession, 1, 1), ')') AS name
FROM Person
ORDER BY person_id DESC;
"""
        return self.sql
# @lc code=end
