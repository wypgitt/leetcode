#
# @lc app=leetcode id=3450 lang=python3
#
# [3450] Maximum Students on a Single Bench
#
# https://leetcode.com/problems/maximum-students-on-a-single-bench/description/
#
# algorithms
# Easy (87.93%)
# Likes:    15
# Dislikes: 1
# Total Accepted:    2.4K
# Total Submissions: 2.8K
# Testcase Example:  "[[1,2],[2,2],[3,3],[1,3],[2,3]]"
#
#
# You are given a 2D integer array of student data students, where
# students[i] = [student_id, bench_id] represents that student student_id
# is sitting on the bench bench_id.
#
# Return the maximum number of unique students sitting on any single
# bench. If no students are present, return 0.
#
# Note: A student can appear multiple times on the same bench in the
# input, but they should be counted only once per bench.
#
# Example 1:
#
# Input: students = [[1,2],[2,2],[3,3],[1,3],[2,3]]
#
# Output: 3
#
# Explanation:
#
# Bench 2 has two unique students: [1, 2].
#
# Bench 3 has three unique students: [1, 2, 3].
#
# The maximum number of unique students on a single bench is 3.
#
# Example 2:
#
# Input: students = [[1,1],[2,1],[3,1],[4,2],[5,2]]
#
# Output: 3
#
# Explanation:
#
# Bench 1 has three unique students: [1, 2, 3].
#
# Bench 2 has two unique students: [4, 5].
#
# The maximum number of unique students on a single bench is 3.
#
# Example 3:
#
# Input: students = [[1,1],[1,1]]
#
# Output: 1
#
# Explanation:
#
# The maximum number of unique students on a single bench is 1.
#
# Example 4:
#
# Input: students = []
#
# Output: 0
#
# Explanation:
#
# Since no students are present, the output is 0.
#
# Constraints:
#
# 0 <= students.length <= 100
#
# students[i] = [student_id, bench_id]
#
# 1 <= student_id <= 100
#
# 1 <= bench_id <= 100
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def maxStudentsOnBench(self, students: List[List[int]]) -> int:
        """
        Interview explanation:
        Per bench, count unique student ids; return the maximum (0 if empty).

        Algorithm:
        - Map bench -> set of students; take max set size.

        Complexity: O(n) time, O(n) space.
        """
        if not students:
            return 0
        benches: dict[int, set[int]] = defaultdict(set)
        for sid, bid in students:
            benches[bid].add(sid)
        return max(len(s) for s in benches.values())
# @lc code=end
