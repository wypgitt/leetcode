#
# @lc app=leetcode id=355 lang=python3
#
# [355] Design Twitter
#
# https://leetcode.com/problems/design-twitter/description/
#
# algorithms
# Medium (45.29%)
# Likes:    4787
# Dislikes: 670
# Total Accepted:    369K
# Total Submissions: 815K
# Testcase Example:  "[\"Twitter\",\"postTweet\",\"getNewsFeed\",\"follow\",\"postTweet\",\"getNewsFeed\",\"unfollow\",\"getNewsFeed\"]"
#
# Design a simplified version of Twitter where users can post tweets,
# follow/unfollow another user, and is able to see the 10 most recent tweets in
# the user's news feed.
#
# Implement the Twitter class:
#
# Twitter() Initializes your twitter object.
#
# void postTweet(int userId, int tweetId) Composes a new tweet with ID tweetId
# by the user userId. Each call to this function will be made with a unique
# tweetId.
#
# List<Integer> getNewsFeed(int userId) Retrieves the 10 most recent tweet IDs
# in the user's news feed. Each item in the news feed must be posted by users
# who the user followed or by the user themself. Tweets must be ordered from
# most recent to least recent.
#
# void follow(int followerId, int followeeId) The user with ID followerId
# started following the user with ID followeeId.
#
# void unfollow(int followerId, int followeeId) The user with ID followerId
# started unfollowing the user with ID followeeId.
#
# Example 1:
#
# Input
# ["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed",
# "unfollow", "getNewsFeed"]
# [[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]]
# Output
# [null, null, [5], null, null, [6, 5], null, [5]]
#
# Explanation
# Twitter twitter = new Twitter();
# twitter.postTweet(1, 5); // User 1 posts a new tweet (id = 5).
# twitter.getNewsFeed(1); // User 1's news feed should return a list with 1
# tweet id -> [5]. return [5]
# twitter.follow(1, 2); // User 1 follows user 2.
# twitter.postTweet(2, 6); // User 2 posts a new tweet (id = 6).
# twitter.getNewsFeed(1); // User 1's news feed should return a list with 2
# tweet ids -> [6, 5]. Tweet id 6 should precede tweet id 5 because it is
# posted after tweet id 5.
# twitter.unfollow(1, 2); // User 1 unfollows user 2.
# twitter.getNewsFeed(1); // User 1's news feed should return a list with 1
# tweet id -> [5], since user 1 is no longer following user 2.
#
# Constraints:
#
# 1 <= userId, followerId, followeeId <= 500
#
# 0 <= tweetId <= 10^4
#
# All the tweets have unique IDs.
#
# At most 3 * 10^4 calls will be made to postTweet, getNewsFeed, follow, and
# unfollow.
#
# A user cannot follow himself.
#

# @lc code=start
import heapq
from collections import defaultdict
from typing import Dict, List, Set


class Twitter:
    """
    Interview explanation:
    Each user stores tweets as (time, tweetId) newest-first lists and a follow
    set. getNewsFeed merges up to 10 tweets from self+followees with a max-heap
    (negate time) — like merge k sorted lists.

    Algorithm:
    - postTweet: append (-time, tweetId, userId) to user; global clock++.
    - follow/unfollow: manage followees set (never follow self).
    - getNewsFeed: heap of latest tweet pointer per user; pop 10.

    Complexity: post/follow O(1); feed O(F log F) for F followees; space O(total tweets).
    """

    def __init__(self):
        """
        Interview explanation:
        Per-user tweet lists (chronological) and followee sets, plus a global
        clock for recency ordering in the feed merge.

        Algorithm:
        - time=0; tweets[user]=list of (time, tweetId); followees[user]=set.

        Complexity: O(1) init, O(tweets + follows) space overall.
        """
        self.time = 0
        self.tweets: Dict[int, List[tuple]] = defaultdict(list)
        self.followees: Dict[int, Set[int]] = defaultdict(set)

    def postTweet(self, userId: int, tweetId: int) -> None:
        """
        Interview explanation:
        Append a timestamped tweet for the user and advance the global clock.

        Algorithm:
        - tweets[userId].append((time, tweetId)); time += 1.

        Complexity: O(1) time, O(1) amortized space.
        """
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        """
        Interview explanation:
        Merge up to 10 newest tweets from the user and followees with a max-heap
        (k-way merge of reverse-chronological lists).

        Algorithm:
        - Seed heap with each user's latest tweet; pop 10 times, pushing prior tweet.

        Complexity: O(F + 10 log F) for F followees with tweets, O(F) space.
        """
        users = self.followees[userId] | {userId}
        heap: List[tuple] = []
        for uid in users:
            if self.tweets[uid]:
                t, tid = self.tweets[uid][-1]
                heap.append((-t, tid, uid, len(self.tweets[uid]) - 1))
        heapq.heapify(heap)
        feed: List[int] = []
        while heap and len(feed) < 10:
            neg_t, tid, uid, idx = heapq.heappop(heap)
            feed.append(tid)
            if idx > 0:
                t2, tid2 = self.tweets[uid][idx - 1]
                heapq.heappush(heap, (-t2, tid2, uid, idx - 1))
        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        """
        Interview explanation:
        Add followee to follower's set; ignore self-follows.

        Algorithm:
        - If ids differ: followees[followerId].add(followeeId).

        Complexity: O(1) time, O(1) space.
        """
        if followerId != followeeId:
            self.followees[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        """
        Interview explanation:
        Remove followee from follower's set if present (discard is safe).

        Algorithm:
        - followees[followerId].discard(followeeId).

        Complexity: O(1) time, O(1) space.
        """
        self.followees[followerId].discard(followeeId)


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)
# @lc code=end
