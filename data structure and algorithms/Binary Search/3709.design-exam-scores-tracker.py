#
# @lc app=leetcode id=3709 lang=python3
#
# [3709] Design Exam Scores Tracker
#
# https://leetcode.com/problems/design-exam-scores-tracker/description/
#
# algorithms
# Medium (44.40%)
# Likes:    62
# Dislikes: 1
# Total Accepted:    20.2K
# Total Submissions: 45.6K
# Testcase Example:  "[\"ExamTracker\",\"record\",\"totalScore\",\"record\",\"totalScore\",\"totalScore\",\"totalScore\",\"totalScore\"]\n[[],[1,98],[1,1],[5,99],[1,3],[1,5],[3,4],[2,5]]"
#
#
# Alice frequently takes exams and wants to track her scores and calculate
# the total scores over specific time periods.
#
# Implement the ExamTracker class:
#
# ExamTracker(): Initializes the ExamTracker object.
#
# void record(int time, int score): Alice takes a new exam at time time
# and achieves the score score.
#
# long long totalScore(int startTime, int endTime): Returns an integer
# that represents the total score of all exams taken by Alice between
# startTime and endTime (inclusive). If there are no recorded exams taken
# by Alice within the specified time interval, return 0.
#
# It is guaranteed that the function calls are made in chronological
# order. That is,
#
# Calls to record() will be made with strictly increasing time.
#
# Alice will never ask for total scores that require information from the
# future. That is, if the latest record() is called with time = t, then
# totalScore() will always be called with startTime <= endTime <= t.
#
# Example 1:
#
# Input:
#
# ["ExamTracker", "record", "totalScore", "record", "totalScore",
# "totalScore", "totalScore", "totalScore"]
#
# [[], [1, 98], [1, 1], [5, 99], [1, 3], [1, 5], [3, 4], [2, 5]]
#
# Output:
#
# [null, null, 98, null, 98, 197, 0, 99]
#
# Explanation
#
# ExamTracker examTracker = new ExamTracker();
#
# examTracker.record(1, 98); // Alice takes a new exam at time 1, scoring
# 98.
#
# examTracker.totalScore(1, 1); // Between time 1 and time 1, Alice took 1
# exam at time 1, scoring 98. The total score is 98.
#
# examTracker.record(5, 99); // Alice takes a new exam at time 5, scoring
# 99.
#
# examTracker.totalScore(1, 3); // Between time 1 and time 3, Alice took 1
# exam at time 1, scoring 98. The total score is 98.
#
# examTracker.totalScore(1, 5); // Between time 1 and time 5, Alice took 2
# exams at time 1 and 5, scoring 98 and 99. The total score is 98 + 99 =
# 197.
#
# examTracker.totalScore(3, 4); // Alice did not take any exam between
# time 3 and time 4. Therefore, the answer is 0.
#
# examTracker.totalScore(2, 5); // Between time 2 and time 5, Alice took 1
# exam at time 5, scoring 99. The total score is 99.
#
# Constraints:
#
# 1 <= time <= 10^9
#
# 1 <= score <= 10^9
#
# 1 <= startTime <= endTime <= t, where t is the value of time from the
# most recent call of record().
#
# Calls of record() will be made with strictly increasing time.
#
# After ExamTracker(), the first function call will always be record().
#
# At most 10^5 calls will be made in total to record() and totalScore().
#

# @lc code=start

import bisect
from typing import List


class ExamTracker:
    """
    Interview explanation:
    Chronological records let us store times + prefix sums and answer range
    score queries with binary search.

    Algorithm:
    - times[i], pref[i+1] = sum of first i+1 scores.
    - totalScore: bisect start/end, return pref difference (0 if empty).

    Complexity: O(1) record amortized; O(log n) per query; O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize empty exam history.

        Algorithm:
        - Empty times list and prefix sum starting at 0.

        Complexity: O(1) time.
        """
        self.times: List[int] = []
        self.pref: List[int] = [0]

    def record(self, time: int, score: int) -> None:
        """
        Interview explanation:
        Append a new exam at strictly increasing time.

        Algorithm:
        - Push time; extend prefix sum by score.

        Complexity: O(1) amortized time.
        """
        self.times.append(time)
        self.pref.append(self.pref[-1] + score)

    def totalScore(self, startTime: int, endTime: int) -> int:
        """
        Interview explanation:
        Sum scores with times in [startTime, endTime].

        Algorithm:
        - l = first index with time >= startTime; r = last with time <= endTime.
        - Return pref[r+1] - pref[l] (or 0 if l > r).

        Complexity: O(log n) time.
        """
        l = bisect.bisect_left(self.times, startTime)
        r = bisect.bisect_right(self.times, endTime) - 1
        if l > r:
            return 0
        return self.pref[r + 1] - self.pref[l]


# Your ExamTracker object will be instantiated and called as such:
# obj = ExamTracker()
# obj.record(time,score)
# param_2 = obj.totalScore(startTime,endTime)
# @lc code=end
