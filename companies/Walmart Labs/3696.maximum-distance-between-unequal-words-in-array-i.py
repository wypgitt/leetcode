#
# @lc app=leetcode id=3696 lang=python3
#
# [3696] Maximum Distance Between Unequal Words in Array I
#
# https://leetcode.com/problems/maximum-distance-between-unequal-words-in-array-i/description/
#
# algorithms
# Easy (82.03%)
# Likes:    6
# Dislikes: 1
# Total Accepted:    1.3K
# Total Submissions: 1.5K
# Testcase Example:  "[\"leetcode\",\"leetcode\",\"codeforces\"]"
#
#
# You are given a string array words.
#
# Find the maximum distance between two distinct indices i and j such
# that:
#
# words[i] != words[j], and
#
# the distance is defined as j - i + 1.
#
# Return the maximum distance among all such pairs. If no valid pair
# exists, return 0.
#
# Example 1:
#
# Input: words = ["leetcode","leetcode","codeforces"]
#
# Output: 3
#
# Explanation:
#
# In this example, words[0] and words[2] are not equal, and they have the
# maximum distance 2 - 0 + 1 = 3.
#
# Example 2:
#
# Input: words = ["a","b","c","a","a"]
#
# Output: 4
#
# Explanation:
#
# In this example words[1] and words[4] have the largest distance of 4 - 1
# + 1 = 4.
#
# Example 3:
#
# Input: words = ["z","z","z"]
#
# Output: 0
#
# Explanation:
#
# In this example all the words are equal, thus the answer is 0.
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 10
#
# words[i] consists of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def maxDistance(self, words: List[str]) -> int:
        """
        Interview explanation:
        Maximum j - i + 1 with words[i] != words[j] is achieved with an
        endpoint at 0 or n-1 (shrinking the other side cannot help).

        Algorithm:
        - If ends differ, answer is n.
        - Else max distance from index 0 to farthest unequal, and from n-1 to
          nearest unequal; return that max (0 if none).

        Complexity: O(n) time, O(1) space.
        """
        n = len(words)
        if words[0] != words[-1]:
            return n
        ans = 0
        for j in range(n - 1, -1, -1):
            if words[j] != words[0]:
                ans = max(ans, j + 1)
                break
        for i in range(n):
            if words[i] != words[-1]:
                ans = max(ans, n - i)
                break
        return ans
# @lc code=end
