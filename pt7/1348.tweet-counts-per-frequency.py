#
# @lc app=leetcode id=1348 lang=python3
#
# [1348] Tweet Counts Per Frequency
#
# https://leetcode.com/problems/tweet-counts-per-frequency/description/
#
# algorithms
# Medium (46.08%)
# Likes:    223
# Dislikes: 309
# Total Accepted:    39.9K
# Total Submissions: 86.6K
# Testcase Example:  '["TweetCounts","recordTweet","recordTweet","recordTweet","getTweetCountsPerFrequency","getTweetCountsPerFrequency","recordTweet","getTweetCountsPerFrequency"]\n' +
# '[[],["tweet3",0],["tweet3",60],["tweet3",10],["minute","tweet3",0,59],["minute","tweet3",0,60],["tweet3",120],["hour","tweet3",0,210]]'
#
# A social media company is trying to monitor activity on their site by
# analyzing the number of tweets that occur in select periods of time. These
# periods can be partitioned into smaller time chunks based on a certain
# frequency (every minute, hour, or day).
# 
# For example, the period [10, 10000] (in seconds) would be partitioned into
# the following time chunks with these frequencies:
# 
# 
# Every minute (60-second chunks): [10,69], [70,129], [130,189], ...,
# [9970,10000]
# Every hour (3600-second chunks): [10,3609], [3610,7209], [7210,10000]
# Every day (86400-second chunks): [10,10000]
# 
# 
# Notice that the last chunk may be shorter than the specified frequency's
# chunk size and will always end with the end time of the period (10000 in the
# above example).
# 
# Design and implement an API to help the company with their analysis.
# 
# Implement the TweetCounts class:
# 
# 
# TweetCounts() Initializes the TweetCounts object.
# void recordTweet(String tweetName, int time) Stores the tweetName at the
# recorded time (in seconds).
# List<Integer> getTweetCountsPerFrequency(String freq, String tweetName, int
# startTime, int endTime) Returns a list of integers representing the number of
# tweets with tweetName in each time chunk for the given period of time
# [startTime, endTime] (in seconds) and frequency freq.
# 
# freq is one of "minute", "hour", or "day" representing a frequency of every
# minute, hour, or day respectively.
# 
# 
# 
# 
# 
# Example:
# 
# 
# Input
# 
# ["TweetCounts","recordTweet","recordTweet","recordTweet","getTweetCountsPerFrequency","getTweetCountsPerFrequency","recordTweet","getTweetCountsPerFrequency"]
# 
# [[],["tweet3",0],["tweet3",60],["tweet3",10],["minute","tweet3",0,59],["minute","tweet3",0,60],["tweet3",120],["hour","tweet3",0,210]]
# 
# Output
# [null,null,null,null,[2],[2,1],null,[4]]
# 
# Explanation
# TweetCounts tweetCounts = new TweetCounts();
# tweetCounts.recordTweet("tweet3", 0);                              // New
# tweet "tweet3" at time 0
# tweetCounts.recordTweet("tweet3", 60);                             // New
# tweet "tweet3" at time 60
# tweetCounts.recordTweet("tweet3", 10);                             // New
# tweet "tweet3" at time 10
# tweetCounts.getTweetCountsPerFrequency("minute", "tweet3", 0, 59); // return
# [2]; chunk [0,59] had 2 tweets
# tweetCounts.getTweetCountsPerFrequency("minute", "tweet3", 0, 60); // return
# [2,1]; chunk [0,59] had 2 tweets, chunk [60,60] had 1 tweet
# tweetCounts.recordTweet("tweet3", 120);                            // New
# tweet "tweet3" at time 120
# tweetCounts.getTweetCountsPerFrequency("hour", "tweet3", 0, 210);  // return
# [4]; chunk [0,210] had 4 tweets
# 
# 
# 
# Constraints:
# 
# 
# 0 <= time, startTime, endTime <= 10^9
# 0 <= endTime - startTime <= 10^4
# There will be at most 10^4 calls in total to recordTweet and
# getTweetCountsPerFrequency.
# 
# 
#

# @lc code=start
from __future__ import annotations

from bisect import bisect_left, bisect_right, insort
from collections import defaultdict
from typing import DefaultDict, List


class TweetCounts:

    def __init__(self):
        self.tweets: DefaultDict[str, List[int]] = defaultdict(list)

    def recordTweet(self, tweetName: str, time: int) -> None:
        insort(self.tweets[tweetName], time)

    def getTweetCountsPerFrequency(self, freq: str, tweetName: str, startTime: int, endTime: int) -> List[int]:
        interval = {"minute": 60, "hour": 3600, "day": 86400}[freq]
        times = self.tweets[tweetName]
        counts = []

        bucket_start = startTime
        while bucket_start <= endTime:
            bucket_end = min(bucket_start + interval - 1, endTime)
            left = bisect_left(times, bucket_start)
            right = bisect_right(times, bucket_end)
            counts.append(right - left)
            bucket_start += interval

        return counts


# Your TweetCounts object will be instantiated and called as such:
# obj = TweetCounts()
# obj.recordTweet(tweetName,time)
# param_2 = obj.getTweetCountsPerFrequency(freq,tweetName,startTime,endTime)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# For each tweet name, keep its recorded times sorted. A query splits the time
# interval into fixed-size buckets and counts how many sorted times fall inside
# each bucket.
#
# Data structures:
# - `defaultdict(list)` maps tweet name to sorted timestamps.
# - `insort` inserts while preserving order.
# - `bisect_left` and `bisect_right` find the range of timestamps in a bucket.
#
# Walkthrough:
# 1. `recordTweet` inserts the timestamp into that tweet's sorted list.
# 2. Convert frequency to seconds: minute, hour, or day.
# 3. For each bucket `[bucket_start, bucket_end]`, binary search the first time
#    >= start and the first time > end.
# 4. Their index difference is the number of tweets in the bucket.
#
# Edge cases:
# - Last bucket may be shorter than the frequency, so clamp to `endTime`.
# - No tweets for a name: the sorted list is empty and all counts are 0.
# - Tweets exactly at bucket boundaries: left/right bisects include both ends.
#
# Complexity:
# - `recordTweet`: O(m) for insertion into a list of m timestamps.
# - `getTweetCountsPerFrequency`: O(b log m), where b is the number of buckets.
# - Space: O(total records).
#
# Improvement:
# If records were much larger, a balanced tree per tweet would make insertion
# O(log m). For LeetCode's call limits, sorted lists are simple and accepted.
