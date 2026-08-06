#
# @lc app=leetcode id=3278 lang=python3
#
# [3278] Find Candidates for Data Scientist Position II
#
# https://leetcode.com/problems/find-candidates-for-data-scientist-position-ii/description/
#
# database
# Medium (43.15%)
# Likes:    12
# Dislikes: 5
# Total Accepted:    2.4K
# Total Submissions: 5.5K
# Testcase Example:  "{\"headers\":{\"Candidates\":[\"candidate_id\",\"skill\",\"proficiency\"],\"Projects\":[\"project_id\",\"skill\",\"importance\"]},\"rows\":{\"Candidates\":[[101,\"Python\",5],[101,\"Tableau\",3],[101,\"PostgreSQL\",4],[101,\"TensorFlow\",2],[102,\"Python\",4],[102,\"Tableau\",5],[102,\"PostgreSQL\",4],[102,\"R\",4],[103,\"Python\",3],[103,\"Tableau\",5],[103,\"PostgreSQL\",5],[103,\"Spark\",4]],\"Projects\":[[501,\"Python\",4],[501,\"Tableau\",3],[501,\"PostgreSQL\",5],[502,\"Python\",3],[502,\"Tableau\",4],[502,\"R\",2]]}}"
#
#
# Table: Candidates
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | candidate_id | int     |
# | skill        | varchar |
# | proficiency  | int     |
# +--------------+---------+
# (candidate_id, skill) is the unique key for this table.
# Each row includes candidate_id, skill, and proficiency level (1-5).
#
# Table: Projects
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | project_id   | int     |
# | skill        | varchar |
# | importance   | int     |
# +--------------+---------+
# (project_id, skill) is the primary key for this table.
# Each row includes project_id, required skill, and its importance (1-5)
# for the project.
#
# Leetcode is staffing for multiple data science projects. Write a
# solution to find the best candidate for each project based on the
# following criteria:
#
# Candidates must have all the skills required for a project.
#
# Calculate a score for each candidate-project pair as follows:
#
# Start with 100 points
#
# Add 10 points for each skill where proficiency > importance
#
# Subtract 5 points for each skill where proficiency < importance
#
# If the candidate's skill proficiency equal to the project's skill
# importance, the score remains unchanged
#
# Include only the top candidate (highest score) for each project. If
# there’s a tie, choose the candidate with the lower candidate_id. If
# there is no suitable candidate for a project, do not return that
# project.
#
# Return a result table ordered by project_id in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Candidates table:
#
# +--------------+-----------+-------------+
# | candidate_id | skill     | proficiency |
# +--------------+-----------+-------------+
# | 101          | Python    | 5           |
# | 101          | Tableau   | 3           |
# | 101          | PostgreSQL| 4           |
# | 101          | TensorFlow| 2           |
# | 102          | Python    | 4           |
# | 102          | Tableau   | 5           |
# | 102          | PostgreSQL| 4           |
# | 102          | R         | 4           |
# | 103          | Python    | 3           |
# | 103          | Tableau   | 5           |
# | 103          | PostgreSQL| 5           |
# | 103          | Spark     | 4           |
# +--------------+-----------+-------------+
#
# Projects table:
#
# +-------------+-----------+------------+
# | project_id  | skill     | importance |
# +-------------+-----------+------------+
# | 501         | Python    | 4          |
# | 501         | Tableau   | 3          |
# | 501         | PostgreSQL| 5          |
# | 502         | Python    | 3          |
# | 502         | Tableau   | 4          |
# | 502         | R         | 2          |
# +-------------+-----------+------------+
#
# Output:
#
# +-------------+--------------+-------+
# | project_id  | candidate_id | score |
# +-------------+--------------+-------+
# | 501         | 101          | 105   |
# | 502         | 102          | 130   |
# +-------------+--------------+-------+
#
# Explanation:
#
# For Project 501, Candidate 101 has the highest score of 105. All other
# candidates have the same score but Candidate 101 has the lowest
# candidate_id among them.
#
# For Project 502, Candidate 102 has the highest score of 130.
#
# The output table is ordered by project_id in ascending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: for each project, pick the best candidate who has every
        required skill. Score = 100 + 10*(prof>imp) - 5*(prof<imp). Ties break
        by smaller candidate_id. Order by project_id ASC.

        Algorithm:
        - Join project skills to candidate skills; require COUNT matched = project
          skill count (candidate has all skills).
        - Aggregate score; ROW_NUMBER by score DESC, candidate_id ASC; keep rn=1.

        Complexity: O(N) with hash joins / grouping.
        """
        self.sql = """
WITH proj_size AS (
  SELECT project_id, COUNT(*) AS cnt
  FROM Projects
  GROUP BY project_id
),
cand_scores AS (
  SELECT
    p.project_id,
    c.candidate_id,
    100
      + 10 * SUM(c.proficiency > p.importance)
      - 5 * SUM(c.proficiency < p.importance) AS score,
    COUNT(*) AS matched
  FROM Projects p
  JOIN Candidates c
    ON c.skill = p.skill
  GROUP BY p.project_id, c.candidate_id
),
eligible AS (
  SELECT cs.project_id, cs.candidate_id, cs.score
  FROM cand_scores cs
  JOIN proj_size ps ON ps.project_id = cs.project_id
  WHERE cs.matched = ps.cnt
),
ranked AS (
  SELECT
    project_id,
    candidate_id,
    score,
    ROW_NUMBER() OVER (
      PARTITION BY project_id
      ORDER BY score DESC, candidate_id ASC
    ) AS rn
  FROM eligible
)
SELECT project_id, candidate_id, score
FROM ranked
WHERE rn = 1
ORDER BY project_id;
"""
        return self.sql
# @lc code=end
