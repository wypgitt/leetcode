#
# @lc app=leetcode id=2041 lang=python3
#
# [2041] Accepted Candidates From the Interviews
#
# https://leetcode.com/problems/accepted-candidates-from-the-interviews/description/
#
# database
# Medium (78.42%)
# Likes:    58
# Dislikes: 28
# Total Accepted:    17K
# Total Submissions: 21.7K
# Testcase Example:  "{\"headers\":{\"Candidates\":[\"candidate_id\",\"name\",\"years_of_exp\",\"interview_id\"],\"Rounds\":[\"interview_id\",\"round_id\",\"score\"]},\"rows\":{\"Candidates\":[[11,\"Atticus\",1,101],[9,\"Ruben\",6,104],[6,\"Aliza\",10,109],[8,\"Alfredo\",0,107]],\"Rounds\":[[109,3,4],[101,2,8],[109,4,1],[107,1,3],[104,3,6],[109,1,4],[104,4,7],[104,1,2],[109,2,1],[104,2,7],[107,2,3],[101,1,8]]}}"
#
#
# Table: Candidates
#
# +--------------+----------+
# | Column Name  | Type     |
# +--------------+----------+
# | candidate_id | int      |
# | name         | varchar  |
# | years_of_exp | int      |
# | interview_id | int      |
# +--------------+----------+
# candidate_id is the primary key (column with unique values) for this
# table.
# Each row of this table indicates the name of a candidate, their number
# of years of experience, and their interview ID.
#
# Table: Rounds
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | interview_id | int  |
# | round_id     | int  |
# | score        | int  |
# +--------------+------+
# (interview_id, round_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates the score of one round of an interview.
#
# Write a solution to report the IDs of the candidates who have at least
# two years of experience and the sum of the score of their interview
# rounds is strictly greater than 15.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Candidates table:
# +--------------+---------+--------------+--------------+
# | candidate_id | name    | years_of_exp | interview_id |
# +--------------+---------+--------------+--------------+
# | 11           | Atticus | 1            | 101          |
# | 9            | Ruben   | 6            | 104          |
# | 6            | Aliza   | 10           | 109          |
# | 8            | Alfredo | 0            | 107          |
# +--------------+---------+--------------+--------------+
# Rounds table:
# +--------------+----------+-------+
# | interview_id | round_id | score |
# +--------------+----------+-------+
# | 109          | 3        | 4     |
# | 101          | 2        | 8     |
# | 109          | 4        | 1     |
# | 107          | 1        | 3     |
# | 104          | 3        | 6     |
# | 109          | 1        | 4     |
# | 104          | 4        | 7     |
# | 104          | 1        | 2     |
# | 109          | 2        | 1     |
# | 104          | 2        | 7     |
# | 107          | 2        | 3     |
# | 101          | 1        | 8     |
# +--------------+----------+-------+
# Output:
# +--------------+
# | candidate_id |
# +--------------+
# | 9            |
# +--------------+
# Explanation:
# - Candidate 11: The total score is 16, and they have one year of
# experience. We do not include them in the result table because of their
# years of experience.
# - Candidate 9: The total score is 22, and they have six years of
# experience. We include them in the result table.
# - Candidate 6: The total score is 10, and they have ten years of
# experience. We do not include them in the result table because the score
# is not good enough.
# - Candidate 8: The total score is 6, and they have zero years of
# experience. We do not include them in the result table because of their
# years of experience and the score.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Candidates(candidate_id, name, years_of_exp, interview_id) and
        Rounds(interview_id, round_id, score). Accept candidates with
        years_of_exp >= 2 and total interview score > 15; return candidate_id, name.

        Algorithm:
        - JOIN + GROUP BY interview; HAVING SUM(score) > 15 AND years_of_exp >= 2.

        Complexity: O(N).
        """
        self.sql = """
SELECT c.candidate_id, c.name
FROM Candidates c
JOIN Rounds r ON c.interview_id = r.interview_id
WHERE c.years_of_exp >= 2
GROUP BY c.candidate_id, c.name
HAVING SUM(r.score) > 15;
"""
        return self.sql
# @lc code=end
