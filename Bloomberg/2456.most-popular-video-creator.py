#
# @lc app=leetcode id=2456 lang=python3
#
# [2456] Most Popular Video Creator
#
# https://leetcode.com/problems/most-popular-video-creator/description/
#
# algorithms
# Medium (45.47%)
# Likes:    314
# Dislikes: 386
# Total Accepted:    29.2K
# Total Submissions: 64.2K
# Testcase Example:  "[\"alice\",\"bob\",\"alice\",\"chris\"]\n[\"one\",\"two\",\"three\",\"four\"]\n[5,10,5,4]"
#
# You are given two string arrays creators and ids, and an integer array views,
# all of length n. The i^th video on a platform was created by creators[i], has
# an id of ids[i], and has views[i] views.
#
# The popularity of a creator is the sum of the number of views on all of the
# creator's videos. Find the creator with the highest popularity and the id of
# their most viewed video.
#
#
# If multiple creators have the highest popularity, find all of them.
#
#
# If multiple videos have the highest view count for a creator, find the
# lexicographically smallest id.
#
# Note: It is possible for different videos to have the same id, meaning that
# ids do not uniquely identify a video. For example, two videos with the same ID
# are considered as distinct videos with their own viewcount.
#
# Return a 2D array of strings answer where answer[i] = [creators_i, id_i] means
# that creators_i has the highest popularity and id_i is the id of their most
# popular video. The answer can be returned in any order.
#
#
#
# Example 1:
#
# Input: creators = ["alice","bob","alice","chris"], ids =
# ["one","two","three","four"], views = [5,10,5,4]
#
# Output: [["alice","one"],["bob","two"]]
#
# Explanation:
#
# The popularity of alice is 5 + 5 = 10.
#
# The popularity of bob is 10.
#
# The popularity of chris is 4.
#
# alice and bob are the most popular creators.
#
# For bob, the video with the highest view count is "two".
#
# For alice, the videos with the highest view count are "one" and "three". Since
# "one" is lexicographically smaller than "three", it is included in the answer.
#
# Example 2:
#
# Input: creators = ["alice","alice","alice"], ids = ["a","b","c"], views =
# [1,2,2]
#
# Output: [["alice","b"]]
#
# Explanation:
#
# The videos with id "b" and "c" have the highest view count.
#
# Since "b" is lexicographically smaller than "c", it is included in the answer.
#
#
#
# Constraints:
#
#
# n == creators.length == ids.length == views.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= creators[i].length, ids[i].length <= 5
#
#
# creators[i] and ids[i] consist only of lowercase English letters.
#
#
# 0 <= views[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def mostPopularCreator(
        self, creators: List[str], ids: List[str], views: List[int]
    ) -> List[List[str]]:
        """
        Interview explanation:
        Popularity = sum of views per creator. Return each most popular creator
        with their highest-view video id (lex-smallest on ties).

        Algorithm:
        - Aggregate total views and best (views, -id) per creator; pick max total.

        Complexity: O(n) time, O(n) space.
        """
        total = defaultdict(int)
        best = {}
        for c, i, v in zip(creators, ids, views):
            total[c] += v
            if c not in best or v > best[c][0] or (v == best[c][0] and i < best[c][1]):
                best[c] = (v, i)
        mx = max(total.values())
        return [[c, best[c][1]] for c in total if total[c] == mx]
# @lc code=end

