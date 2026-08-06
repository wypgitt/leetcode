#
# @lc app=leetcode id=1700 lang=python3
#
# [1700] Number of Students Unable to Eat Lunch
#
# https://leetcode.com/problems/number-of-students-unable-to-eat-lunch/description/
#
# algorithms
# Easy (79.91%)
# Likes:    2778
# Dislikes: 298
# Total Accepted:    397K
# Total Submissions: 496K
# Testcase Example:  "[1,1,0,0]"
#
# The school cafeteria offers circular and square sandwiches at lunch break,
# referred to by numbers 0 and 1 respectively. All students stand in a queue.
# Each student either prefers square or circular sandwiches.
#
# The number of sandwiches in the cafeteria is equal to the number of students.
# The sandwiches are placed in a stack. At each step:
#
# If the student at the front of the queue prefers the sandwich on the top of
# the stack, they will take it and leave the queue.
#
# Otherwise, they will leave it and go to the queue's end.
#
# This continues until none of the queue students want to take the top sandwich
# and are thus unable to eat.
#
# You are given two integer arrays students and sandwiches where sandwiches[i]
# is the type of the i^th sandwich in the stack (i = 0 is the top of the stack)
# and students[j] is the preference of the j^th student in the initial queue (j
# = 0 is the front of the queue). Return the number of students that are unable
# to eat.
#
# Example 1:
#
# Input: students = [1,1,0,0], sandwiches = [0,1,0,1]
# Output: 0
# Explanation:
# - Front student leaves the top sandwich and returns to the end of the line
# making students = [1,0,0,1].
# - Front student leaves the top sandwich and returns to the end of the line
# making students = [0,0,1,1].
# - Front student takes the top sandwich and leaves the line making students =
# [0,1,1] and sandwiches = [1,0,1].
# - Front student leaves the top sandwich and returns to the end of the line
# making students = [1,1,0].
# - Front student takes the top sandwich and leaves the line making students =
# [1,0] and sandwiches = [0,1].
# - Front student leaves the top sandwich and returns to the end of the line
# making students = [0,1].
# - Front student takes the top sandwich and leaves the line making students =
# [1] and sandwiches = [1].
# - Front student takes the top sandwich and leaves the line making students =
# [] and sandwiches = [].
# Hence all students are able to eat.
#
# Example 2:
#
# Input: students = [1,1,1,0,0,1], sandwiches = [1,0,0,0,1,1]
# Output: 3
#
# Constraints:
#
# 1 <= students.length, sandwiches.length <= 100
#
# students.length == sandwiches.length
#
# sandwiches[i] is 0 or 1.
#
# students[i] is 0 or 1.
#

# @lc code=start
from typing import List
from collections import Counter, deque


class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        """
        Interview explanation:
        Students queue; sandwich stack top. Student takes if preference matches
        top, else goes to queue end. Stop when nobody wants the top sandwich.
        Count remaining students = those preferring the stuck sandwich type.

        Algorithm (count):
        - Count student prefs; for each sandwich in order: if count[s]==0 return remaining;
          else count[s]--.

        Complexity: O(n) time, O(1) space.
        """
        cnt = Counter(students)
        for s in sandwiches:
            if cnt[s] == 0:
                return cnt[0] + cnt[1]
            cnt[s] -= 1
        return 0

    def countStudents_simulate(self, students: List[int], sandwiches: List[int]) -> int:
        """
        Interview explanation:
        Alternate: simulate queue with deque; track consecutive skips.

        Algorithm:
        - While sandwiches: if front matches pop both; else rotate; if rotated n times break.

        Complexity: O(n^2) time, O(n) space.
        """
        q = deque(students)
        i = 0
        skips = 0
        while q and skips < len(q):
            if q[0] == sandwiches[i]:
                q.popleft()
                i += 1
                skips = 0
            else:
                q.append(q.popleft())
                skips += 1
        return len(q)
# @lc code=end
