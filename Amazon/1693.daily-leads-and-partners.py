#
# @lc app=leetcode id=1693 lang=python3
#
# [1693] Daily Leads and Partners
#
# https://leetcode.com/problems/daily-leads-and-partners/description/
#
# algorithms
# Easy (86.8%)
# Likes:    646
# Dislikes: 37
# Total Accepted:    225K
# Total Submissions: 259K
# Testcase Example:  "{\"headers\":{\"DailySales\":[\"date_id\",\"make_name\",\"lead_id\",\"partner_id\"]},\"rows\":{\"DailySales\":[[\"2020-12-8\",\"toyota\",0,1],[\"2020-12-8\",\"toyota\",1,0],[\"2020-12-8\",\"toyota\",1,2],[\"2020-12-7\",\"toyota\",0,2],[\"2020-12-7\",\"toyota\",0,1],[\"2020-12-8\",\"honda\",1,2],[\"2020-12-8\",\"honda\",2,1],[\"2020-12-7\",\"honda\",0,1],[\"2020-12-7\",\"honda\",1,2],[\"2020-12-7\",\"honda\",2,1]]}}"
#
# Table: DailySales
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | date_id | date |
# | make_name | varchar |
# | lead_id | int |
# | partner_id | int |
# +-------------+---------+
# There is no primary key (column with unique values) for this table. It may
# contain duplicates.
# This table contains the date and the name of the product sold and the IDs of
# the lead and partner it was sold to.
# The name consists of only lowercase English letters.
#
# For each date_id and make_name, find the number of distinct lead_id's and
# distinct partner_id's.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# DailySales table:
# +-----------+-----------+---------+------------+
# | date_id | make_name | lead_id | partner_id |
# +-----------+-----------+---------+------------+
# | 2020-12-8 | toyota | 0 | 1 |
# | 2020-12-8 | toyota | 1 | 0 |
# | 2020-12-8 | toyota | 1 | 2 |
# | 2020-12-7 | toyota | 0 | 2 |
# | 2020-12-7 | toyota | 0 | 1 |
# | 2020-12-8 | honda | 1 | 2 |
# | 2020-12-8 | honda | 2 | 1 |
# | 2020-12-7 | honda | 0 | 1 |
# | 2020-12-7 | honda | 1 | 2 |
# | 2020-12-7 | honda | 2 | 1 |
# +-----------+-----------+---------+------------+
# Output:
# +-----------+-----------+--------------+-----------------+
# | date_id | make_name | unique_leads | unique_partners |
# +-----------+-----------+--------------+-----------------+
# | 2020-12-8 | toyota | 2 | 3 |
# | 2020-12-7 | toyota | 1 | 2 |
# | 2020-12-8 | honda | 2 | 2 |
# | 2020-12-7 | honda | 3 | 2 |
# +-----------+-----------+--------------+-----------------+
# Explanation:
# For 2020-12-8, toyota gets leads = [0, 1] and partners = [0, 1, 2] while
# honda gets leads = [1, 2] and partners = [1, 2].
# For 2020-12-7, toyota gets leads = [0] and partners = [1, 2] while honda gets
# leads = [0, 1, 2] and partners = [1, 2].
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        For each date_id + make_name: count distinct lead_id and partner_id.

        Algorithm:
        - GROUP BY date_id, make_name; COUNT(DISTINCT lead_id/partner_id).

        Complexity: O(D).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT date_id,
           make_name,
           COUNT(DISTINCT lead_id) AS unique_leads,
           COUNT(DISTINCT partner_id) AS unique_partners
    FROM DailySales
    GROUP BY date_id, make_name;
    """
# @lc code=end
