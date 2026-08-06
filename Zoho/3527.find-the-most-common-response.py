#
# @lc app=leetcode id=3527 lang=python3
#
# [3527] Find the Most Common Response
#
# https://leetcode.com/problems/find-the-most-common-response/description/
#
# algorithms
# Medium (74.99%)
# Likes:    66
# Dislikes: 7
# Total Accepted:    39.8K
# Total Submissions: 53K
# Testcase Example:  "[[\"good\",\"ok\",\"good\",\"ok\"],[\"ok\",\"bad\",\"good\",\"ok\",\"ok\"],[\"good\"],[\"bad\"]]"
#
#
# You are given a 2D string array responses where each responses[i] is an
# array of strings representing survey responses from the i^th day.
#
# Return the most common response across all days after removing duplicate
# responses within each responses[i]. If there is a tie, return the
# lexicographically smallest response.
#
# Example 1:
#
# Input: responses =
# [["good","ok","good","ok"],["ok","bad","good","ok","ok"],["good"],["bad"]]
#
# Output: "good"
#
# Explanation:
#
# After removing duplicates within each list, responses = [["good", "ok"],
# ["ok", "bad", "good"], ["good"], ["bad"]].
#
# "good" appears 3 times, "ok" appears 2 times, and "bad" appears 2 times.
#
# Return "good" because it has the highest frequency.
#
# Example 2:
#
# Input: responses =
# [["good","ok","good"],["ok","bad"],["bad","notsure"],["great","good"]]
#
# Output: "bad"
#
# Explanation:
#
# After removing duplicates within each list we have responses = [["good",
# "ok"], ["ok", "bad"], ["bad", "notsure"], ["great", "good"]].
#
# "bad", "good", and "ok" each occur 2 times.
#
# The output is "bad" because it is the lexicographically smallest amongst
# the words with the highest frequency.
#
# Constraints:
#
# 1 <= responses.length <= 1000
#
# 1 <= responses[i].length <= 1000
#
# 1 <= responses[i][j].length <= 10
#
# responses[i][j] consists of only lowercase English letters
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def findCommonResponse(self, responses: List[List[str]]) -> str:
        """
        Interview explanation:
        Deduplicate each day's responses, then pick the globally most frequent
        string; break ties lexicographically.

        Algorithm:
        - For each day, add unique strings into a Counter.
        - Return min((-count, word)) style: max count, then min word.

        Complexity: O(total responses * L) time, O(U) space for unique words.
        """
        cnt: Counter = Counter()
        for day in responses:
            for w in set(day):
                cnt[w] += 1
        best = None
        for w, c in cnt.items():
            if best is None or c > best[0] or (c == best[0] and w < best[1]):
                best = (c, w)
        return best[1]
# @lc code=end
