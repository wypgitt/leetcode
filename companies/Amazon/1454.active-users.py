#
# @lc app=leetcode id=1454 lang=python3
#
# [1454] Active Users
#
# https://leetcode.com/problems/active-users/description/
#
# database
# Medium (36.57%)
# Likes:    421
# Dislikes: 41
# Total Accepted:    48.3K
# Total Submissions: 132K
# Testcase Example:  "{\"headers\":{\"Accounts\":[\"id\",\"name\"],\"Logins\":[\"id\",\"login_date\"]},\"rows\":{\"Accounts\":[[1,\"Winston\"],[7,\"Jonathan\"]],\"Logins\":[[7,\"2020-05-30\"],[1,\"2020-05-30\"],[7,\"2020-05-31\"],[7,\"2020-06-01\"],[7,\"2020-06-02\"],[7,\"2020-06-02\"],[7,\"2020-06-03\"],[1,\"2020-06-07\"],[7,\"2020-06-10\"]]}}"
#
#
# Table: Accounts
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | id            | int     |
# | name          | varchar |
# +---------------+---------+
# id is the primary key (column with unique values) for this table.
# This table contains the account id and the user name of each account.
#
# Table: Logins
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | id            | int     |
# | login_date    | date    |
# +---------------+---------+
# This table may contain duplicate rows.
# This table contains the account id of the user who logged in and the
# login date. A user may log in multiple times in the day.
#
# Active users are those who logged in to their accounts for five or more
# consecutive days.
#
# Write a solution to find the id and the name of active users.
#
# Return the result table ordered by id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Accounts table:
# +----+----------+
# | id | name     |
# +----+----------+
# | 1  | Winston  |
# | 7  | Jonathan |
# +----+----------+
# Logins table:
# +----+------------+
# | id | login_date |
# +----+------------+
# | 7  | 2020-05-30 |
# | 1  | 2020-05-30 |
# | 7  | 2020-05-31 |
# | 7  | 2020-06-01 |
# | 7  | 2020-06-02 |
# | 7  | 2020-06-02 |
# | 7  | 2020-06-03 |
# | 1  | 2020-06-07 |
# | 7  | 2020-06-10 |
# +----+------------+
# Output:
# +----+----------+
# | id | name     |
# +----+----------+
# | 7  | Jonathan |
# +----+----------+
# Explanation:
# User Winston with id = 1 logged in 2 times only in 2 different days, so,
# Winston is not an active user.
# User Jonathan with id = 7 logged in 7 times in 6 different days, five of
# them were consecutive days, so, Jonathan is an active user.
#
# Follow up: Could you write a general solution if the active users are
# those who logged in to their accounts for n or more consecutive days?
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Accounts(id, name), Logins(id, login_date). Find accounts
        that logged in for at least 5 consecutive days. Return id, name distinct,
        ordered by id.

        Algorithm:
        - Self-join or window: dense-rank / date - ROW_NUMBER() trick to group
          consecutive dates; filter groups with COUNT DISTINCT dates >= 5.

        Complexity: O(L log L) with sorts/windows.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT a.id, a.name
    FROM Accounts a
    JOIN (
        SELECT id, login_date,
               DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY id ORDER BY login_date) DAY) AS grp
        FROM (SELECT DISTINCT id, login_date FROM Logins) t
    ) x ON a.id = x.id
    GROUP BY a.id, a.name, x.grp
    HAVING COUNT(*) >= 5
    ORDER BY a.id;
    """
# @lc code=end
