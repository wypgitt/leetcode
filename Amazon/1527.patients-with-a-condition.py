#
# @lc app=leetcode id=1527 lang=python3
#
# [1527] Patients With a Condition
#
# https://leetcode.com/problems/patients-with-a-condition/description/
#
# algorithms
# Easy (39.12%)
# Likes:    896
# Dislikes: 662
# Total Accepted:    480K
# Total Submissions: 1.2M
# Testcase Example:  "{\"headers\": {\"Patients\": [\"patient_id\", \"patient_name\", \"conditions\"]}, \"rows\": {\"Patients\": [[1, \"Daniel\", \"YFEV COUGH\"], [2, \"Alice\", \"\"], [3, \"Bob\", \"DIAB100 MYOP\"], [4, \"George\", \"ACNE DIAB100\"], [5, \"Alain\", \"DIAB201\"]]}}"
#
# Table: Patients
#
# +--------------+---------+
# | Column Name | Type |
# +--------------+---------+
# | patient_id | int |
# | patient_name | varchar |
# | conditions | varchar |
# +--------------+---------+
# patient_id is the primary key (column with unique values) for this table.
# 'conditions' contains 0 or more code separated by spaces.
# This table contains information of the patients in the hospital.
#
# Write a solution to find the patient_id, patient_name, and conditions of the
# patients who have Type I Diabetes. Type I Diabetes always starts with DIAB1
# prefix.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Patients table:
# +------------+--------------+--------------+
# | patient_id | patient_name | conditions |
# +------------+--------------+--------------+
# | 1 | Daniel | YFEV COUGH |
# | 2 | Alice | |
# | 3 | Bob | DIAB100 MYOP |
# | 4 | George | ACNE DIAB100 |
# | 5 | Alain | DIAB201 |
# +------------+--------------+--------------+
# Output:
# +------------+--------------+--------------+
# | patient_id | patient_name | conditions |
# +------------+--------------+--------------+
# | 3 | Bob | DIAB100 MYOP |
# | 4 | George | ACNE DIAB100 |
# +------------+--------------+--------------+
# Explanation: Bob and George both have a condition that starts with DIAB1.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL. Patients whose conditions list contains DIAB1 as a condition code
        (space-separated). Match 'DIAB1%' at start or ' DIAB1%' inside.

        Algorithm:
        - WHERE conditions LIKE 'DIAB1%' OR conditions LIKE '% DIAB1%'.

        Complexity: O(P) scan.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT patient_id, patient_name, conditions
    FROM Patients
    WHERE conditions LIKE 'DIAB1%' OR conditions LIKE '% DIAB1%';
    """
# @lc code=end
