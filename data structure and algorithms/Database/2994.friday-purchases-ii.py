#
# @lc app=leetcode id=2994 lang=python3
#
# [2994] Friday Purchases II
#
# https://leetcode.com/problems/friday-purchases-ii/description/
#
# database
# Medium (72.00%)
# Likes:    10
# Dislikes: 5
# Total Accepted:    3.5K
# Total Submissions: 4.9K
# Testcase Example:  "{\"headers\":{\"Purchases\":[\"user_id\",\"purchase_date\",\"amount_spend\"]},\"rows\":{\"Purchases\":[[11,\"2023-11-07\",1126],[15,\"2023-11-30\",7473],[17,\"2023-11-14\",2414],[12,\"2023-11-24\",9692],[8,\"2023-11-03\",5117],[1,\"2023-11-16\",5241],[10,\"2023-11-12\",8266],[13,\"2023-11-24\",12000]]}}"
#
#
# Premium problem. Description unavailable without subscription.
# Friday Purchases II: Purchases in Nov 2023; report total spend on every
# Friday of the month (0 if none). Ordered by week_of_month.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Purchases(user_id, purchase_date, amount_spend) for
        Nov 1–30 2023. Unlike Friday Purchases I, include every Friday even
        when total_amount is 0. week_of_month = CEIL(DAYOFMONTH/7).

        Algorithm:
        - Recursive CTE of all Nov dates; keep DAYOFWEEK=6 (Friday); LEFT JOIN
          Purchases; GROUP BY date; IFNULL(SUM, 0); ORDER BY week_of_month.

        Complexity: O(N).
        """
        self.sql = """
WITH RECURSIVE
    T AS (
        SELECT '2023-11-01' AS purchase_date
        UNION
        SELECT purchase_date + INTERVAL 1 DAY
        FROM T
        WHERE purchase_date < '2023-11-30'
    )
SELECT
    CEIL(DAYOFMONTH(purchase_date) / 7) AS week_of_month,
    purchase_date,
    IFNULL(SUM(amount_spend), 0) AS total_amount
FROM
    T
    LEFT JOIN Purchases USING (purchase_date)
WHERE DAYOFWEEK(purchase_date) = 6
GROUP BY 2
ORDER BY 1;
"""
        return self.sql
# @lc code=end
