#
# @lc app=leetcode id=3728 lang=python3
#
# [3728] Stable Subarrays With Equal Boundary and Interior Sum
#
# https://leetcode.com/problems/stable-subarrays-with-equal-boundary-and-interior-sum/description/
#
# algorithms
# Medium (26.60%)
# Likes:    183
# Dislikes: 3
# Total Accepted:    16.9K
# Total Submissions: 63.4K
# Testcase Example:  "[9,3,3,3,9]"
#
#
# You are given an integer array capacity.
#
# A subarray capacity[l..r] is considered stable if:
#
# Its length is at least 3.
#
# The first and last elements are each equal to the sum of all elements
# strictly between them (i.e., capacity[l] = capacity[r] = capacity[l + 1]
# + capacity[l + 2] + ... + capacity[r - 1]).
#
# Return an integer denoting the number of stable subarrays.
#
# Example 1:
#
# Input: capacity = [9,3,3,3,9]
#
# Output: 2
#
# Explanation:
#
# [9,3,3,3,9] is stable because the first and last elements are both 9,
# and the sum of the elements strictly between them is 3 + 3 + 3 = 9.
#
# [3,3,3] is stable because the first and last elements are both 3, and
# the sum of the elements strictly between them is 3.
#
# Example 2:
#
# Input: capacity = [1,2,3,4,5]
#
# Output: 0
#
# Explanation:
#
# No subarray of length at least 3 has equal first and last elements, so
# the answer is 0.
#
# Example 3:
#
# Input: capacity = [-4,4,0,0,-8,-4]
#
# Output: 1
#
# Explanation:
#
# [-4,4,0,0,-8,-4] is stable because the first and last elements are both
# -4, and the sum of the elements strictly between them is 4 + 0 + 0 +
# (-8) = -4
#
# Constraints:
#
# 3 <= capacity.length <= 10^5
#
# -10^9 <= capacity[i] <= 10^9
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def countStableSubarrays(self, capacity: List[int]) -> int:
        """
        Interview explanation:
        Stable means capacity[l] == capacity[r] == sum(interior). With prefix
        sums, that is capacity[l] == capacity[r] and
        pfs[l+1] == pfs[r] - capacity[r]. Hash prior left endpoints.

        Algorithm:
        - Sweep right endpoint r; before using r, insert l = r-2 keyed by
          (capacity[l], pfs[l+1]).
        - Add frequency of (capacity[r], pfs[r] - capacity[r]).

        Complexity: O(n) time, O(n) space.
        """
        n = len(capacity)
        pfs = [0] * (n + 1)
        for i, x in enumerate(capacity):
            pfs[i + 1] = pfs[i] + x
        cnt = defaultdict(int)
        ans = 0
        for r in range(n):
            if r >= 2:
                cnt[(capacity[r - 2], pfs[r - 1])] += 1
            ans += cnt[(capacity[r], pfs[r] - capacity[r])]
        return ans

    def countStableSubarrays_pair_key(self, capacity: List[int]) -> int:
        """
        Interview explanation:
        Alternate keying: store (value, value + pfs[l+1]) and query
        (capacity[r], pfs[r]).

        Algorithm:
        - Same delayed insertion of left endpoints with length >= 3.

        Complexity: O(n) time, O(n) space.
        """
        n = len(capacity)
        pfs = [0] * (n + 1)
        for i, x in enumerate(capacity):
            pfs[i + 1] = pfs[i] + x
        cnt = defaultdict(int)
        ans = 0
        for r in range(2, n):
            l = r - 2
            key = (capacity[l], capacity[l] + pfs[l + 1])
            cnt[key] += 1
            ans += cnt[(capacity[r], pfs[r])]
        return ans
# @lc code=end

