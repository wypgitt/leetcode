#
# @lc app=leetcode id=2193 lang=python3
#
# [2193] Minimum Number of Moves to Make Palindrome
#
# https://leetcode.com/problems/minimum-number-of-moves-to-make-palindrome/description/
#
# algorithms
# Hard (53.01%)
# Likes:    1063
# Dislikes: 79
# Total Accepted:    36.9K
# Total Submissions: 69.5K
# Testcase Example:  "\"aabb\""
#
# You are given a string s consisting only of lowercase English letters.
#
# In one move, you can select any two adjacent characters of s and swap them.
#
# Return the minimum number of moves needed to make s a palindrome.
#
# Note that the input will be generated such that s can always be converted to a
# palindrome.
#
#
#
# Example 1:
#
# Input: s = "aabb"
# Output: 2
# Explanation:
# We can obtain two palindromes from s, "abba" and "baab".
# - We can obtain "abba" from s in 2 moves: "aabb" -> "abab" -> "abba".
# - We can obtain "baab" from s in 2 moves: "aabb" -> "abab" -> "baab".
# Thus, the minimum number of moves needed to make s a palindrome is 2.
#
# Example 2:
#
# Input: s = "letelt"
# Output: 2
# Explanation:
# One of the palindromes we can obtain from s in 2 moves is "lettel".
# One of the ways we can obtain it is "letelt" -> "letetl" -> "lettel".
# Other palindromes such as "tleelt" can also be obtained in 2 moves.
# It can be shown that it is not possible to obtain a palindrome in less than 2
# moves.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 2000
#
#
# s consists only of lowercase English letters.
#
#
# s can be converted to a palindrome using a finite number of moves.
#

# @lc code=start
class Solution:
    def minMovesToMakePalindrome(self, s: str) -> int:
        """
        Interview explanation:
        Only adjacent swaps allowed; min swaps to make s a palindrome. Greedy:
        match from outside in; for s[l], find matching char from right; cost is
        distance swapped to position r.

        Algorithm:
        (two pointers + greedy)
        - Convert to list; while l<r: if s[l]==s[r] advance; else find k from r
          with s[k]==s[l]; if none, s[l] is middle odd char — bubble toward
          center; else swap s[k] toward r counting swaps.

        Complexity: O(n^2) time, O(n) space.
        """
        arr = list(s)
        n = len(arr)
        l, r = 0, n - 1
        ans = 0
        while l < r:
            if arr[l] == arr[r]:
                l += 1
                r -= 1
                continue
            k = r
            while k > l and arr[k] != arr[l]:
                k -= 1
            if k == l:
                # arr[l] is center; move one step toward middle
                arr[l], arr[l + 1] = arr[l + 1], arr[l]
                ans += 1
            else:
                while k < r:
                    arr[k], arr[k + 1] = arr[k + 1], arr[k]
                    k += 1
                    ans += 1
                l += 1
                r -= 1
        return ans
# @lc code=end
