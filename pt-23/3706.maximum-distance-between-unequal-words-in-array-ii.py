#
# @lc app=leetcode id=3706 lang=python3
#
# [3706] Maximum Distance Between Unequal Words in Array II
#
# https://leetcode.com/problems/maximum-distance-between-unequal-words-in-array-ii/description/
#
# algorithms
# Medium (72.49%)
# Likes:    5
# Dislikes: 2
# Total Accepted:    693
# Total Submissions: 956
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
# ​​​​​​​In this example all the words are equal, thus the answer is 0.
#
# Constraints:
#
# 1 <= words.length <= 10^5
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
        The farthest unequal pair always involves an endpoint: either words[0]
        or words[n-1]. Scan once for the best distance to a different word.

        Algorithm:
        - For each i, if words[i] != words[0], update with i + 1.
        - If words[i] != words[n-1], update with n - i.
        - Return the max (0 if all equal).

        Complexity: O(n) time, O(1) space.
        """
        n = len(words)
        ans = 0
        for i, w in enumerate(words):
            if w != words[0]:
                ans = max(ans, i + 1)
            if w != words[n - 1]:
                ans = max(ans, n - i)
        return ans

    def maxDistance_endpoints(self, words: List[str]) -> int:
        """
        Interview explanation:
        Alternate: walk from both ends until a mismatch with the opposite end.

        Algorithm:
        - Scan left-to-right for first != words[-1]; right-to-left for != words[0].

        Complexity: O(n) time, O(1) space.
        """
        n = len(words)
        ans = 0
        for i in range(n):
            if words[i] != words[-1]:
                ans = max(ans, n - i)
                break
        for i in range(n - 1, -1, -1):
            if words[i] != words[0]:
                ans = max(ans, i + 1)
                break
        return ans
# @lc code=end
