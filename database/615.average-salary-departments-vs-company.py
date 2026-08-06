#
# @lc app=leetcode id=615 lang=python3
#
# [615] Average Salary: Departments VS Company
#
# https://leetcode.com/problems/average-salary-departments-vs-company/description/
#
# database
# Hard (56.62%)
# Likes:    243
# Dislikes: 77
# Total Accepted:    44.5K
# Total Submissions: 78.7K
# Testcase Example:  "{\"headers\":{\"Salary\":[\"id\",\"employee_id\",\"amount\",\"pay_date\"],\"Employee\":[\"employee_id\",\"department_id\"]},\"rows\":{\"Salary\":[[1,1,9000,\"2017/03/31\"],[2,2,6000,\"2017/03/31\"],[3,3,10000,\"2017/03/31\"],[4,1,7000,\"2017/02/28\"],[5,2,6000,\"2017/02/28\"],[6,3,8000,\"2017/02/28\"]],\"Employee\":[[1,1],[2,2],[3,2]]}}"
#
#
# Table: Salary
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | id          | int  |
# | employee_id | int  |
# | amount      | int  |
# | pay_date    | date |
# +-------------+------+
# In SQL, id is the primary key column for this table.
# Each row of this table indicates the salary of an employee in one month.
# employee_id is a foreign key (reference column) from the Employee table.
#
# Table: Employee
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | employee_id   | int  |
# | department_id | int  |
# +---------------+------+
# In SQL, employee_id is the primary key column for this table.
# Each row of this table indicates the department of an employee.
#
# Find the comparison result (higher/lower/same) of the average salary of
# employees in a department to the company's average salary.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Salary table:
# +----+-------------+--------+------------+
# | id | employee_id | amount | pay_date   |
# +----+-------------+--------+------------+
# | 1  | 1           | 9000   | 2017/03/31 |
# | 2  | 2           | 6000   | 2017/03/31 |
# | 3  | 3           | 10000  | 2017/03/31 |
# | 4  | 1           | 7000   | 2017/02/28 |
# | 5  | 2           | 6000   | 2017/02/28 |
# | 6  | 3           | 8000   | 2017/02/28 |
# +----+-------------+--------+------------+
# Employee table:
# +-------------+---------------+
# | employee_id | department_id |
# +-------------+---------------+
# | 1           | 1             |
# | 2           | 2             |
# | 3           | 2             |
# +-------------+---------------+
# Output:
# +-----------+---------------+------------+
# | pay_month | department_id | comparison |
# +-----------+---------------+------------+
# | 2017-02   | 1             | same       |
# | 2017-03   | 1             | higher     |
# | 2017-02   | 2             | same       |
# | 2017-03   | 2             | lower      |
# +-----------+---------------+------------+
# Explanation:
# In March, the company's average salary is (9000+6000+10000)/3 =
# 8333.33...
# The average salary for department '1' is 9000, which is the salary of
# employee_id '1' since there is only one employee in this department. So
# the comparison result is 'higher' since 9000 > 8333.33 obviously.
# The average salary of department '2' is (6000 + 10000)/2 = 8000, which
# is the average of employee_id '2' and '3'. So the comparison result is
# 'lower' since 8000 < 8333.33.
#
# With he same formula for the average salary comparison in February, the
# result is 'same' since both the department '1' and '2' have the same
# average salary with the company, which is 7000.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Compare each department's monthly average salary to the company monthly average.

        Algorithm:
        - Aggregate company AVG(amount) by YYYY-MM.
        - Aggregate department AVG by month via Salary⋈Employee.
        - CASE compare dept_avg vs company_avg → higher/lower/same.

        Complexity: O(S) aggregations.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    WITH company_avg AS (
        SELECT DATE_FORMAT(pay_date, '%Y-%m') AS pay_month,
               AVG(amount) AS company_avg
        FROM Salary
        GROUP BY DATE_FORMAT(pay_date, '%Y-%m')
    ),
    dept_avg AS (
        SELECT DATE_FORMAT(s.pay_date, '%Y-%m') AS pay_month,
               e.department_id,
               AVG(s.amount) AS dept_avg
        FROM Salary s
        JOIN Employee e ON s.employee_id = e.employee_id
        GROUP BY DATE_FORMAT(s.pay_date, '%Y-%m'), e.department_id
    )
    SELECT
        d.pay_month,
        d.department_id,
        CASE
            WHEN d.dept_avg > c.company_avg THEN 'higher'
            WHEN d.dept_avg < c.company_avg THEN 'lower'
            ELSE 'same'
        END AS comparison
    FROM dept_avg d
    JOIN company_avg c ON d.pay_month = c.pay_month;
    """
# @lc code=end
