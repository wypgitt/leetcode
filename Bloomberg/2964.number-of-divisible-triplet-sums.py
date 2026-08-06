#
# @lc app=leetcode id=2964 lang=python3
#
# [2964] Number of Divisible Triplet Sums
#
# https://leetcode.com/problems/number-of-divisible-triplet-sums/description/
#
# algorithms
# Medium (67.70%)
# Likes:    35
# Dislikes: 6
# Total Accepted:    10.3K
# Total Submissions: 15.2K
# Testcase Example:  "[3,3,4,7,8]\n5"
#
#
# Given a 0-indexed integer array nums and an integer d, return the number
# of triplets (i, j, k) such that i < j < k and (nums[i] + nums[j] +
# nums[k]) % d == 0.
#
# Example 1:
#
# Input: nums = [3,3,4,7,8], d = 5
# Output: 3
# Explanation: The triplets which are divisible by 5 are: (0, 1, 2), (0,
# 2, 4), (1, 2, 4).
# It can be shown that no other triplet is divisible by 5. Hence, the
# answer is 3.
#
# Example 2:
#
# Input: nums = [3,3,3,3], d = 3
# Output: 4
# Explanation: Any triplet chosen here has a sum of 9, which is divisible
# by 3. Hence, the answer is the total number of triplets which is 4.
#
# Example 3:
#
# Input: nums = [3,3,3,3], d = 6
# Output: 0
# Explanation: Any triplet chosen here has a sum of 9, which is not
# divisible by 6. Hence, the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^9
#
# 1 <= d <= 10^9
#
# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def divisibleTripletCount(self, nums: List[int], d: int) -> int:
        """
        Interview explanation:
        Premium: count triplets i < j < k with (nums[i]+nums[j]+nums[k]) % d == 0.

        Algorithm:
        - Hash remainders of indices before j. For each pair (j, k), add count of
          needed remainder for i. Then insert nums[j] % d.

        Complexity: O(n^2) time, O(min(n, d)) space.
        """
        cnt: dict = defaultdict(int)
        ans = 0
        n = len(nums)
        for j in range(n):
            for k in range(j + 1, n):
                need = (d - (nums[j] + nums[k]) % d) % d
                ans += cnt[need]
            cnt[nums[j] % d] += 1
        return ans

    def divisibleTripletCount_suffix(self, nums: List[int], d: int) -> int:
        """
        Interview explanation:
        Alternate: walk from the right, counting k-side remainders while enumerating
        pairs (i, j).

        Algorithm:
        - For j from n-1 down to 1, for each i < j add count[needed], then ++count[nums[j]%d].

        Complexity: O(n^2) time, O(min(n, d)) space.
        """
        from collections import Counter

        count: Counter = Counter()
        ans = 0
        for j in range(len(nums) - 1, 0, -1):
            for i in range(j - 1, -1, -1):
                ans += count[-(nums[i] + nums[j]) % d]
            count[nums[j] % d] += 1
        return ans
# @lc code=end
