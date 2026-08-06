#
# @lc app=leetcode id=3851 lang=python3
#
# [3851] Maximum Requests Without Violating the Limit
#
# https://leetcode.com/problems/maximum-requests-without-violating-the-limit/description/
#
# algorithms
# Medium (64.95%)
# Likes:    5
# Dislikes: 2
# Total Accepted:    418
# Total Submissions: 645
# Testcase Example:  '[[1,1],[2,1],[1,7],[2,8]]\n1\n4'
#
# You are given a 2D integer array requests, where requests[i] = [useri, timei]
# indicates that useri made a request at timei.
# 
# You are also given two integers k and window.
# 
# A user violates the limit if there exists an integer t such that the user
# makes strictly more than k requests in the inclusive interval [t, t +
# window].
# 
# You may drop any number of requests.
# 
# Return an integer denoting the maximum​​​​​​​ number of requests that can
# remain such that no user violates the limit.
# 
# 
# Example 1:
# 
# 
# Input: requests = [[1,1],[2,1],[1,7],[2,8]], k = 1, window = 4
# 
# Output: 4
# 
# Explanation:​​​​​​​
# 
# 
# For user 1, the request times are [1, 7]. The difference between them is 6,
# which is greater than window = 4.
# For user 2, the request times are [1, 8]. The difference is 7, which is also
# greater than window = 4.
# No user makes more than k = 1 request within any inclusive interval of length
# window. Therefore, all 4 requests can remain.
# 
# 
# 
# Example 2:
# 
# 
# Input: requests = [[1,2],[1,5],[1,2],[1,6]], k = 2, window = 5
# 
# Output: 2
# 
# Explanation:​​​​​​​
# 
# 
# For user 1, the request times are [2, 2, 5, 6]. The inclusive interval [2, 7]
# of length window = 5 contains all 4 requests.
# Since 4 is strictly greater than k = 2, at least 2 requests must be
# removed.
# After removing any 2 requests, every inclusive interval of length window
# contains at most k = 2 requests.
# Therefore, the maximum number of requests that can remain is 2.
# 
# 
# 
# Example 3:
# 
# 
# Input: requests = [[1,1],[2,5],[1,2],[3,9]], k = 1, window = 1
# 
# Output: 3
# 
# Explanation:
# 
# 
# For user 1, the request times are [1, 2]. The difference is 1, which is equal
# to window = 1.
# The inclusive interval [1, 2] contains both requests, so the count is 2,
# which exceeds k = 1. One request must be removed.
# Users 2 and 3 each have only one request and do not violate the limit.
# Therefore, the maximum number of requests that can remain is 3.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= requests.length <= 10^5
# requests[i] = [useri, timei]
# 1 <= k <= requests.length
# 1 <= useri, timei, window <= 10^5
# 
# 
#

# @lc code=start
from collections import defaultdict, deque


class Solution:
    def maxRequests(self, requests: list[list[int]], k: int, window: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        Each request is:

            [user, time]

        A user violates the limit if there is some inclusive time interval:

            [t, t + window]

        that contains strictly more than `k` of that user's remaining requests.

        We may drop any requests. Return the maximum number of requests that can
        remain without any user violating the limit.

        Important detail:
        The interval is inclusive. So two request times `a <= b` are within a
        window of length `window` exactly when:

            b - a <= window

        Key observation 1: users are independent
        ----------------------------------------
        A violation is checked separately for each user. Dropping or keeping a
        request from user A cannot affect user B.

        Therefore:

            answer = sum(best_keep_count_for_each_user)

        So we group request times by user and solve one user's sorted times at a
        time.

        Key observation 2: sorted selected times condition
        --------------------------------------------------
        Consider one user and their kept request times in sorted order:

            kept[0] <= kept[1] <= ... <= kept[m - 1]

        The user is valid if and only if every group of `k + 1` consecutive kept
        requests has span greater than `window`:

            kept[i + k] - kept[i] > window

        Why?
        If `k + 1` kept requests fit in some inclusive interval of length
        `window`, then the first and last of those requests have difference at
        most `window`.

        Conversely, if some `k + 1` consecutive kept requests have first/last
        difference at most `window`, then the interval starting at the first
        request contains all `k + 1`, causing a violation.

        Greedy choice
        -------------
        For one user's request times sorted from earliest to latest:

        Keep a request time `time` if adding it would not create a violation.

        Since all previous kept requests are already valid, the only possible new
        violation must include the new request as the latest request.

        To test that, we only need the `k`-th most recent kept request:

        * If fewer than `k` requests are currently kept, adding this one cannot
          create `k + 1` requests.
        * Otherwise, let `oldest_of_last_k` be the earliest among the last `k`
          kept times.

          Adding `time` would create `k + 1` requests in a window if:

              time - oldest_of_last_k <= window

          So we keep `time` only when:

              time - oldest_of_last_k > window

        Why greedy is optimal
        ---------------------
        Intuition:
        Keeping earlier valid requests is never worse than replacing them with
        later requests. Earlier requests leave at least as much room for future
        requests under the same spacing/window constraint.

        More formal exchange-style view:
        Let the greedy selected sequence for one user be:

            g1, g2, ..., gp

        For any feasible selected sequence:

            s1, s2, ..., sq

        we can show by induction that for every position `r` that both sequences
        have:

            gr <= sr

        The first `k` greedy choices are simply the earliest available requests,
        so they are no later than any feasible sequence's first `k` choices.

        For `r > k`, a feasible sequence must satisfy:

            sr - s(r-k) > window

        By induction:

            g(r-k) <= s(r-k)

        so `sr` is also late enough to be a valid candidate after the greedy
        prefix. Greedy chooses the earliest valid candidate, so:

            gr <= sr

        If there were a feasible sequence longer than greedy's sequence, its
        next request would be a valid next candidate for greedy too, a
        contradiction. Therefore greedy keeps the maximum possible number.

        Data structure choice
        ---------------------
        We use:

        * `defaultdict(list)` to group request times by user.
        * Sorting each user's times so the sliding/greedy decision is local.
        * A `deque` containing the last at most `k` kept times for the current
          user.

        Why a deque?
        We only need to inspect the oldest of the last `k` kept requests. A
        deque gives:

        * `last_kept[0]` in O(1)
        * append new kept times in O(1)
        * pop from the left when more than `k` kept times are stored in O(1)

        We do not need to store every kept time for the current user once it is
        older than the last `k`, because it can never be part of a new `k + 1`
        group ending at a future request.

        Algorithm
        ---------
        1. Group all request times by user.
        2. For each user's list of times:
              - sort times ascending
              - initialize `last_kept` as an empty deque
              - for each time:
                    if fewer than k requests are in `last_kept`, keep it
                    else keep it only if `time - last_kept[0] > window`
              - whenever keeping a request, increment the answer and append its
                time to `last_kept`
              - if `last_kept` grows beyond k, pop from the left
        3. Return the total kept count.

        Walkthrough
        -----------
        Example:

            requests = [[1,2], [1,5], [1,2], [1,6]]
            k = 2
            window = 5

        User 1 times after sorting:

            [2, 2, 5, 6]

        Greedy:

            keep 2       last_kept = [2]
            keep 2       last_kept = [2, 2]
            test 5: 5 - 2 = 3 <= 5, skip
            test 6: 6 - 2 = 4 <= 5, skip

        Kept count is 2.

        Correctness proof
        -----------------
        Lemma 1:
        For one user, a kept set is valid if and only if no `k + 1` consecutive
        kept times have first/last difference at most `window`.

        Proof:
        If `k + 1` kept times are inside an inclusive interval `[t, t + window]`,
        then their smallest and largest times differ by at most `window`. Taking
        the consecutive block between those two in sorted order gives `k + 1`
        consecutive kept times with span at most `window`.

        Conversely, if `k + 1` consecutive kept times have span at most
        `window`, then the interval starting at the first of them contains all
        `k + 1`, so the user violates the limit.

        Lemma 2:
        When processing a new time, the greedy test accepts it exactly when
        adding it preserves validity.

        Proof:
        Before processing the new time, all kept requests are valid. Since times
        are processed in sorted order, any newly created violation must include
        the new time as the latest element. By Lemma 1, it is enough to check the
        block consisting of the new time and the previous `k` kept times. If
        there are fewer than `k` previous kept times, such a block cannot exist.
        Otherwise, the block violates exactly when:

            time - oldest_of_last_k <= window

        The algorithm rejects in that case and accepts otherwise.

        Lemma 3:
        For each user, the greedy algorithm keeps the maximum possible number of
        requests.

        Proof:
        Let greedy's selected times be `g1, g2, ...`. For any feasible selected
        sequence `s1, s2, ...`, we prove by induction that `gr <= sr` for every
        position `r` that exists in both sequences.

        For `r <= k`, greedy chooses the earliest available requests, so `gr` is
        no later than the `r`-th request of any feasible sequence.

        For `r > k`, feasibility of `s` implies:

            sr - s(r-k) > window

        By induction, `g(r-k) <= s(r-k)`, so `sr` is also far enough after
        `g(r-k)` to be a valid `r`-th greedy candidate. Greedy chooses the
        earliest valid candidate, hence `gr <= sr`.

        If a feasible sequence had more requests than greedy, its next request
        would be a valid next candidate for greedy, contradicting that greedy
        stopped. Therefore greedy is optimal for that user.

        Lemma 4:
        Summing the optimal kept counts per user gives the global optimum.

        Proof:
        User limits are independent. A request from one user never affects any
        interval count for another user. Therefore the best global solution is
        obtained by independently taking the best solution for every user and
        summing their kept counts.

        Theorem:
        The algorithm returns the maximum number of requests that can remain
        without any user violating the limit.

        Proof:
        By Lemma 3, the algorithm computes the optimal kept count for each user.
        By Lemma 4, summing these counts gives the global optimum.

        Complexity analysis
        -------------------
        Let `R = len(requests)`.

        Time:

            O(R log R)

        Reason:
        Grouping is O(R). Sorting all user lists costs at most O(R log R) total.
        The greedy scan across all users is O(R).

        Space:

            O(R)

        Reason:
        We store all times grouped by user. The deque for one user stores at
        most `k` times, and over the whole algorithm this is dominated by the
        grouped input storage.

        Edge cases
        ----------
        * One request:
          Always keep it.

        * `k >=` number of requests for a user:
          That user can keep all requests because they never have more than `k`
          in any interval.

        * Duplicate timestamps:
          They are all inside the same inclusive interval. The algorithm keeps
          at most `k` of them for a user.

        * Difference exactly equal to `window`:
          This is still inside the inclusive interval, so `time - old <= window`
          violates when it creates `k + 1` requests.

        * Many users:
          They are processed independently and summed.

        Test strategy
        -------------
        Useful tests:

            requests = [[1,1], [2,1], [1,7], [2,8]], k = 1, window = 4 -> 4
            requests = [[1,2], [1,5], [1,2], [1,6]], k = 2, window = 5 -> 2
            requests = [[1,1], [2,5], [1,2], [3,9]], k = 1, window = 1 -> 3
            requests = [[1,5], [1,5], [1,5]], k = 2, window = 10 -> 2
            requests = [[1,1], [1,3], [1,5]], k = 1, window = 1 -> 3

        For small random cases, brute force all subsets per user and compare
        against this greedy solution.

        Possible improvements
        ---------------------
        We could sort the whole request list by `(user, time)` and process it in
        one pass instead of building a dictionary of lists. That has the same
        O(R log R) time and can reduce grouping overhead. The grouped version is
        easier to explain and directly mirrors the user-independence idea.
        """

        times_by_user: dict[int, list[int]] = defaultdict(list)
        for user, time in requests:
            times_by_user[user].append(time)

        kept_total = 0

        for times in times_by_user.values():
            times.sort()
            last_kept: deque[int] = deque()

            for time in times:
                if len(last_kept) < k or time - last_kept[0] > window:
                    kept_total += 1
                    last_kept.append(time)
                    if len(last_kept) > k:
                        last_kept.popleft()

        return kept_total
# @lc code=end
