#
# @lc app=leetcode id=2638 lang=python3
#
# [2638] Count the Number of K-Free Subsets
#
# https://leetcode.com/problems/count-the-number-of-k-free-subsets/description/
#
# algorithms
# Medium (47.36%)
# Likes:    99
# Dislikes: 19
# Total Accepted:    5.4K
# Total Submissions: 11.4K
# Testcase Example:  "[5,4,6]\n1"
#
#
# You are given an integer array nums, which contains distinct elements
# and an integer k.
#
# A subset is called a k-Free subset if it contains no two elements with
# an absolute difference equal to k. Notice that the empty set is a k-Free
# subset.
#
# Return the number of k-Free subsets of nums.
#
# A subset of an array is a selection of elements (possibly none) of the
# array.
#
# Example 1:
#
# Input: nums = [5,4,6], k = 1
# Output: 5
# Explanation: There are 5 valid subsets: {}, {5}, {4}, {6} and {4, 6}.
#
# Example 2:
#
# Input: nums = [2,3,5,8], k = 5
# Output: 12
# Explanation: There are 12 valid subsets: {}, {2}, {3}, {5}, {8}, {2, 3},
# {2, 3, 5}, {2, 5}, {2, 5, 8}, {2, 8}, {3, 5} and {5, 8}.
#
# Example 3:
#
# Input: nums = [10,5,9,11], k = 20
# Output: 16
# Explanation: All subsets are valid. Since the total count of subsets is
# 2^4 = 16, so the answer is 16.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 1000
#
# 1 <= k <= 1000
#
# @lc code=start
from collections import Counter, defaultdict
from typing import List


class Solution:
    def countTheNumOfKFreeSubsets(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subsets where no two chosen values differ by exactly k
        (empty subset included). Equal values do not differ by k, so all
        copies of one value may be chosen together.

        Algorithm:
        - Frequency-count values; group by residue mod k (only same residue
          can differ by k), sort within each residue.
        - Split each residue into chains where consecutive values differ by k.
        - For a chain with frequencies f0,f1,... use house-robber DP:
          skip current: previous total; take current: previous-skip * (2^f - 1).
        - Multiply subset counts (each includes empty) across chains.

        Complexity: O(n log n) time, O(n) space.
        """
        cnt = Counter(nums)

        def chain_ways(freqs: List[int]) -> int:
            # dp0 = ways not taking last value; dp1 = ways taking last value
            dp0, dp1 = 1, 0
            for f in freqs:
                choose = (1 << f) - 1  # nonempty subsets of this value
                ndp0 = dp0 + dp1
                ndp1 = dp0 * choose
                dp0, dp1 = ndp0, ndp1
            return dp0 + dp1

        # Only values with the same residue mod k can differ by k.
        by_res = defaultdict(list)
        for v in cnt:
            by_res[v % k].append(v)

        ans = 1
        for vals in by_res.values():
            vals.sort()
            i, n = 0, len(vals)
            while i < n:
                freqs = [cnt[vals[i]]]
                j = i + 1
                while j < n and vals[j] - vals[j - 1] == k:
                    freqs.append(cnt[vals[j]])
                    j += 1
                ans *= chain_ways(freqs)
                i = j
        return ans
# @lc code=end
