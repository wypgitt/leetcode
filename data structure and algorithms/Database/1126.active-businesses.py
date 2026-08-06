#
# @lc app=leetcode id=1126 lang=python3
#
# [1126] Active Businesses
#
# https://leetcode.com/problems/active-businesses/description/
#
# database
# Medium (66.01%)
# Likes:    285
# Dislikes: 34
# Total Accepted:    53.6K
# Total Submissions: 81.1K
# Testcase Example:  "{\"headers\":{\"Events\":[\"business_id\",\"event_type\",\"occurrences\"]},\"rows\":{\"Events\":[[1,\"reviews\",7],[3,\"reviews\",3],[1,\"ads\",11],[2,\"ads\",7],[3,\"ads\",6],[1,\"page views\",3],[2,\"page views\",12]]}}"
#
#
# Table: Events
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | business_id   | int     |
# | event_type    | varchar |
# | occurrences   | int     |
# +---------------+---------+
# (business_id, event_type) is the primary key (combination of columns
# with unique values) of this table.
# Each row in the table logs the info that an event of some type occurred
# at some business for a number of times.
#
# The average activity for a particular event_type is the average
# occurrences across all companies that have this event.
#
# An active business is a business that has more than one event_type such
# that their occurrences is strictly greater than the average activity for
# that event.
#
# Write a solution to find all active businesses.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Events table:
# +-------------+------------+-------------+
# | business_id | event_type | occurrences |
# +-------------+------------+-------------+
# | 1           | reviews    | 7           |
# | 3           | reviews    | 3           |
# | 1           | ads        | 11          |
# | 2           | ads        | 7           |
# | 3           | ads        | 6           |
# | 1           | page views | 3           |
# | 2           | page views | 12          |
# +-------------+------------+-------------+
# Output:
# +-------------+
# | business_id |
# +-------------+
# | 1           |
# +-------------+
# Explanation:
# The average activity for each event can be calculated as follows:
# - 'reviews': (7+3)/2 = 5
# - 'ads': (11+7+6)/3 = 8
# - 'page views': (3+12)/2 = 7.5
# The business with id=1 has 7 'reviews' events (more than 5) and 11 'ads'
# events (more than 8), so it is an active business.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. An active business has >1 event types where its
        occurrences exceed the average occurrences of that event type.

        Algorithm:
        - Compute AVG(occurrences) per event_type.
        - Join Events to averages; keep rows with occurrences > avg.
        - GROUP BY business_id HAVING COUNT(DISTINCT event_type) > 1
          (or COUNT(*) > 1 since (business, event) is unique).

        Complexity: O(N) with aggregation + join.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT e.business_id
    FROM Events e
    JOIN (
        SELECT event_type, AVG(occurrences) AS avg_occ
        FROM Events
        GROUP BY event_type
    ) a ON e.event_type = a.event_type
    WHERE e.occurrences > a.avg_occ
    GROUP BY e.business_id
    HAVING COUNT(*) > 1;
    """
# @lc code=end
