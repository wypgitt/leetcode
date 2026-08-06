#
# @lc app=leetcode id=3433 lang=python3
#
# [3433] Count Mentions Per User
#
# https://leetcode.com/problems/count-mentions-per-user/description/
#
# algorithms
# Medium (50.79%)
# Likes:    397
# Dislikes: 251
# Total Accepted:    86.8K
# Total Submissions: 170.8K
# Testcase Example:  "2\n[[\"MESSAGE\",\"10\",\"id1 id0\"],[\"OFFLINE\",\"11\",\"0\"],[\"MESSAGE\",\"71\",\"HERE\"]]"
#
#
# You are given an integer numberOfUsers representing the total number of
# users and an array events of size n x 3.
#
# Each events[i] can be either of the following two types:
#
# Message Event: ["MESSAGE", "timestamp_i", "mentions_string_i"]
#
# This event indicates that a set of users was mentioned in a message at
# timestamp_i.
#
# The mentions_string_i string can contain one of the following tokens:
#
# id<number>: where <number> is an integer in range [0,numberOfUsers - 1].
# There can be multiple ids separated by a single whitespace and may
# contain duplicates. This can mention even the offline users.
#
# ALL: mentions all users.
#
# HERE: mentions all online users.
#
# Offline Event: ["OFFLINE", "timestamp_i", "id_i"]
#
# This event indicates that the user id_i had become offline at
# timestamp_i for 60 time units. The user will automatically be online
# again at time timestamp_i + 60.
#
# Return an array mentions where mentions[i] represents the number of
# mentions the user with id i has across all MESSAGE events.
#
# All users are initially online, and if a user goes offline or comes back
# online, their status change is processed before handling any message
# event that occurs at the same timestamp.
#
# Note that a user can be mentioned multiple times in a single message
# event, and each mention should be counted separately.
#
# Example 1:
#
# Input: numberOfUsers = 2, events = [["MESSAGE","10","id1
# id0"],["OFFLINE","11","0"],["MESSAGE","71","HERE"]]
#
# Output: [2,2]
#
# Explanation:
#
# Initially, all users are online.
#
# At timestamp 10, id1 and id0 are mentioned. mentions = [1,1]
#
# At timestamp 11, id0 goes offline.
#
# At timestamp 71, id0 comes back online and "HERE" is mentioned. mentions
# = [2,2]
#
# Example 2:
#
# Input: numberOfUsers = 2, events = [["MESSAGE","10","id1
# id0"],["OFFLINE","11","0"],["MESSAGE","12","ALL"]]
#
# Output: [2,2]
#
# Explanation:
#
# Initially, all users are online.
#
# At timestamp 10, id1 and id0 are mentioned. mentions = [1,1]
#
# At timestamp 11, id0 goes offline.
#
# At timestamp 12, "ALL" is mentioned. This includes offline users, so
# both id0 and id1 are mentioned. mentions = [2,2]
#
# Example 3:
#
# Input: numberOfUsers = 2, events =
# [["OFFLINE","10","0"],["MESSAGE","12","HERE"]]
#
# Output: [0,1]
#
# Explanation:
#
# Initially, all users are online.
#
# At timestamp 10, id0 goes offline.
#
# At timestamp 12, "HERE" is mentioned. Because id0 is still offline, they
# will not be mentioned. mentions = [0,1]
#
# Constraints:
#
# 1 <= numberOfUsers <= 100
#
# 1 <= events.length <= 100
#
# events[i].length == 3
#
# events[i][0] will be one of MESSAGE or OFFLINE.
#
# 1 <= int(events[i][1]) <= 10^5
#
# The number of id<number> mentions in any "MESSAGE" event is between 1
# and 100.
#
# 0 <= <number> <= numberOfUsers - 1
#
# It is guaranteed that the user id referenced in the OFFLINE event is
# online at the time the event occurs.
#

# @lc code=start
from typing import List


class Solution:
    def countMentions(self, numberOfUsers: int, events: List[List[str]]) -> List[int]:
        """
        Interview explanation:
        Process events in time order; at equal timestamps handle OFFLINE before
        MESSAGE. Track each user's next-online time; ALL mentions apply to everyone
        (lazy), HERE only to currently online users, id* always.

        Algorithm:
        - Sort by (timestamp, MESSAGE after OFFLINE).
        - OFFLINE: online_t[id] = t+60.
        - ALL: lazy++; HERE: +1 for users with online_t <= t; else parse ids.
        - Finally add lazy to every user.

        Complexity: O(E log E + E * U) time, O(U) space.
        """
        events = sorted(events, key=lambda e: (int(e[1]), e[0] == "MESSAGE"))
        ans = [0] * numberOfUsers
        online_t = [0] * numberOfUsers
        lazy = 0
        for etype, ts, s in events:
            cur = int(ts)
            if etype == "OFFLINE":
                online_t[int(s)] = cur + 60
            elif s == "ALL":
                lazy += 1
            elif s == "HERE":
                for i, t in enumerate(online_t):
                    if t <= cur:
                        ans[i] += 1
            else:
                for token in s.split():
                    ans[int(token[2:])] += 1
        return [c + lazy for c in ans]
# @lc code=end
