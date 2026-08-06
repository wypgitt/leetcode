#
# @lc app=leetcode id=1850 lang=python3
#
# [1850] Minimum Adjacent Swaps to Reach the Kth Smallest Number
#
# https://leetcode.com/problems/minimum-adjacent-swaps-to-reach-the-kth-smallest-number/description/
#
# algorithms
# Medium (71.77%)
# Likes:    818
# Dislikes: 123
# Total Accepted:    29.0K
# Total Submissions: 40.4K
# Testcase Example:  "\"5489355142\""
#
# You are given a string num, representing a large integer, and an integer k.
#
# We call some integer wonderful if it is a permutation of the digits in num
# and is greater in value than num. There can be many wonderful integers.
# However, we only care about the smallest-valued ones.
#
# For example, when num = "5489355142":
#
# The 1^st smallest wonderful integer is "5489355214".
#
# The 2^nd smallest wonderful integer is "5489355241".
#
# The 3^rd smallest wonderful integer is "5489355412".
#
# The 4^th smallest wonderful integer is "5489355421".
#
# Return the minimum number of adjacent digit swaps that needs to be applied to
# num to reach the k^th smallest wonderful integer.
#
# The tests are generated in such a way that k^th smallest wonderful integer
# exists.
#
# Example 1:
#
# Input: num = "5489355142", k = 4
# Output: 2
# Explanation: The 4^th smallest wonderful number is "5489355421". To get this
# number:
# - Swap index 7 with index 8: "5489355142" -> "5489355412"
# - Swap index 8 with index 9: "5489355412" -> "5489355421"
#
# Example 2:
#
# Input: num = "11112", k = 4
# Output: 4
# Explanation: The 4^th smallest wonderful number is "21111". To get this
# number:
# - Swap index 3 with index 4: "11112" -> "11121"
# - Swap index 2 with index 3: "11121" -> "11211"
# - Swap index 1 with index 2: "11211" -> "12111"
# - Swap index 0 with index 1: "12111" -> "21111"
#
# Example 3:
#
# Input: num = "00123", k = 1
# Output: 1
# Explanation: The 1^st smallest wonderful number is "00132". To get this
# number:
# - Swap index 3 with index 4: "00123" -> "00132"
#
# Constraints:
#
# 2 <= num.length <= 1000
#
# 1 <= k <= 1000
#
# num only consists of digits.
#

# @lc code=start
class Solution:
    def getMinSwaps(self, num: str, k: int) -> int:
        """
        Interview explanation:
        Apply next-permutation k times to get target; count min adjacent swaps
        to turn num into target (selection: for each position bring needed digit
        from the right by swapping left).

        Algorithm (k next-perms + count swaps):
        - digits = list(num); apply next_permutation k times -> target.
        - For each i, find j>i with cur[j]==target[i]; swap j down to i counting.

        Complexity: O(k*n + n^2) time, O(n) space.
        """
        def next_permutation(a: list) -> None:
            i = len(a) - 2
            while i >= 0 and a[i] >= a[i + 1]:
                i -= 1
            j = len(a) - 1
            while a[j] <= a[i]:
                j -= 1
            a[i], a[j] = a[j], a[i]
            a[i + 1:] = reversed(a[i + 1:])

        target = list(num)
        for _ in range(k):
            next_permutation(target)
        cur = list(num)
        ans = 0
        for i in range(len(cur)):
            if cur[i] == target[i]:
                continue
            j = i
            while cur[j] != target[i]:
                j += 1
            while j > i:
                cur[j], cur[j - 1] = cur[j - 1], cur[j]
                j -= 1
                ans += 1
        return ans
# @lc code=end
