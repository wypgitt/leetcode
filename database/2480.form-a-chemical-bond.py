#
# @lc app=leetcode id=2480 lang=python3
#
# [2480] Form a Chemical Bond
#
# https://leetcode.com/problems/form-a-chemical-bond/description/
#
# database
# Easy (80.10%)
# Likes:    31
# Dislikes: 11
# Total Accepted:    7.7K
# Total Submissions: 9.6K
# Testcase Example:  "{\"headers\": {\"Elements\": [\"symbol\", \"type\", \"electrons\"]}, \"rows\": {\"Elements\": [[\"He\", \"Noble\", 0], [\"Na\", \"Metal\", 1], [\"Ca\", \"Metal\", 2], [\"La\", \"Metal\", 3], [\"Cl\", \"Nonmetal\", 1], [\"O\", \"Nonmetal\", 2], [\"N\", \"Nonmetal\", 3]]}}"
#
#
# Table: Elements
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | symbol      | varchar |
# | type        | enum    |
# | electrons   | int     |
# +-------------+---------+
# symbol is the primary key (column with unique values) for this table.
# Each row of this table contains information of one element.
# type is an ENUM (category) of type ('Metal', 'Nonmetal', 'Noble')
#  - If type is Noble, electrons is 0.
#  - If type is Metal, electrons is the number of electrons that one atom
# of this element can give.
#  - If type is Nonmetal, electrons is the number of electrons that one
# atom of this element needs.
#
# Two elements can form a bond if one of them is 'Metal' and the other is
# 'Nonmetal'.
#
# Write a solution to find all the pairs of elements that can form a bond.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Elements table:
# +--------+----------+-----------+
# | symbol | type     | electrons |
# +--------+----------+-----------+
# | He     | Noble    | 0         |
# | Na     | Metal    | 1         |
# | Ca     | Metal    | 2         |
# | La     | Metal    | 3         |
# | Cl     | Nonmetal | 1         |
# | O      | Nonmetal | 2         |
# | N      | Nonmetal | 3         |
# +--------+----------+-----------+
# Output:
# +-------+----------+
# | metal | nonmetal |
# +-------+----------+
# | La    | Cl       |
# | Ca    | Cl       |
# | Na    | Cl       |
# | La    | O        |
# | Ca    | O        |
# | Na    | O        |
# | La    | N        |
# | Ca    | N        |
# | Na    | N        |
# +-------+----------+
# Explanation:
# Metal elements are La, Ca, and Na.
# Nonmeal elements are Cl, O, and N.
# Each Metal element pairs with a Nonmetal element in the output table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Elements(symbol, type, electrons). Pair every Metal with
        every Nonmetal as a chemical bond.

        Algorithm:
        - Cross join Metals and Nonmetals; select symbols.

        Complexity: O(M*N) rows.
        """
        self.sql = """
SELECT a.symbol AS metal, b.symbol AS nonmetal
FROM Elements AS a
CROSS JOIN Elements AS b
WHERE a.type = 'Metal' AND b.type = 'Nonmetal';
"""
        return self.sql
# @lc code=end

