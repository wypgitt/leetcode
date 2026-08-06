#
# @lc app=leetcode id=3937 lang=python3
#
# [3937] Minimum Operations to Make Array Modulo Alternating I
#
# https://leetcode.com/problems/minimum-operations-to-make-array-modulo-alternating-i/description/
#
# algorithms
# Medium (46.75%)
# Likes:    49
# Dislikes: 7
# Total Accepted:    21K
# Total Submissions: 44.8K
# Testcase Example:  "[1,4,2,8]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# In one operation, you can increase or decrease any element of nums by 1.
#
# An array is called modulo alternating if there exist two distinct
# integers x and y (0 <= x, y < k) such that:
#
# For every even index i, nums[i] % k == x
#
# For every odd index i, nums[i] % k == y
#
# Return the minimum number of operations required to make nums modulo
# alternating.
#
# Example 1:
#
# Input: nums = [1,4,2,8], k = 3
#
# Output: 2
#
# Explanation:
#
# Let's choose x = 1 for even indices and y = 2 for odd indices.
#
# Perform the following operations:
#
# Increment nums[1] = 4 by 1, giving nums = [1, 5, 2, 8].
#
# Decrement nums[2] = 2 by 1, giving nums = [1, 5, 1, 8].
#
# Now, for even indices, nums[i] % k = 1, and for odd indices, nums[i] % k
# = 2.
#
# Thus, the total number of operations required is 2.
#
# Example 2:
#
# Input: nums = [1,1,1], k = 3
#
# Output: 1
#
# Explanation:
#
# Incrementing nums[1] by 1 gives nums = [1, 2, 1], which satisfies the
# condition with x = 1 and y = 2.
#
# Thus, the total number of operations required is 1.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 10^9
#
# 2 <= k <= 100
#

# @lc code=start

class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        """
        Interview explanation:
        Choose distinct residues (x, y) for even/odd indices. Cost to change a
        value with residue r to target t is the circular distance on 0..k-1.
        Try all pairs since k <= 100.

        Algorithm:
        - Precompute residues.
        - For every x != y, sum min(|r-t|, k-|r-t|) over even→x and odd→y.
        - Return the minimum over pairs.

        Complexity: O(n * k^2) time, O(n) space.
        """
        n = len(nums)
        res = [x % k for x in nums]
        best = 10**18
        for x in range(k):
            for y in range(k):
                if x == y:
                    continue
                cost = 0
                for i, r in enumerate(res):
                    t = x if i % 2 == 0 else y
                    d = abs(r - t)
                    cost += min(d, k - d)
                if cost < best:
                    best = cost
        return best
# @lc code=end
