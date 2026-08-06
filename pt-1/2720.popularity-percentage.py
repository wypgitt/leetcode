#
# @lc app=leetcode id=2720 lang=python3
#
# [2720] Popularity Percentage
#
# https://leetcode.com/problems/popularity-percentage/description/
#
# algorithms
# Hard
#
# Premium SQL. Friends(user1, user2) undirected friendships.
# Popularity % = (#friends / #users on platform) * 100, rounded to 2 decimals.
# Return user1, percentage_popularity ordered by user1.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Treat friendships as bidirectional; for each user compute
        friends / total distinct users * 100, rounded to 2 decimals.

        Algorithm:
        - UNION reverse edges; count distinct users; window-count friends per user1.

        Complexity: O(N) over friendship rows.
        """
        self.sql = """
WITH F AS (
  SELECT user1, user2 FROM Friends
  UNION
  SELECT user2, user1 FROM Friends
),
T AS (SELECT COUNT(DISTINCT user1) AS cnt FROM F)
SELECT DISTINCT
  user1,
  ROUND((COUNT(1) OVER (PARTITION BY user1)) * 100 / (SELECT cnt FROM T), 2)
    AS percentage_popularity
FROM F
ORDER BY 1;
"""
        return self.sql
# @lc code=end
