#
# @lc app=leetcode id=3839 lang=python3
#
# [3839] Number of Prefix Connected Groups
#
# https://leetcode.com/problems/number-of-prefix-connected-groups/description/
#
# algorithms
# Medium (60.74%)
# Likes:    53
# Dislikes: 4
# Total Accepted:    40.3K
# Total Submissions: 66.3K
# Testcase Example:  "[\"apple\",\"apply\",\"banana\",\"bandit\"]\n2"
#
#
# You are given an array of strings words and an integer k.
#
# Two words a and b at distinct indices are prefix-connected if a[0..k-1]
# == b[0..k-1].
#
# A connected group is a set of words such that each pair of words is
# prefix-connected.
#
# Return the number of connected groups that contain at least two words,
# formed from the given words.
#
# Note:
#
# Words with length less than k cannot join any group and are ignored.
#
# Duplicate strings are treated as separate words.
#
# Example 1:
#
# Input: words = ["apple","apply","banana","bandit"], k = 2
#
# Output: 2
#
# Explanation:
#
# Words sharing the same first k = 2 letters are grouped together:
#
# words[0] = "apple" and words[1] = "apply" share prefix "ap".
#
# words[2] = "banana" and words[3] = "bandit" share prefix "ba".
#
# Thus, there are 2 connected groups, each containing at least two words.
#
# Example 2:
#
# Input: words = ["car","cat","cartoon"], k = 3
#
# Output: 1
#
# Explanation:
#
# Words are evaluated for a prefix of length k = 3:
#
# words[0] = "car" and words[2] = "cartoon" share prefix "car".
#
# words[1] = "cat" does not share a 3-length prefix with any other word.
#
# Thus, there is 1 connected group.
#
# Example 3:
#
# Input: words = ["bat","dog","dog","doggy","bat"], k = 3
#
# Output: 2
#
# Explanation:
#
# Words are evaluated for a prefix of length k = 3:
#
# words[0] = "bat" and words[4] = "bat" form a group.
#
# words[1] = "dog", words[2] = "dog" and words[3] = "doggy" share prefix
# "dog".
#
# Thus, there are 2 connected groups, each containing at least two words.
#
# Constraints:
#
# 1 <= words.length <= 5000
#
# 1 <= words[i].length <= 100
#
# 1 <= k <= 100
#
# All strings in words consist of lowercase English letters.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def prefixConnected(self, words: List[str], k: int) -> int:
        """
        Interview explanation:
        Words of length >= k that share the same length-k prefix form one
        connected group. Count prefixes that appear at least twice.

        Algorithm:
        - Count first-k prefixes among eligible words.
        - Sum 1 for each prefix with frequency >= 2.

        Complexity: O(n * k) time, O(n * k) space.
        """
        cnt = Counter(w[:k] for w in words if len(w) >= k)
        return sum(1 for v in cnt.values() if v >= 2)
# @lc code=end
