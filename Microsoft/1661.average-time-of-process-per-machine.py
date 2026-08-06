#
# @lc app=leetcode id=1661 lang=python3
#
# [1661] Average Time of Process per Machine
#
# https://leetcode.com/problems/average-time-of-process-per-machine/description/
#
# algorithms
# Easy (66.9%)
# Likes:    2567
# Dislikes: 252
# Total Accepted:    848K
# Total Submissions: 1.3M
# Testcase Example:  "{\"headers\":{\"Activity\":[\"machine_id\",\"process_id\",\"activity_type\",\"timestamp\"]},\"rows\":{\"Activity\":[[0,0,\"start\",0.712],[0,0,\"end\",1.52],[0,1,\"start\",3.14],[0,1,\"end\",4.12],[1,0,\"start\",0.55],[1,0,\"end\",1.55],[1,1,\"start\",0.43],[1,1,\"end\",1.42],[2,0,\"start\",4.1],[2,0,\"end\",4.512],[2,1,\"start\",2.5],[2,1,\"end\",5]]}}"
#
# Table: Activity
#
# +----------------+---------+
# | Column Name | Type |
# +----------------+---------+
# | machine_id | int |
# | process_id | int |
# | activity_type | enum |
# | timestamp | float |
# +----------------+---------+
# The table shows the user activities for a factory website.
# (machine_id, process_id, activity_type) is the primary key (combination of
# columns with unique values) of this table.
# machine_id is the ID of a machine.
# process_id is the ID of a process running on the machine with ID machine_id.
# activity_type is an ENUM (category) of type ('start', 'end').
# timestamp is a float representing the current time in seconds.
# 'start' means the machine starts the process at the given timestamp and 'end'
# means the machine ends the process at the given timestamp.
# The `start` timestamp will always be less than or equal to the `end`
# timestamp for every `(machine_id, process_id)` pair.
# It is guaranteed that each (machine_id, process_id) pair has a 'start' and
# 'end' timestamp.
#
# There is a factory website that has several machines each running the same
# number of processes. Write a solution to find the average time each machine
# takes to complete a process.
#
# The time to complete a process is the 'end' timestamp minus the 'start'
# timestamp. The average time is calculated by the total time to complete every
# process on the machine divided by the number of processes that were run.
#
# The resulting table should have the machine_id along with the average time as
# processing_time, which should be rounded to 3 decimal places.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Activity table:
# +------------+------------+---------------+-----------+
# | machine_id | process_id | activity_type | timestamp |
# +------------+------------+---------------+-----------+
# | 0 | 0 | start | 0.712 |
# | 0 | 0 | end | 1.520 |
# | 0 | 1 | start | 3.140 |
# | 0 | 1 | end | 4.120 |
# | 1 | 0 | start | 0.550 |
# | 1 | 0 | end | 1.550 |
# | 1 | 1 | start | 0.430 |
# | 1 | 1 | end | 1.420 |
# | 2 | 0 | start | 4.100 |
# | 2 | 0 | end | 4.512 |
# | 2 | 1 | start | 2.500 |
# | 2 | 1 | end | 5.000 |
# +------------+------------+---------------+-----------+
# Output:
# +------------+-----------------+
# | machine_id | processing_time |
# +------------+-----------------+
# | 0 | 0.894 |
# | 1 | 0.995 |
# | 2 | 1.456 |
# +------------+-----------------+
# Explanation:
# There are 3 machines running 2 processes each.
# Machine 0's average time is ((1.520 - 0.712) + (4.120 - 3.140)) / 2 = 0.894
# Machine 1's average time is ((1.550 - 0.550) + (1.420 - 0.430)) / 2 = 0.995
# Machine 2's average time is ((4.512 - 4.100) + (5.000 - 2.500)) / 2 = 1.456
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Per machine, average (end-start) over processes; round to 3 decimals.

        Algorithm:
        - Self-join Activity start/end on (machine_id, process_id); AVG(end-start);
          ROUND(..., 3).

        Complexity: O(A).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT a.machine_id,
           ROUND(AVG(b.timestamp - a.timestamp), 3) AS processing_time
    FROM Activity a
    JOIN Activity b
      ON a.machine_id = b.machine_id
     AND a.process_id = b.process_id
     AND a.activity_type = 'start'
     AND b.activity_type = 'end'
    GROUP BY a.machine_id;
    """
# @lc code=end
