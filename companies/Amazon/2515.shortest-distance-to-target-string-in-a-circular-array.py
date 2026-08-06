#
# @lc app=leetcode id=2515 lang=python3
#
# [2515] Shortest Distance to Target String in a Circular Array
#
# https://leetcode.com/problems/shortest-distance-to-target-string-in-a-circular-array/description/
#
# algorithms
# Easy (65.25%)
# Likes:    634
# Dislikes: 37
# Total Accepted:    140.7K
# Total Submissions: 215.7K
# Testcase Example:  "[\"hello\",\"i\",\"am\",\"leetcode\",\"hello\"]\n\"hello\"\n1"
#
# You are given a 0-indexed circular string array words and a string target. A
# circular array means that the array's end connects to the array's beginning.
#
#
# Formally, the next element of words[i] is words[(i + 1) % n] and the previous
# element of words[i] is words[(i - 1 + n) % n], where n is the length of words.
#
# Starting from startIndex, you can move to either the next word or the previous
# word with 1 step at a time.
#
# Return the shortest distance needed to reach the string target. If the string
# target does not exist in words, return -1.
#
#
#
# Example 1:
#
# Input: words = ["hello","i","am","leetcode","hello"], target = "hello",
# startIndex = 1
# Output: 1
# Explanation: We start from index 1 and can reach "hello" by
# - moving 3 units to the right to reach index 4.
# - moving 2 units to the left to reach index 4.
# - moving 4 units to the right to reach index 0.
# - moving 1 unit to the left to reach index 0.
# The shortest distance to reach "hello" is 1.
#
# Example 2:
#
# Input: words = ["a","b","leetcode"], target = "leetcode", startIndex = 0
# Output: 1
# Explanation: We start from index 0 and can reach "leetcode" by
# - moving 2 units to the right to reach index 2.
# - moving 1 unit to the left to reach index 2.
# The shortest distance to reach "leetcode" is 1.
#
# Example 3:
#
# Input: words = ["i","eat","leetcode"], target = "ate", startIndex = 0
# Output: -1
# Explanation: Since "ate" does not exist in words, we return -1.
#
#
#
# Constraints:
#
#
# 1 <= words.length <= 100
#
#
# 1 <= words[i].length <= 100
#
#
# words[i] and target consist of only lowercase English letters.
#
#
# 0 <= startIndex < words.length
#

# @lc code=start
from typing import List


class Solution:
    def closestTarget(self, words: List[str], target: str, startIndex: int) -> int:
        """
        Interview explanation:
        In a circular word array, find shortest steps from startIndex to target.

        Algorithm:
        - For each match index i, take min(|i-start|, n-|i-start|); return min or -1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(words)
        ans = n
        for i, w in enumerate(words):
            if w == target:
                d = abs(i - startIndex)
                ans = min(ans, d, n - d)
        return -1 if ans == n else ans

    def closestTarget_two_pointers(self, words: List[str], target: str, startIndex: int) -> int:
        """
        Interview explanation:
        Walk outward left and right from start until a target is found.

        Algorithm:
        - For distance d = 0..n-1, check start±d (mod n); first hit is answer.

        Complexity: O(n) time, O(1) space.
        """
        n = len(words)
        for d in range(n):
            if words[(startIndex + d) % n] == target or words[(startIndex - d) % n] == target:
                return d
        return -1
# @lc code=end
