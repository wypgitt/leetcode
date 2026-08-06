#
# @lc app=leetcode id=1086 lang=python3
#
# [1086] High Five
#
# https://leetcode.com/problems/high-five/description/
#
# algorithms
# Easy (74.18%)
# Likes:    830
# Dislikes: 131
# Total Accepted:    125.1K
# Total Submissions: 168.7K
# Testcase Example:  "[[1,91],[1,92],[2,93],[2,97],[1,60],[2,77],[1,65],[1,87],[1,100],[2,100],[2,76]]"
#
#
# Given a list of the scores of different students, items, where items[i]
# = [ID_i, score_i] represents one score from a student with ID_i,
# calculate each student's top five average.
#
# Return the answer as an array of pairs result, where result[j] = [ID_j,
# topFiveAverage_j] represents the student with ID_j and their top five
# average. Sort result by ID_j in increasing order.
#
# A student's top five average is calculated by taking the sum of their
# top five scores and dividing it by 5 using integer division.
#
# Example 1:
#
# Input: items =
# [[1,91],[1,92],[2,93],[2,97],[1,60],[2,77],[1,65],[1,87],[1,100],[2,100],[2,76]]
# Output: [[1,87],[2,88]]
# Explanation:
# The student with ID = 1 got scores 91, 92, 60, 65, 87, and 100. Their
# top five average is (100 + 92 + 91 + 87 + 65) / 5 = 87.
# The student with ID = 2 got scores 93, 97, 77, 100, and 76. Their top
# five average is (100 + 97 + 93 + 77 + 76) / 5 = 88.6, but with integer
# division their average converts to 88.
#
# Example 2:
#
# Input: items =
# [[1,100],[7,100],[1,100],[7,100],[1,100],[7,100],[1,100],[7,100],[1,100],[7,100]]
# Output: [[1,100],[7,100]]
#
# Constraints:
#
# 1 <= items.length <= 1000
#
# items[i].length == 2
#
# 1 <= ID_i <= 1000
#
# 0 <= score_i <= 100
#
# For each ID_i, there will be at least five scores.
#
# @lc code=start
from typing import List
from collections import defaultdict
import heapq


class Solution:
    def highFive(self, items: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Premium. For each student_id, keep the top 5 scores and report the
        integer average of those five. Return [id, avg] sorted by id.

        Algorithm (min-heap per student):
        - Map id → min-heap of size ≤5; push score, pop if size>5.
        - avg = sum(heap)//5; sort by id.

        Complexity: O(n log 5 + u log u) ≈ O(n + u log u).
        """
        tops = defaultdict(list)
        for sid, score in items:
            heap = tops[sid]
            heapq.heappush(heap, score)
            if len(heap) > 5:
                heapq.heappop(heap)
        ans = []
        for sid in sorted(tops):
            heap = tops[sid]
            ans.append([sid, sum(heap) // 5])
        return ans
# @lc code=end
