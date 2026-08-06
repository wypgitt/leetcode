#
# @lc app=leetcode id=2253 lang=python3
#
# [2253] Dynamic Unpivoting of a Table
#
# https://leetcode.com/problems/dynamic-unpivoting-of-a-table/description/
#
# database
# Hard (69.60%)
# Likes:    20
# Dislikes: 13
# Total Accepted:    1.6K
# Total Submissions: 2.2K
# Testcase Example:  "{\"headers\": {\"Products\": [\"product_id\", \"LC_Store\", \"Nozama\", \"Shop\", \"Souq\"]}, \"rows\": {\"Products\": [[1, 100, null, 110, null], [2, null, 200, null, 190], [3, null, null, 1000, 1900]]}}"
#
#
# Table: Products
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | product_id  | int     |
# | store_name_1 | int     |
# | store_name_2 | int     |
# |      :      | int     |
# |      :      | int     |
# |      :      | int     |
# | store_name_n | int     |
# +-------------+---------+
# product_id is the primary key for this table.
# Each row in this table indicates the product's price in n different
# stores.
# If the product is not available in a store, the price will be null in
# that store's column.
# The names of the stores may change from one testcase to another. There
# will be at least 1 store and at most 30 stores.
#
# Important note: This problem targets those who have a good experience
# with SQL. If you are a beginner, we recommend that you skip it for now.
#
# Implement the procedure UnpivotProducts to reorganize the Products table
# so that each row has the id of one product, the name of a store where it
# is sold, and its price in that store. If a product is not available in a
# store, do not include a row with that product_id and store combination
# in the result table. There should be three columns: product_id, store,
# and price.
#
# The procedure should return the table after reorganizing it.
#
# Return the result table in any order.
#
# The query result format is in the following example.
#
# Example 1:
#
# Input:
# Products table:
# +------------+----------+--------+------+------+
# | product_id | LC_Store | Nozama | Shop | Souq |
# +------------+----------+--------+------+------+
# | 1          | 100      | null   | 110  | null |
# | 2          | null     | 200    | null | 190  |
# | 3          | null     | null   | 1000 | 1900 |
# +------------+----------+--------+------+------+
# Output:
# +------------+----------+-------+
# | product_id | store    | price |
# +------------+----------+-------+
# | 1          | LC_Store | 100   |
# | 1          | Shop     | 110   |
# | 2          | Nozama   | 200   |
# | 2          | Souq     | 190   |
# | 3          | Shop     | 1000  |
# | 3          | Souq     | 1900  |
# +------------+----------+-------+
# Explanation:
# Product 1 is sold in LC_Store and Shop with prices of 100 and 110
# respectively.
# Product 2 is sold in Nozama and Souq with prices of 200 and 190.
# Product 3 is sold in Shop and Souq with prices of 1000 and 1900.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL procedure UnpivotProducts: unpivot store columns into rows
        (product_id, store, price), omit NULL prices.

        Algorithm:
        - Build UNION of SELECTs from information_schema column names.

        Complexity: O(N * S).
        """
        self.sql = '''
CREATE PROCEDURE UnpivotProducts()
BEGIN
    SET group_concat_max_len = 5000;
    SELECT GROUP_CONCAT(
        CONCAT(
            'SELECT product_id, \'', column_name, '\' AS store, `',
            column_name, '` AS price FROM Products WHERE `',
            column_name, '` IS NOT NULL'
        )
        SEPARATOR ' UNION '
    ) INTO @sql
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'Products'
      AND column_name != 'product_id';
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END
'''
        return self.sql
# @lc code=end
