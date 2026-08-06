#
# @lc app=leetcode id=630 lang=python3
#
# [630] Course Schedule III
#
# https://leetcode.com/problems/course-schedule-iii/description/
#
# algorithms
# Hard (41.99%)
# Likes:    4040
# Dislikes: 104
# Total Accepted:    147K
# Total Submissions: 350K
# Testcase Example:  "[[100,200],[200,1300],[1000,1250],[2000,3200]]"
#
# There are n different online courses numbered from 1 to n. You are given an
# array courses where courses[i] = [duration_i, lastDay_i] indicate that the
# i^th course should be taken continuously for duration_i days and must be
# finished before or on lastDay_i.
#
# You will start on the 1^st day and you cannot take two or more courses
# simultaneously.
#
# Return the maximum number of courses that you can take.
#
# Example 1:
#
# Input: courses = [[100,200],[200,1300],[1000,1250],[2000,3200]]
# Output: 3
# Explanation:
# There are totally 4 courses, but you can take 3 courses at most:
# First, take the 1^st course, it costs 100 days so you will finish it on the
# 100^th day, and ready to take the next course on the 101^st day.
# Second, take the 3^rd course, it costs 1000 days so you will finish it on the
# 1100^th day, and ready to take the next course on the 1101^st day.
# Third, take the 2^nd course, it costs 200 days so you will finish it on the
# 1300^th day.
# The 4^th course cannot be taken now, since you will finish it on the 3300^th
# day, which exceeds the closed date.
#
# Example 2:
#
# Input: courses = [[1,2]]
# Output: 1
#
# Example 3:
#
# Input: courses = [[3,2],[4,3]]
# Output: 0
#
# Constraints:
#
# 1 <= courses.length <= 10^4
#
# 1 <= duration_i, lastDay_i <= 10^4
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def scheduleCourse(self, courses: List[List[int]]) -> int:
        """
        Interview explanation:
        Take as many courses as possible before their deadlines. Greedy: sort by
        lastDay; take course if it fits; if not and it is shorter than the longest
        already taken, swap (max-heap of durations).

        Algorithm:
        - Sort courses by lastDay ascending.
        - Max-heap (negated) of taken durations; time = sum durations.
        - For each course: push duration; if time > lastDay, pop longest.

        Complexity: O(N log N) time, O(N) space.
        """
        courses.sort(key=lambda c: c[1])
        heap = []
        time = 0
        for duration, last in courses:
            heapq.heappush(heap, -duration)
            time += duration
            if time > last:
                time += heapq.heappop(heap)  # remove longest (negative)
        return len(heap)
# @lc code=end
