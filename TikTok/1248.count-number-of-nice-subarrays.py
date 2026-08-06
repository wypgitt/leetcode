#
# @lc app=leetcode id=1248 lang=python3
#
# [1248] Count Number of Nice Subarrays
#
# https://leetcode.com/problems/count-number-of-nice-subarrays/description/
#
# algorithms
# Medium (75.58%)
# Likes:    5533
# Dislikes: 153
# Total Accepted:    539K
# Total Submissions: 713K
# Testcase Example:  "[1,1,2,1,1]"
#
# Given an array of integers nums and an integer k. A continuous subarray is
# called nice if there are k odd numbers on it.
#
# Return the number of nice sub-arrays.
#
# Example 1:
#
# Input: nums = [1,1,2,1,1], k = 3
# Output: 2
# Explanation: The only sub-arrays with 3 odd numbers are [1,1,2,1] and
# [1,2,1,1].
#
# Example 2:
#
# Input: nums = [2,4,6], k = 1
# Output: 0
# Explanation: There are no odd numbers in the array.
#
# Example 3:
#
# Input: nums = [2,2,2,1,2,2,1,2,2,2], k = 2
# Output: 16
#
# Constraints:
#
# 1 <= nums.length <= 50000
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= nums.length
#


# @lc code=start
from typing import List

class Solution:
    def numberOfSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Nice subarray = exactly k odd numbers. atMost(k) - atMost(k-1) via
        sliding window counting odds.

        Algorithm:
        - def atMost(K): window with <=K odds; add window sizes
        - return atMost(k)-atMost(k-1)

        Complexity: O(n) time, O(1) space.
        """
        def atMost(K: int) -> int:
            if K < 0:
                return 0
            left = odds = ans = 0
            for right, x in enumerate(nums):
                odds += x & 1
                while odds > K:
                    odds -= nums[left] & 1
                    left += 1
                ans += right - left + 1
            return ans

        return atMost(k) - atMost(k - 1)

    def numberOfSubarrays_prefix(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: prefix odd-count; hashmap of how many prefixes with each
        odd count; for each prefix p add freq[p-k].

        Algorithm:
        - freq={0:1}; cur=0; for x: cur+=x%2; ans+=freq[cur-k]; freq[cur]++

        Complexity: O(n) time, O(n) space.
        """
        from collections import defaultdict
        freq = defaultdict(int)
        freq[0] = 1
        cur = ans = 0
        for x in nums:
            cur += x & 1
            ans += freq[cur - k]
            freq[cur] += 1
        return ans
# @lc code=end
