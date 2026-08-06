#
# @lc app=leetcode id=1050 lang=python3
#
# [1050] Actors and Directors Who Cooperated At Least Three Times
#
# https://leetcode.com/problems/actors-and-directors-who-cooperated-at-least-three-times/description/
#
# algorithms
# Easy (71.28%)
# Likes:    808
# Dislikes: 57
# Total Accepted:    342K
# Total Submissions: 480K
# Testcase Example:  "{\"headers\":{\"ActorDirector\":[\"actor_id\",\"director_id\",\"timestamp\"]},\"rows\":{\"ActorDirector\":[[1,1,0],[1,1,1],[1,1,2],[1,2,3],[1,2,4],[2,1,5],[2,1,6]]}}"
#
# Table: ActorDirector
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | actor_id | int |
# | director_id | int |
# | timestamp | int |
# +-------------+---------+
# timestamp is the primary key (column with unique values) for this table.
#
# Write a solution to find all the pairs (actor_id, director_id) where the
# actor has cooperated with the director at least three times.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# ActorDirector table:
# +-------------+-------------+-------------+
# | actor_id | director_id | timestamp |
# +-------------+-------------+-------------+
# | 1 | 1 | 0 |
# | 1 | 1 | 1 |
# | 1 | 1 | 2 |
# | 1 | 2 | 3 |
# | 1 | 2 | 4 |
# | 2 | 1 | 5 |
# | 2 | 1 | 6 |
# +-------------+-------------+-------------+
# Output:
# +-------------+-------------+
# | actor_id | director_id |
# +-------------+-------------+
# | 1 | 1 |
# +-------------+-------------+
# Explanation: The only pair is (1, 1) where they cooperated exactly 3 times.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Count collaborations per (actor_id, director_id) and keep those with
        count >= 3.

        Algorithm:
        - GROUP BY actor_id, director_id HAVING COUNT(*) >= 3

        Complexity: O(n) scan with hash aggregate.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT actor_id, director_id
    FROM ActorDirector
    GROUP BY actor_id, director_id
    HAVING COUNT(*) >= 3;
    """
# @lc code=end
