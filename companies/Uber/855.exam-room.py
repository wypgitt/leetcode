#
# @lc app=leetcode id=855 lang=python3
#
# [855] Exam Room
#
# https://leetcode.com/problems/exam-room/description/
#
# algorithms
# Medium (43.69%)
# Likes:    1441
# Dislikes: 533
# Total Accepted:    77.7K
# Total Submissions: 178K
# Testcase Example:  "[\"ExamRoom\",\"seat\",\"seat\",\"seat\",\"seat\",\"leave\",\"seat\"]"
#
# There is an exam room with n seats in a single row labeled from 0 to n - 1.
#
# When a student enters the room, they must sit in the seat that maximizes the
# distance to the closest person. If there are multiple such seats, they sit in
# the seat with the lowest number. If no one is in the room, then the student
# sits at seat number 0.
#
# Design a class that simulates the mentioned exam room.
#
# Implement the ExamRoom class:
#
# ExamRoom(int n) Initializes the object of the exam room with the number of
# the seats n.
#
# int seat() Returns the label of the seat at which the next student will set.
#
# void leave(int p) Indicates that the student sitting at seat p will leave the
# room. It is guaranteed that there will be a student sitting at seat p.
#
# Example 1:
#
# Input
# ["ExamRoom", "seat", "seat", "seat", "seat", "leave", "seat"]
# [[10], [], [], [], [], [4], []]
# Output
# [null, 0, 9, 4, 2, null, 5]
#
# Explanation
# ExamRoom examRoom = new ExamRoom(10);
# examRoom.seat(); // return 0, no one is in the room, then the student sits at
# seat number 0.
# examRoom.seat(); // return 9, the student sits at the last seat number 9.
# examRoom.seat(); // return 4, the student sits at the last seat number 4.
# examRoom.seat(); // return 2, the student sits at the last seat number 2.
# examRoom.leave(4);
# examRoom.seat(); // return 5, the student sits at the last seat number 5.
#
# Constraints:
#
# 1 <= n <= 10^9
#
# It is guaranteed that there is a student sitting at seat p.
#
# At most 10^4 calls will be made to seat and leave.
#

# @lc code=start

import bisect


class ExamRoom:
    def __init__(self, n: int):
        """
        Interview explanation:
        Maintain sorted occupied seats. seat() picks the position maximizing
        distance to closest neighbor (edges use distance to end). leave removes.

        Algorithm:
        - seats sorted list; for seat scan gaps between consecutive occupied.

        Complexity: O(1) init; O(p) seat/leave with p occupied (≤10^4 calls).
        """
        self.n = n
        self.seats: list[int] = []

    def seat(self) -> int:
        """
        Interview explanation:
        If empty sit at 0. Else consider sitting at 0, at n-1, or midpoint of
        each gap between consecutive students; choose max min-distance, break
        ties by lowest index.

        Algorithm:
        - Scan gaps; track best (dist, -pos) then insert pos into sorted seats.

        Complexity: O(p) time.
        """
        if not self.seats:
            self.seats.append(0)
            return 0
        # candidate: seat 0
        best_pos = 0
        best_dist = self.seats[0] - 0
        for i in range(1, len(self.seats)):
            a, b = self.seats[i - 1], self.seats[i]
            d = (b - a) // 2
            if d > best_dist:
                best_dist = d
                best_pos = a + d
        # candidate: seat n-1
        d = self.n - 1 - self.seats[-1]
        if d > best_dist:
            best_pos = self.n - 1
        bisect.insort(self.seats, best_pos)
        return best_pos

    def leave(self, p: int) -> None:
        """
        Interview explanation:
        Student at p leaves; remove p from the sorted occupied list.

        Algorithm:
        - seats.remove(p).

        Complexity: O(p) time.
        """
        self.seats.remove(p)
# @lc code=end
