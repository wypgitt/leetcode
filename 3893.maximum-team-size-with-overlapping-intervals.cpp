// Translated from 3893.maximum-team-size-with-overlapping-intervals.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3893 lang=python3
// #
// # [3893] Maximum Team Size with Overlapping Intervals
// #
// # https://leetcode.com/problems/maximum-team-size-with-overlapping-intervals/description/
// #
// # algorithms
// # Medium (55.26%)
// # Likes:    6
// # Dislikes: 1
// # Total Accepted:    295
// # Total Submissions: 537
// # Testcase Example:  '[1,2,3]\n[4,5,6]'
// #
// # You are given two integer arrays startTime and endTime of length n.
// # 
// # 
// # startTime[i] represents the start time of the i^th employee.
// # endTime[i] represents the end time of the i^th employee.
// # 
// # 
// # Two employees i and j can interact if their time intervals overlap. Two
// # intervals are considered overlapping if they share at least one common time
// # point.
// # 
// # A team is valid if there exists at least one employee in the team who can
// # interact with every other member of the team.
// # 
// # Return an integer denoting the maximum possible size of such a team.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: startTime = [1,2,3], endTime = [4,5,6]
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # For i = 0 with interval [1, 4].
// # It overlaps with i = 1 having interval [2, 5] and i = 2 having interval [3,
// # 6].
// # Thus, index 0 can interact with all other indices, so the team size is 3.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: startTime = [2,5,8], endTime = [3,7,9]
// # 
// # Output: 1
// # 
// # Explanation:
// # 
// # 
// # For i = 0, interval [2, 3] does not overlap with [5, 7] or [8, 9].
// # For i = 1, interval [5, 7] does not overlap with [2, 3] or [8, 9].
// # For i = 2, interval [8, 9] does not overlap with [2, 3] or [5, 7].
// # Thus, no index can interact with others, so the maximum team size is 1.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: startTime = [3,4,6], endTime = [8,5,7]
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # For i = 0 with interval [3, 8].
// # It overlaps with i = 1 having interval [4, 5] and i = 2 having interval [6,
// # 7].
// # Thus, index 0 can interact with all other indices, so the team size is
// # 3.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n == startTime.length == endTime.length <= 10^5
// # 0 <= startTime[i] <= endTime[i] <= 10^9
// # 
// # 
// #
// 
// # @lc code=start
// from bisect import bisect_left, bisect_right
// 
// 
// class Solution:
//     def maximumTeamSize(self, startTime: list[int], endTime: list[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         Each employee has an inclusive time interval:
// 
//             [startTime[i], endTime[i]]
// 
//         Two employees can interact if their intervals overlap at at least one
//         common time point.  A team is valid if there is one employee in the team
//         who overlaps with every other employee in that same team.
// 
//         We need the maximum possible valid team size.
// 
//         Key interpretation
//         ------------------
//         The team does NOT need to be pairwise overlapping.
// 
//         That is the most important detail.  We only need one "hub" employee who
//         can interact with everyone else on the team.  The other employees do not
//         have to interact with each other.
// 
//         Therefore, if employee `i` is the hub, the largest team using `i` as the
//         required universal-interaction employee is:
// 
//             employee i
//             + every employee whose interval overlaps interval i
// 
//         So the answer is:
// 
//             max over every interval i of:
//                 count of intervals that overlap interval i
// 
//         Overlap condition
//         -----------------
//         For two inclusive intervals:
// 
//             A = [s, e]
//             B = [x, y]
// 
//         They overlap if and only if:
// 
//             x <= e and y >= s
// 
//         Equivalently, B does NOT overlap A only if:
// 
//             y < s       # B ends before A starts
//             or
//             x > e       # B starts after A ends
// 
//         Counting overlaps efficiently
//         -----------------------------
//         For a fixed hub interval [s, e], we want the number of intervals [x, y]
//         such that:
// 
//             x <= e and y >= s
// 
//         We can count this using sorted arrays:
// 
//         * `starts`: all start times sorted
//         * `ends`: all end times sorted
// 
//         Number of intervals with start <= e:
// 
//             bisect_right(starts, e)
// 
//         Among those, the intervals that still do NOT overlap are exactly the
//         ones with end < s.  The number of intervals with end < s is:
// 
//             bisect_left(ends, s)
// 
//         Therefore:
// 
//             overlap_count = count(start <= e) - count(end < s)
//                           = bisect_right(starts, e) - bisect_left(ends, s)
// 
//         Why is this subtraction valid?
//         ------------------------------
//         Any interval with `end < s` must also have `start <= end < s <= e`,
//         because every interval has start <= end.  So every interval that ends
//         before the hub starts is included in the `start <= e` group.  Subtracting
//         them leaves exactly the intervals whose start is not too late and whose
//         end is not too early, which is precisely the overlap condition.
// 
//         Data structures
//         ---------------
//         We use two sorted lists:
// 
//         * `starts` supports binary search for how many intervals start by time e.
//         * `ends` supports binary search for how many intervals end before time s.
// 
//         Python's `bisect_right` and `bisect_left` give these counts in O(log n).
// 
//         Algorithm
//         ---------
//         1. Sort all start times.
//         2. Sort all end times.
//         3. For every employee interval [s, e]:
//               before_or_at_end = bisect_right(starts, e)
//               ended_before_start = bisect_left(ends, s)
//               overlaps = before_or_at_end - ended_before_start
//               update the answer with overlaps
//         4. Return the largest overlap count.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For a fixed employee i, the largest valid team with i as the
//         hub has size equal to the number of intervals that overlap i.
//         A team with i as hub can include exactly those employees whose intervals
//         overlap employee i's interval.  Any non-overlapping employee cannot be
//         included, because the hub would not be able to interact with them.  Every
//         overlapping employee can be included, because the only required condition
//         is that the hub interacts with every team member.
// 
//         Lemma 2: For a hub interval [s, e], the formula
//         `bisect_right(starts, e) - bisect_left(ends, s)` counts exactly the
//         intervals that overlap [s, e].
//         `bisect_right(starts, e)` counts intervals whose start is <= e.
//         Among these, `bisect_left(ends, s)` counts intervals whose end is < s,
//         which are exactly the intervals ending before the hub begins.  Removing
//         those leaves exactly the intervals with start <= e and end >= s, the
//         inclusive-overlap condition.
// 
//         Lemma 3: The algorithm considers the optimal hub.
//         Every valid team has at least one employee who acts as the hub.  The
//         algorithm evaluates every employee as a possible hub, so it evaluates a
//         hub from an optimal team.
// 
//         Theorem: The algorithm returns the maximum possible valid team size.
//         By Lemma 1, for each possible hub the best team size is its overlap
//         count.  By Lemma 2, the algorithm computes that count correctly.  By
//         Lemma 3, the algorithm considers the hub of an optimal team.  Therefore
//         the maximum count returned by the algorithm is exactly the optimal team
//         size.
// 
//         Complexity analysis
//         -------------------
//         Let n be the number of employees.
// 
//         Sorting the starts and ends costs O(n log n).
//         For each of n intervals, we perform two binary searches, each O(log n).
// 
//         Total time:  O(n log n)
//         Total space: O(n), for the two sorted arrays
// 
//         Edge cases
//         ----------
//         * n = 1:
//           The only employee forms a valid team of size 1.
// 
//         * Touching endpoints:
//           [1, 3] and [3, 5] overlap because they share time point 3.  This is
//           why we use `start <= e` and `end >= s`, not strict inequalities.
// 
//         * No overlaps:
//           Every employee can at least form a team alone, so the answer is 1.
// 
//         * Nested intervals:
//           A large interval can be the hub for many smaller intervals even if the
//           smaller intervals do not overlap each other.
// 
//         * Large time values up to 10^9:
//           We never build an array by time value; we only sort the given n
//           endpoints, so large coordinates are handled naturally.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [1,2,3], [4,5,6] -> 3
//               [2,5,8], [3,7,9] -> 1
//               [3,4,6], [8,5,7] -> 3
// 
//         * Endpoint-touching intervals:
//               [1,3] and [3,4] should overlap.
// 
//         * Nested intervals:
//               [1,10] can be the hub for [2,3], [4,5], [8,9].
// 
//         * Random small tests compared against a brute-force O(n^2) overlap
//           counter.
// 
//         Possible improvement?
//         ---------------------
//         O(n log n) is already efficient for n <= 100,000.  A sweep-line can also
//         find the maximum number of intervals active at a single time point, but
//         that solves a different problem: it requires all chosen intervals to
//         share one common time point.  Here we only need all chosen intervals to
//         overlap one hub interval, so the binary-search overlap count is the
//         direct fit.
//         """
// 
//         starts = sorted(startTime)
//         ends = sorted(endTime)
// 
//         best = 1
//         for start, end in zip(startTime, endTime):
//             started_by_end = bisect_right(starts, end)
//             ended_before_start = bisect_left(ends, start)
//             best = max(best, started_by_end - ended_before_start)
// 
//         return best
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
public:
    int maximumTeamSize(vector<int>& startTime, vector<int>& endTime) {
        vector<int> starts = startTime, ends = endTime;
        sort(starts.begin(), starts.end());
        sort(ends.begin(), ends.end());
        int best = 1;
        for (int i = 0; i < (int)startTime.size(); ++i) {
            int started = upper_bound(starts.begin(), starts.end(), endTime[i]) - starts.begin();
            int ended = lower_bound(ends.begin(), ends.end(), startTime[i]) - ends.begin();
            best = max(best, started - ended);
        }
        return best;
    }
};
