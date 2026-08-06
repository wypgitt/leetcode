#
# @lc app=leetcode id=2107 lang=python3
#
# [2107] Number of Unique Flavors After Sharing K Candies
#
# https://leetcode.com/problems/number-of-unique-flavors-after-sharing-k-candies/description/
#
# algorithms
# Medium (62.33%)
# Likes:    124
# Dislikes: 7
# Total Accepted:    12.2K
# Total Submissions: 19.6K
# Testcase Example:  "[1,2,2,3,4,3]\n3"
#
#
# You are given a 0-indexed integer array candies, where candies[i]
# represents the flavor of the i^th candy. Your mom wants you to share
# these candies with your little sister by giving her k consecutive
# candies, but you want to keep as many flavors of candies as possible.
#
# Return the maximum number of unique flavors of candy you can keep after
# sharing  with your sister.
#
# Example 1:
#
# Input: candies = [1,2,2,3,4,3], k = 3
# Output: 3
# Explanation:
# Give the candies in the range [1, 3] (inclusive) with flavors [2,2,3].
# You can eat candies with flavors [1,4,3].
# There are 3 unique flavors, so return 3.
#
# Example 2:
#
# Input: candies = [2,2,2,2,3,3], k = 2
# Output: 2
# Explanation:
# Give the candies in the range [3, 4] (inclusive) with flavors [2,3].
# You can eat candies with flavors [2,2,2,3].
# There are 2 unique flavors, so return 2.
# Note that you can also share the candies with flavors [2,2] and eat the
# candies with flavors [2,2,3,3].
#
# Example 3:
#
# Input: candies = [2,4,5], k = 0
# Output: 3
# Explanation:
# You do not have to give any candies.
# You can eat the candies with flavors [2,4,5].
# There are 3 unique flavors, so return 3.
#
# Constraints:
#
# 0 <= candies.length <= 10^5
#
# 1 <= candies[i] <= 10^5
#
# 0 <= k <= candies.length
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def shareCandies(self, candies: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium: give sister k consecutive candies; maximize unique flavors you keep.

        Algorithm:
        - Count flavors outside a window of size k; slide window; track max
          number of positive-count flavors outside.

        Complexity: O(n) time, O(n) space.
        """
        n = len(candies)
        if k == 0:
            return len(set(candies))
        cnt = Counter(candies[k:])
        ans = len(cnt)
        for i in range(k, n):
            cnt[candies[i - k]] += 1
            cnt[candies[i]] -= 1
            if cnt[candies[i]] == 0:
                del cnt[candies[i]]
            ans = max(ans, len(cnt))
        return ans
# @lc code=end

