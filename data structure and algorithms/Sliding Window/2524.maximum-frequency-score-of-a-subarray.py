#
# @lc app=leetcode id=2524 lang=python3
#
# [2524] Maximum Frequency Score of a Subarray
#
# https://leetcode.com/problems/maximum-frequency-score-of-a-subarray/description/
#
# algorithms
# Hard (36.19%)
# Likes:    25
# Dislikes: 7
# Total Accepted:    1.7K
# Total Submissions: 4.7K
# Testcase Example:  "[1,1,1,2,1,2]\n3"
#
#
# You are given an integer array nums and a positive integer k.
#
# The frequency score of an array is the sum of the distinct values in the
# array raised to the power of their frequencies, taking the sum modulo
# 10^9 + 7.
#
# For example, the frequency score of the array [5,4,5,7,4,4] is (4^3 +
# 5^2 + 7^1) modulo (10^9 + 7) = 96.
#
# Return the maximum frequency score of a subarray of size k in nums. You
# should maximize the value under the modulo and not the actual value.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [1,1,1,2,1,2], k = 3
# Output: 5
# Explanation: The subarray [2,1,2] has a frequency score equal to 5. It
# can be shown that it is the maximum frequency score we can have.
#
# Example 2:
#
# Input: nums = [1,1,1,1,1,1], k = 4
# Output: 1
# Explanation: All the subarrays of length 4 have a frequency score equal
# to 1.
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def maxFrequencyScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Frequency score of a window = sum over distinct x of (x^freq(x)) mod
        10^9+7. Return the maximum score among all length-k subarrays
        (maximize the modular value, not the pre-mod integer).

        Algorithm:
        - Sliding window + Counter: init score for nums[0:k] via pow(..., mod).
        - On slide: subtract leaving x^old, update freq, add x^new; same for
          entering. Track max modular score.

        Complexity: O(n log k) time (modular pow), O(k) space.
        """
        MOD = 10**9 + 7
        cnt = Counter(nums[:k])
        cur = sum(pow(x, f, MOD) for x, f in cnt.items()) % MOD
        ans = cur
        for i in range(k, len(nums)):
            left = nums[i - k]
            cur = (cur - pow(left, cnt[left], MOD) + MOD) % MOD
            cnt[left] -= 1
            if cnt[left] > 0:
                cur = (cur + pow(left, cnt[left], MOD)) % MOD
            else:
                del cnt[left]
            right = nums[i]
            if cnt[right] > 0:
                cur = (cur - pow(right, cnt[right], MOD) + MOD) % MOD
            cnt[right] += 1
            cur = (cur + pow(right, cnt[right], MOD)) % MOD
            ans = max(ans, cur)
        return ans
# @lc code=end
