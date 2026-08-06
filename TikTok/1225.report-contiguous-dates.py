#
# @lc app=leetcode id=1225 lang=python3
#
# [1225] Report Contiguous Dates
#
# https://leetcode.com/problems/report-contiguous-dates/description/
#
# database
# Hard (57.07%)
# Likes:    351
# Dislikes: 22
# Total Accepted:    33.9K
# Total Submissions: 59.3K
# Testcase Example:  "{\"headers\":{\"Failed\":[\"fail_date\"],\"Succeeded\":[\"success_date\"]},\"rows\":{\"Failed\":[[\"2018-12-28\"],[\"2018-12-29\"],[\"2019-01-04\"],[\"2019-01-05\"]],\"Succeeded\":[[\"2018-12-30\"],[\"2018-12-31\"],[\"2019-01-01\"],[\"2019-01-02\"],[\"2019-01-03\"],[\"2019-01-06\"]]}}"
#
#
# Table: Failed
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | fail_date    | date    |
# +--------------+---------+
# fail_date is the primary key (column with unique values) for this table.
# This table contains the days of failed tasks.
#
# Table: Succeeded
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | success_date | date    |
# +--------------+---------+
# success_date is the primary key (column with unique values) for this
# table.
# This table contains the days of succeeded tasks.
#
# A system is running one task every day. Every task is independent of the
# previous tasks. The tasks can fail or succeed.
#
# Write a solution to report the period_state for each continuous interval
# of days in the period from 2019-01-01 to 2019-12-31.
#
# period_state is 'failed' if tasks in this interval failed or 'succeeded'
# if tasks in this interval succeeded. Interval of days are retrieved as
# start_date and end_date.
#
# Return the result table ordered by start_date.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Failed table:
# +-------------------+
# | fail_date         |
# +-------------------+
# | 2018-12-28        |
# | 2018-12-29        |
# | 2019-01-04        |
# | 2019-01-05        |
# +-------------------+
# Succeeded table:
# +-------------------+
# | success_date      |
# +-------------------+
# | 2018-12-30        |
# | 2018-12-31        |
# | 2019-01-01        |
# | 2019-01-02        |
# | 2019-01-03        |
# | 2019-01-06        |
# +-------------------+
# Output:
# +--------------+--------------+--------------+
# | period_state | start_date   | end_date     |
# +--------------+--------------+--------------+
# | succeeded    | 2019-01-01   | 2019-01-03   |
# | failed       | 2019-01-04   | 2019-01-05   |
# | succeeded    | 2019-01-06   | 2019-01-06   |
# +--------------+--------------+--------------+
# Explanation:
# The report ignored the system state in 2018 as we care about the system
# in the period 2019-01-01 to 2019-12-31.
# From 2019-01-01 to 2019-01-03 all tasks succeeded and the system state
# was "succeeded".
# From 2019-01-04 to 2019-01-05 all tasks failed and the system state was
# "failed".
# From 2019-01-06 to 2019-01-06 all tasks succeeded and the system state
# was "succeeded".
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Merge Failed and Succeeded period dates in 2019-01-01..
        2019-12-31; report contiguous date ranges with period_state
        ('failed'/'succeeded'), start_date, end_date.

        Algorithm:
        - UNION ALL fail/success with state; find islands via date - ROW_NUMBER
        - GROUP BY state, island; MIN/MAX dates; ORDER BY start_date

        Complexity: O(N log N).
        """
        return self.sql

    sql = """
    WITH all_days AS (
        SELECT fail_date AS dt, 'failed' AS period_state
        FROM Failed
        WHERE fail_date BETWEEN '2019-01-01' AND '2019-12-31'
        UNION ALL
        SELECT success_date AS dt, 'succeeded' AS period_state
        FROM Succeeded
        WHERE success_date BETWEEN '2019-01-01' AND '2019-12-31'
    ),
    marked AS (
        SELECT dt, period_state,
               DATE_SUB(dt, INTERVAL ROW_NUMBER() OVER (PARTITION BY period_state ORDER BY dt) DAY) AS grp
        FROM all_days
    )
    SELECT period_state,
           MIN(dt) AS start_date,
           MAX(dt) AS end_date
    FROM marked
    GROUP BY period_state, grp
    ORDER BY start_date;
    """
# @lc code=end
