#
# @lc app=leetcode id=2512 lang=python3
#
# [2512] Reward Top K Students
#
# https://leetcode.com/problems/reward-top-k-students/description/
#
# algorithms
# Medium (47.45%)
# Likes:    370
# Dislikes: 92
# Total Accepted:    32.2K
# Total Submissions: 67.9K
# Testcase Example:  "[\"smart\",\"brilliant\",\"studious\"]\n[\"not\"]\n[\"this student is studious\",\"the student is smart\"]\n[1,2]\n2"
#
# You are given two string arrays positive_feedback and negative_feedback,
# containing the words denoting positive and negative feedback, respectively.
# Note that no word is both positive and negative.
#
# Initially every student has 0 points. Each positive word in a feedback report
# increases the points of a student by 3, whereas each negative word decreases
# the points by 1.
#
# You are given n feedback reports, represented by a 0-indexed string array
# report and a 0-indexed integer array student_id, where student_id[i]
# represents the ID of the student who has received the feedback report
# report[i]. The ID of each student is unique.
#
# Given an integer k, return the top k students after ranking them in
# non-increasing order by their points. In case more than one student has the
# same points, the one with the lower ID ranks higher.
#
#
#
# Example 1:
#
# Input: positive_feedback = ["smart","brilliant","studious"], negative_feedback
# = ["not"], report = ["this student is studious","the student is smart"],
# student_id = [1,2], k = 2
# Output: [1,2]
# Explanation:
# Both the students have 1 positive feedback and 3 points but since student 1
# has a lower ID he ranks higher.
#
# Example 2:
#
# Input: positive_feedback = ["smart","brilliant","studious"], negative_feedback
# = ["not"], report = ["this student is not studious","the student is smart"],
# student_id = [1,2], k = 2
# Output: [2,1]
# Explanation:
# - The student with ID 1 has 1 positive feedback and 1 negative feedback, so he
# has 3-1=2 points.
# - The student with ID 2 has 1 positive feedback, so he has 3 points.
# Since student 2 has more points, [2,1] is returned.
#
#
#
# Constraints:
#
#
# 1 <= positive_feedback.length, negative_feedback.length <= 10^4
#
#
# 1 <= positive_feedback[i].length, negative_feedback[j].length <= 100
#
#
# Both positive_feedback[i] and negative_feedback[j] consists of lowercase
# English letters.
#
#
# No word is present in both positive_feedback and negative_feedback.
#
#
# n == report.length == student_id.length
#
#
# 1 <= n <= 10^4
#
#
# report[i] consists of lowercase English letters and spaces ' '.
#
#
# There is a single space between consecutive words of report[i].
#
#
# 1 <= report[i].length <= 100
#
#
# 1 <= student_id[i] <= 10^9
#
#
# All the values of student_id[i] are unique.
#
#
# 1 <= k <= n
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def topStudents(self, positive_feedback: List[str], negative_feedback: List[str], report: List[str], student_id: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Score each student (+3 per positive word, -1 per negative), return top k
        IDs by score desc, then ID asc.

        Algorithm:
        - Build feedback sets; score each report; sort by (-score, id); take k.

        Complexity: O(W + L + n log n) time, O(W + n) space (W words, L report length).
        """
        pos = set(positive_feedback)
        neg = set(negative_feedback)
        scores = []
        for sid, text in zip(student_id, report):
            score = 0
            for w in text.split():
                if w in pos:
                    score += 3
                elif w in neg:
                    score -= 1
            scores.append((-score, sid))
        scores.sort()
        return [sid for _, sid in scores[:k]]

    def topStudents_heap(self, positive_feedback: List[str], negative_feedback: List[str], report: List[str], student_id: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Same ranking; keep a size-k heap of worst among current top-k.

        Algorithm:
        - Score students; heap of (score, -id) size k; extract and reverse.

        Complexity: O(W + L + n log k) time, O(W + k) space.
        """
        pos = set(positive_feedback)
        neg = set(negative_feedback)
        heap = []
        for sid, text in zip(student_id, report):
            score = 0
            for w in text.split():
                if w in pos:
                    score += 3
                elif w in neg:
                    score -= 1
            # min-heap of "worst" among top-k: smaller score / larger id pops first
            item = (score, -sid)
            if len(heap) < k:
                heapq.heappush(heap, item)
            elif item > heap[0]:
                heapq.heapreplace(heap, item)
        ans = []
        while heap:
            score, neg_sid = heapq.heappop(heap)
            ans.append(-neg_sid)
        ans.reverse()
        return ans
# @lc code=end
