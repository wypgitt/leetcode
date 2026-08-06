#
# @lc app=leetcode id=1491 lang=python3
#
# [1491] Average Salary Excluding the Minimum and Maximum Salary
#
# https://leetcode.com/problems/average-salary-excluding-the-minimum-and-maximum-salary/description/
#
# algorithms
# Easy (63.55%)
# Likes:    2286
# Dislikes: 187
# Total Accepted:    401K
# Total Submissions: 632K
# Testcase Example:  "[4000,3000,1000,2000]"
#
# You are given an array of unique integers salary where salary[i] is the
# salary of the i^th employee.
#
# Return the average salary of employees excluding the minimum and maximum
# salary. Answers within 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input: salary = [4000,3000,1000,2000]
# Output: 2500.00000
# Explanation: Minimum salary and maximum salary are 1000 and 4000
# respectively.
# Average salary excluding minimum and maximum salary is (2000+3000) / 2 = 2500
#
# Example 2:
#
# Input: salary = [1000,2000,3000]
# Output: 2000.00000
# Explanation: Minimum salary and maximum salary are 1000 and 3000
# respectively.
# Average salary excluding minimum and maximum salary is (2000) / 1 = 2000
#
# Constraints:
#
# 3 <= salary.length <= 100
#
# 1000 <= salary[i] <= 10^6
#
# All the integers of salary are unique.
#

# @lc code=start
from typing import List


class Solution:
    def average(self, salary: List[int]) -> float:
        """
        Interview explanation:
        Average of salaries excluding the unique min and max.

        Algorithm:
        - (sum(salary) - min - max) / (n - 2).

        Complexity: O(n) time, O(1) space.
        """
        return (sum(salary) - min(salary) - max(salary)) / (len(salary) - 2)

    def average_one_pass(self, salary: List[int]) -> float:
        """
        Interview explanation:
        Alternate: single pass tracking sum, min, max.

        Algorithm:
        - Accumulate s, mn, mx; return (s-mn-mx)/(n-2).

        Complexity: O(n) time, O(1) space.
        """
        s = mn = mx = salary[0]
        for x in salary[1:]:
            s += x
            if x < mn:
                mn = x
            if x > mx:
                mx = x
        return (s - mn - mx) / (len(salary) - 2)
# @lc code=end
