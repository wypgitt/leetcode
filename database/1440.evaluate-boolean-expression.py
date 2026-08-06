#
# @lc app=leetcode id=1440 lang=python3
#
# [1440] Evaluate Boolean Expression
#
# https://leetcode.com/problems/evaluate-boolean-expression/description/
#
# database
# Medium (71.67%)
# Likes:    233
# Dislikes: 41
# Total Accepted:    39.5K
# Total Submissions: 55.1K
# Testcase Example:  "{\"headers\":{\"Variables\":[\"name\",\"value\"],\"Expressions\":[\"left_operand\",\"operator\",\"right_operand\"]},\"rows\":{\"Variables\":[[\"x\",66],[\"y\",77]],\"Expressions\":[[\"x\",\">\",\"y\"],[\"x\",\"<\",\"y\"],[\"x\",\"=\",\"y\"],[\"y\",\">\",\"x\"],[\"y\",\"<\",\"x\"],[\"x\",\"=\",\"x\"]]}}"
#
#
# Table Variables:
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | name          | varchar |
# | value         | int     |
# +---------------+---------+
# In SQL, name is the primary key for this table.
# This table contains the stored variables and their values.
#
# Table Expressions:
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | left_operand  | varchar |
# | operator      | enum    |
# | right_operand | varchar |
# +---------------+---------+
# In SQL, (left_operand, operator, right_operand) is the primary key for
# this table.
# This table contains a boolean expression that should be evaluated.
# operator is an enum that takes one of the values ('<', '>', '=')
# The values of left_operand and right_operand are guaranteed to be in the
# Variables table.
#
# Evaluate the boolean expressions in Expressions table.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Variables table:
# +------+-------+
# | name | value |
# +------+-------+
# | x    | 66    |
# | y    | 77    |
# +------+-------+
# Expressions table:
# +--------------+----------+---------------+
# | left_operand | operator | right_operand |
# +--------------+----------+---------------+
# | x            | >        | y             |
# | x            | <        | y             |
# | x            | =        | y             |
# | y            | >        | x             |
# | y            | <        | x             |
# | x            | =        | x             |
# +--------------+----------+---------------+
# Output:
# +--------------+----------+---------------+-------+
# | left_operand | operator | right_operand | value |
# +--------------+----------+---------------+-------+
# | x            | >        | y             | false |
# | x            | <        | y             | true  |
# | x            | =        | y             | false |
# | y            | >        | x             | true  |
# | y            | <        | x             | false |
# | x            | =        | x             | true  |
# +--------------+----------+---------------+-------+
# Explanation:
# As shown, you need to find the value of each boolean expression in the
# table using the variables table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Variables(name,value), Expressions(left,operator,right)
        with operators >, <, =. Evaluate each expression to 'true'/'false'.

        Algorithm:
        - Join Variables twice for left/right values; CASE on operator.

        Complexity: O(E+V).
        """
        return self.sql

    sql = """
    SELECT e.left_operand, e.operator, e.right_operand,
           CASE
             WHEN e.operator = '>' AND l.value > r.value THEN 'true'
             WHEN e.operator = '<' AND l.value < r.value THEN 'true'
             WHEN e.operator = '=' AND l.value = r.value THEN 'true'
             ELSE 'false'
           END AS value
    FROM Expressions e
    JOIN Variables l ON e.left_operand = l.name
    JOIN Variables r ON e.right_operand = r.name;
    """
# @lc code=end
