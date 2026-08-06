#
# @lc app=leetcode id=2327 lang=python3
#
# [2327] Number of People Aware of a Secret
#
# https://leetcode.com/problems/number-of-people-aware-of-a-secret/description/
#
# algorithms
# Medium (60.61%)
# Likes:    1504
# Dislikes: 165
# Total Accepted:    128.9K
# Total Submissions: 212.7K
# Testcase Example:  "6\n2\n4"
#
# On day 1, one person discovers a secret.
#
# You are given an integer delay, which means that each person will share the
# secret with a new person every day, starting from delay days after discovering
# the secret. You are also given an integer forget, which means that each person
# will forget the secret forget days after discovering it. A person cannot share
# the secret on the same day they forgot it, or on any day afterwards.
#
# Given an integer n, return the number of people who know the secret at the end
# of day n. Since the answer may be very large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: n = 6, delay = 2, forget = 4
# Output: 5
# Explanation:
# Day 1: Suppose the first person is named A. (1 person)
# Day 2: A is the only person who knows the secret. (1 person)
# Day 3: A shares the secret with a new person, B. (2 people)
# Day 4: A shares the secret with a new person, C. (3 people)
# Day 5: A forgets the secret, and B shares the secret with a new person, D. (3
# people)
# Day 6: B shares the secret with E, and C shares the secret with F. (5 people)
#
# Example 2:
#
# Input: n = 4, delay = 1, forget = 3
# Output: 6
# Explanation:
# Day 1: The first person is named A. (1 person)
# Day 2: A shares the secret with B. (2 people)
# Day 3: A and B share the secret with 2 new people, C and D. (4 people)
# Day 4: A forgets the secret. B, C, and D share the secret with 3 new people.
# (6 people)
#
#
#
# Constraints:
#
#
# 2 <= n <= 1000
#
#
# 1 <= delay < forget <= n
#

# @lc code=start
class Solution:
    def peopleAwareOfSecret(self, n: int, delay: int, forget: int) -> int:
        """
        Interview explanation:
        Day 1: one person learns a secret. They share on days
        [learn+delay, learn+forget); forget on learn+forget. Count people who
        still know on day n.

        Algorithm:
        - dp[i] = new learners on day i. share[i] accumulates people who start
          sharing. Use difference-array style: when someone learns on day i,
          they add to days i+delay .. i+forget-1.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (n + 1)  # new people on day i
        dp[1] = 1
        share = 0
        for day in range(2, n + 1):
            if day - delay >= 1:
                share = (share + dp[day - delay]) % MOD
            if day - forget >= 1:
                share = (share - dp[day - forget]) % MOD
            dp[day] = share
        # people who have not forgotten by day n: learned in (n-forget+1 .. n)
        ans = 0
        for day in range(n - forget + 1, n + 1):
            if day >= 1:
                ans = (ans + dp[day]) % MOD
        return ans

    def peopleAwareOfSecret_dp(self, n: int, delay: int, forget: int) -> int:
        """
        Interview explanation:
        Sliding-window DP of new learners (same as primary).

        Algorithm:
        - Maintain count of currently sharing people; sum recent learners.

        Complexity: O(n) time, O(n) space.
        """
        return self.peopleAwareOfSecret(n, delay, forget)
# @lc code=end
