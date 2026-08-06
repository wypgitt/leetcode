#
# @lc app=leetcode id=2701 lang=python3
#
# [2701] Consecutive Transactions with Increasing Amounts
#
# https://leetcode.com/problems/consecutive-transactions-with-increasing-amounts/description/
#
# algorithms
# Hard
#
# Premium SQL. Transactions(transaction_id, customer_id, transaction_date, amount).
# Find streaks of consecutive days with strictly increasing amounts of length >= 3.
# Return customer_id, consecutive_start, consecutive_end ordered by customer_id.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Find per-customer streaks of consecutive calendar days with
        strictly increasing amounts lasting at least 3 days; report start/end dates.

        Algorithm:
        - Left-join each row to the prior-day smaller-amount row; when missing,
          start a new group via running SUM of break flags; keep groups with COUNT >= 3.

        Complexity: O(N log N) with window sort / join keys.
        """
        self.sql = """
WITH T AS (
  SELECT
    t1.*,
    SUM(CASE WHEN t2.customer_id IS NULL THEN 1 ELSE 0 END)
      OVER (ORDER BY t1.customer_id, t1.transaction_date) AS s
  FROM Transactions AS t1
  LEFT JOIN Transactions AS t2
    ON t1.customer_id = t2.customer_id
   AND t1.amount > t2.amount
   AND DATEDIFF(t1.transaction_date, t2.transaction_date) = 1
)
SELECT
  customer_id,
  MIN(transaction_date) AS consecutive_start,
  MAX(transaction_date) AS consecutive_end
FROM T
GROUP BY customer_id, s
HAVING COUNT(1) >= 3
ORDER BY customer_id;
"""
        return self.sql
# @lc code=end
