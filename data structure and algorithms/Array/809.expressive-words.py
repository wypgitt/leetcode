#
# @lc app=leetcode id=809 lang=python3
#
# [809] Expressive Words
#
# https://leetcode.com/problems/expressive-words/description/
#
# algorithms
# Medium (46.80%)
# Likes:    919
# Dislikes: 1951
# Total Accepted:    136.5K
# Total Submissions: 291.6K
# Testcase Example:  '"heeellooo"\n["hello", "hi", "helo"]'
#
# Sometimes people repeat letters to represent extra feeling. For
# example:
# 
# 
# "hello" -> "heeellooo"
# "hi" -> "hiiii"
# 
# 
# In these strings like "heeellooo", we have groups of adjacent letters that
# are all the same: "h", "eee", "ll", "ooo".
# 
# You are given a string s and an array of query strings words. A query word is
# stretchy if it can be made to be equal to s by any number of applications of
# the following extension operation: choose a group consisting of characters c,
# and add some number of characters c to the group so that the size of the
# group is three or more.
# 
# 
# For example, starting with "hello", we could do an extension on the group "o"
# to get "hellooo", but we cannot get "helloo" since the group "oo" has a size
# less than three. Also, we could do another extension like "ll" -> "lllll" to
# get "helllllooo". If s = "helllllooo", then the query word "hello" would be
# stretchy because of these two extension operations: query = "hello" ->
# "hellooo" -> "helllllooo" = s.
# 
# 
# Return the number of query strings that are stretchy.
# 
# 
# Example 1:
# 
# 
# Input: s = "heeellooo", words = ["hello", "hi", "helo"]
# Output: 1
# Explanation: 
# We can extend "e" and "o" in the word "hello" to get "heeellooo".
# We can't extend "helo" to get "heeellooo" because the group "ll" is not size
# 3 or more.
# 
# 
# Example 2:
# 
# 
# Input: s = "zzzzzyyyyy", words = ["zzyy","zy","zyy"]
# Output: 3
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length, words.length <= 100
# 1 <= words[i].length <= 100
# s and words[i] consist of lowercase letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def expressiveWords(self, s: str, words: List[str]) -> int:
        def groups(t: str):
            res = []
            i = 0
            while i < len(t):
                j = i + 1
                while j < len(t) and t[j] == t[i]:
                    j += 1
                res.append((t[i], j - i))
                i = j
            return res

        target = groups(s)
        ans = 0
        for word in words:
            g = groups(word)
            if len(g) != len(target):
                continue
            ok = True
            for (tc, tn), (wc, wn) in zip(target, g):
                if tc != wc or wn > tn or (tn < 3 and wn != tn):
                    ok = False
                    break
            ans += ok
        return ans
# @lc code=end

"""
Interview explanation:
Compress strings into character groups. A word can stretch to s if it has the same group characters, each word group is no longer than the target group, and any changed target group has length at least 3.

Data structure: run-length encoded lists make comparisons local per group.

Edge cases: target groups of length 1 or 2 cannot be stretched, so counts must match exactly. Extra or missing groups fail.

Complexity: grouping s is O(|s|), and grouping all words costs their total length. Space is O(number of groups) per string.
"""
