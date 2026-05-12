#
# @lc app=leetcode id=1311 lang=python3
#
# [1311] Get Watched Videos by Your Friends
#
# https://leetcode.com/problems/get-watched-videos-by-your-friends/description/
#
# algorithms
# Medium (52.87%)
# Likes:    486
# Dislikes: 456
# Total Accepted:    42.4K
# Total Submissions: 80.1K
# Testcase Example:  '[["A","B"],["C"],["B","C"],["D"]]\n[[1,2],[0,3],[0,3],[1,2]]\n0\n1'
#
# There are n people, each person has a unique id between 0 and n-1. Given the
# arrays watchedVideos and friends, where watchedVideos[i] and friends[i]
# contain the list of watched videos and the list of friends respectively for
# the person with id = i.
# 
# Level 1 of videos are all watched videos by your friends, level 2 of videos
# are all watched videos by the friends of your friends and so on. In general,
# the level k of videos are all watched videos by people with the shortest path
# exactly equal to k with you. Given your id and the level of videos, return
# the list of videos ordered by their frequencies (increasing). For videos with
# the same frequency order them alphabetically from least to greatest. 
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: watchedVideos = [["A","B"],["C"],["B","C"],["D"]], friends =
# [[1,2],[0,3],[0,3],[1,2]], id = 0, level = 1
# Output: ["B","C"] 
# Explanation: 
# You have id = 0 (green color in the figure) and your friends are (yellow
# color in the figure):
# Person with id = 1 -> watchedVideos = ["C"] 
# Person with id = 2 -> watchedVideos = ["B","C"] 
# The frequencies of watchedVideos by your friends are: 
# B -> 1 
# C -> 2
# 
# 
# Example 2:
# 
# 
# 
# 
# Input: watchedVideos = [["A","B"],["C"],["B","C"],["D"]], friends =
# [[1,2],[0,3],[0,3],[1,2]], id = 0, level = 2
# Output: ["D"]
# Explanation: 
# You have id = 0 (green color in the figure) and the only friend of your
# friends is the person with id = 3 (yellow color in the figure).
# 
# 
# 
# Constraints:
# 
# 
# n == watchedVideos.length == friends.length
# 2 <= n <= 100
# 1 <= watchedVideos[i].length <= 100
# 1 <= watchedVideos[i][j].length <= 8
# 0 <= friends[i].length < n
# 0 <= friends[i][j] < n
# 0 <= id < n
# 1 <= level < n
# if friends[i] contains j, then friends[j] contains i
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import Counter, deque
from typing import List


class Solution:
    def watchedVideosByFriends(self, watchedVideos: List[List[str]], friends: List[List[int]], id: int, level: int) -> List[str]:
        visited = {id}
        queue = deque([id])

        for _ in range(level):
            for _ in range(len(queue)):
                person = queue.popleft()
                for friend in friends[person]:
                    if friend not in visited:
                        visited.add(friend)
                        queue.append(friend)

        counts = Counter()
        for person in queue:
            counts.update(watchedVideos[person])

        return sorted(counts, key=lambda video: (counts[video], video))
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Friend relationships form an unweighted graph. "Friends at exactly `level`"
# means all nodes whose shortest distance from `id` is exactly `level`, so BFS
# is the right traversal.
#
# Data structures:
# - `deque` for BFS by levels.
# - `visited` to avoid revisiting people and accidentally including closer
#   friends again.
# - `Counter` to count video frequencies among the target level.
#
# Walkthrough:
# 1. Start BFS at `id`.
# 2. Expand the queue exactly `level` times. After that loop, the queue contains
#    the people at the requested distance.
# 3. Count every video watched by those people.
# 4. Sort video names first by frequency, then lexicographically.
#
# Edge cases:
# - `level == 0`: the queue remains `[id]`, so only the person's own videos are
#   counted.
# - Multiple friends watched the same video: Counter aggregates frequency.
# - Graph cycles: `visited` prevents infinite traversal.
#
# Complexity:
# - Time: O(n + e + v log v), where v is the number of distinct videos counted.
# - Space: O(n + v), for BFS state and counts.
