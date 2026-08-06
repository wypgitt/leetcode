#
# @lc app=leetcode id=1204 lang=python3
#
# [1204] Last Person to Fit in the Bus
#
# https://leetcode.com/problems/last-person-to-fit-in-the-bus/description/
#
# algorithms
# Medium (69.65%)
# Likes:    1158
# Dislikes: 51
# Total Accepted:    370K
# Total Submissions: 531K
# Testcase Example:  "{\"headers\":{\"Queue\":[\"person_id\",\"person_name\",\"weight\",\"turn\"]},\"rows\":{\"Queue\":[[5,\"Alice\",250,1],[4,\"Bob\",175,5],[3,\"Alex\",350,2],[6,\"John Cena\",400,3],[1,\"Winston\",500,6],[2,\"Marie\",200,4]]}}"
#
# Table: Queue
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | person_id | int |
# | person_name | varchar |
# | weight | int |
# | turn | int |
# +-------------+---------+
# person_id column contains unique values.
# This table has the information about all people waiting for a bus.
# The person_id and turn columns will contain all numbers from 1 to n, where n
# is the number of rows in the table.
# turn determines the order of which the people will board the bus, where
# turn=1 denotes the first person to board and turn=n denotes the last person
# to board.
# weight is the weight of the person in kilograms.
#
# There is a queue of people waiting to board a bus. However, the bus has a
# weight limit of 1000 kilograms, so there may be some people who cannot board.
#
# Write a solution to find the person_name of the last person that can fit on
# the bus without exceeding the weight limit. The test cases are generated such
# that the first person does not exceed the weight limit.
#
# Note that only one person can board the bus at any given turn.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Queue table:
# +-----------+-------------+--------+------+
# | person_id | person_name | weight | turn |
# +-----------+-------------+--------+------+
# | 5 | Alice | 250 | 1 |
# | 4 | Bob | 175 | 5 |
# | 3 | Alex | 350 | 2 |
# | 6 | John Cena | 400 | 3 |
# | 1 | Winston | 500 | 6 |
# | 2 | Marie | 200 | 4 |
# +-----------+-------------+--------+------+
# Output:
# +-------------+
# | person_name |
# +-------------+
# | John Cena |
# +-------------+
# Explanation: The folowing table is ordered by the turn for simplicity.
# +------+----+-----------+--------+--------------+
# | Turn | ID | Name | Weight | Total Weight |
# +------+----+-----------+--------+--------------+
# | 1 | 5 | Alice | 250 | 250 |
# | 2 | 3 | Alex | 350 | 600 |
# | 3 | 6 | John Cena | 400 | 1000 | (last person to board)
# | 4 | 2 | Marie | 200 | 1200 | (cannot board)
# | 5 | 4 | Bob | 175 | ___ |
# | 6 | 1 | Winston | 500 | ___ |
# +------+----+-----------+--------+--------------+
#


# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Board people in turn order; cumulative weight must stay <= 1000.
        Return the name of the last person whose prefix sum is still <= 1000.

        Algorithm:
        - Window SUM(weight) OVER (ORDER BY turn) AS total
        - Filter total <= 1000; ORDER BY turn DESC; LIMIT 1 person_name

        Complexity: O(N log N) with sort/window.
        """
        return self.sql

    sql = """
    SELECT person_name
    FROM (
        SELECT person_name, turn,
               SUM(weight) OVER (ORDER BY turn) AS total
        FROM Queue
    ) t
    WHERE total <= 1000
    ORDER BY turn DESC
    LIMIT 1;
    """
# @lc code=end
