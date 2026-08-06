#
# @lc app=leetcode id=1384 lang=python3
#
# [1384] Total Sales Amount by Year
#
# https://leetcode.com/problems/total-sales-amount-by-year/description/
#
# database
# Hard (61.13%)
# Likes:    236
# Dislikes: 133
# Total Accepted:    20.3K
# Total Submissions: 33.2K
# Testcase Example:  "{\"headers\": {\"Product\": [\"product_id\", \"product_name\"], \"Sales\": [\"product_id\", \"period_start\", \"period_end\", \"average_daily_sales\"]}, \"rows\": {\"Product\": [[1, \"LC Phone \"], [2, \"LC T-Shirt\"], [3, \"LC Keychain\"]], \"Sales\": [[1, \"2019-01-25\", \"2019-02-28\", 100], [2, \"2018-12-01\", \"2020-01-01\", 10], [3, \"2019-12-01\", \"2020-01-31\", 1]]}}"
#
#
# Table: Product
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | product_id    | int     |
# | product_name  | varchar |
# +---------------+---------+
# product_id is the primary key (column with unique values) for this
# table.
# product_name is the name of the product.
#
# Table: Sales
#
# +---------------------+---------+
# | Column Name         | Type    |
# +---------------------+---------+
# | product_id          | int     |
# | period_start        | date    |
# | period_end          | date    |
# | average_daily_sales | int     |
# +---------------------+---------+
# product_id is the primary key (column with unique values) for this
# table.
# period_start and period_end indicate the start and end date for the
# sales period, and both dates are inclusive.
# The average_daily_sales column holds the average daily sales amount of
# the items for the period.
# The dates of the sales years are between 2018 to 2020.
#
# Write a solution to report the total sales amount of each item for each
# year, with corresponding product_name, product_id, report_year, and
# total_amount.
#
# Return the result table ordered by product_id and report_year.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Product table:
# +------------+--------------+
# | product_id | product_name |
# +------------+--------------+
# | 1          | LC Phone     |
# | 2          | LC T-Shirt   |
# | 3          | LC Keychain  |
# +------------+--------------+
# Sales table:
# +------------+--------------+-------------+---------------------+
# | product_id | period_start | period_end  | average_daily_sales |
# +------------+--------------+-------------+---------------------+
# | 1          | 2019-01-25   | 2019-02-28  | 100                 |
# | 2          | 2018-12-01   | 2020-01-01  | 10                  |
# | 3          | 2019-12-01   | 2020-01-31  | 1                   |
# +------------+--------------+-------------+---------------------+
# Output:
# +------------+--------------+-------------+--------------+
# | product_id | product_name | report_year | total_amount |
# +------------+--------------+-------------+--------------+
# | 1          | LC Phone     |    2019     | 3500         |
# | 2          | LC T-Shirt   |    2018     | 310          |
# | 2          | LC T-Shirt   |    2019     | 3650         |
# | 2          | LC T-Shirt   |    2020     | 10           |
# | 3          | LC Keychain  |    2019     | 31           |
# | 3          | LC Keychain  |    2020     | 31           |
# +------------+--------------+-------------+--------------+
# Explanation:
# LC Phone was sold for the period of 2019-01-25 to 2019-02-28, and there
# are 35 days for this period. Total amount 35*100 = 3500.
# LC T-shirt was sold for the period of 2018-12-01 to 2020-01-01, and
# there are 31, 365, 1 days for years 2018, 2019 and 2020 respectively.
# LC Keychain was sold for the period of 2019-12-01 to 2020-01-31, and
# there are 31, 31 days for years 2019 and 2020 respectively.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Expand each sales period across calendar years; for each
        (product, year) compute days overlapping that year * average_daily_sales.

        Algorithm:
        - For each Sales row, generate year segments clipped to [period_start, period_end]
        - Join Product for name; report year as 'yyyy', total_amount

        Complexity: O(S * Y) years spanned per sale.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        s.product_id,
        p.product_name,
        y.report_year,
        s.average_daily_sales * (
            DATEDIFF(
                LEAST(s.period_end, y.y_end),
                GREATEST(s.period_start, y.y_start)
            ) + 1
        ) AS total_amount
    FROM Sales s
    JOIN Product p ON s.product_id = p.product_id
    JOIN (
        SELECT '2018' AS report_year, '2018-01-01' AS y_start, '2018-12-31' AS y_end
        UNION ALL
        SELECT '2019', '2019-01-01', '2019-12-31'
        UNION ALL
        SELECT '2020', '2020-01-01', '2020-12-31'
    ) y
      ON s.period_start <= y.y_end AND s.period_end >= y.y_start
    ORDER BY s.product_id, y.report_year;
    """
# @lc code=end
