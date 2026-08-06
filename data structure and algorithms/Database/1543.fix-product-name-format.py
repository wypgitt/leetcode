#
# @lc app=leetcode id=1543 lang=python3
#
# [1543] Fix Product Name Format
#
# https://leetcode.com/problems/fix-product-name-format/description/
#
# database
# Easy (58.81%)
# Likes:    93
# Dislikes: 45
# Total Accepted:    24.3K
# Total Submissions: 41.3K
# Testcase Example:  "{\"headers\": {\"Sales\": [\"sale_id\", \"product_name\", \"sale_date\"]}, \"rows\": {\"Sales\": [[1, \"LCPHONE\", \"2000-01-16\"], [2, \"LCPhone\", \"2000-01-17\"], [3, \"LcPhOnE\", \"2000-02-18\"], [4, \"LCKeyCHAiN\", \"2000-02-19\"], [5, \"LCKeyChain\", \"2000-02-28\"], [6, \"Matryoshka\", \"2000-03-31\"]]}}"
#
#
# Table: Sales
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | sale_id      | int     |
# | product_name | varchar |
# | sale_date    | date    |
# +--------------+---------+
# sale_id is the column with unique values for this table.
# Each row of this table contains the product name and the date it was
# sold.
#
# Since table Sales was filled manually in the year 2000, product_name may
# contain leading and/or trailing white spaces, also they are
# case-insensitive.
#
# Write a solution to report
#
# product_name in lowercase without leading or trailing white spaces.
#
# sale_date in the format ('YYYY-MM').
#
# total the number of times the product was sold in this month.
#
# Return the result table ordered by product_name in ascending order. In
# case of a tie, order it by sale_date in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Sales table:
# +---------+--------------+------------+
# | sale_id | product_name | sale_date  |
# +---------+--------------+------------+
# | 1       | LCPHONE      | 2000-01-16 |
# | 2       | LCPhone      | 2000-01-17 |
# | 3       | LcPhOnE      | 2000-02-18 |
# | 4       | LCKeyCHAiN   | 2000-02-19 |
# | 5       | LCKeyChain   | 2000-02-28 |
# | 6       | Matryoshka   | 2000-03-31 |
# +---------+--------------+------------+
# Output:
# +--------------+-----------+-------+
# | product_name | sale_date | total |
# +--------------+-----------+-------+
# | lckeychain   | 2000-02   | 2     |
# | lcphone      | 2000-01   | 2     |
# | lcphone      | 2000-02   | 1     |
# | matryoshka   | 2000-03   | 1     |
# +--------------+-----------+-------+
# Explanation:
# In January, 2 LcPhones were sold. Please note that the product names are
# not case sensitive and may contain spaces.
# In February, 2 LCKeychains and 1 LCPhone were sold.
# In March, one matryoshka was sold.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Fix product names: trim spaces, lowercase; sale_date to
        YYYY-MM. Group by fixed name+date and SUM(sale_id count? sale amounts)
        — return product_name, sale_date, total (COUNT of sales).

        Algorithm:
        - SELECT LOWER(TRIM(product_name)), DATE_FORMAT(sale_date,'%Y-%m'),
          COUNT(*) GROUP BY 1,2 ORDER BY 1,2.

        Complexity: O(S).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT LOWER(TRIM(product_name)) AS product_name,
           DATE_FORMAT(sale_date, '%Y-%m') AS sale_date,
           COUNT(*) AS total
    FROM Sales
    GROUP BY 1, 2
    ORDER BY product_name, sale_date;
    """
# @lc code=end
