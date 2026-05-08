// Translated from 911.online-election.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=911 lang=python3
// #
// # [911] Online Election
// #
// 
// # =============================================================================
// # INTERVIEW: ELEVATOR PITCH (~30 seconds)
// # =============================================================================
// #
// # "Votes arrive at strictly increasing timestamps. After each ballot we know who is
// # ahead: whoever has the most votes; on a tie, whoever got a vote **most recently**.
// # That's a single forward simulation updating counts and the current leader with one
// # comparison per vote. Queries ask 'who leads at time t?' — that's **prefix-only**
// # information, so we **snapshot the leader after each vote** and answer queries by
// # binary-searching the last vote at or before `t`. Preprocessing O(n), each query
// # O(log n)."
// #
// # =============================================================================
// # PROBLEM (PRECISE)
// # =============================================================================
// #
// # • `persons[i]` receives one vote at time `times[i]`.
// # • `times` is strictly increasing (typical LeetCode constraint).
// # • Query `q(t)`: among all votes cast at times **≤ t**, which candidate has the
// #   most votes? **Tie-break:** if multiple have the same maximum count, return the
// #   candidate who received a vote **most recently** among those tied at the top.
// #
// # =============================================================================
// # WHY PREFIX SNAPSHOTS + BINARY SEARCH?
// # =============================================================================
// #
// # The leader depends only on votes with timestamp ≤ t — a **prefix** of the
// # chronological vote stream. Between consecutive vote times the leader does not
// # change. Therefore:
// #
// #   leader_at(t) = leader_immediately_after_processing_the_last_vote_with_time_≤t
// #
// # Precompute `leaders[k]` = winner after applying votes `0 .. k` inclusive.
// # For query `t`, find largest index `k` with `times[k] ≤ t` (binary search on sorted
// # `times`), then return `leaders[k]`.
// #
// # =============================================================================
// # TIE-BREAKING — SINGLE PASS UPDATE RULE
// # =============================================================================
// #
// # Process votes in order. Maintain `cnt[p]` = votes for person `p`, and `leader`.
// #
// # After recording vote for person `p` at this step:
// #
// #       if cnt[p] >= cnt[leader]:
// #           leader = p
// #
// # **Why this encodes “most recent wins ties”:**  
// # When we increment `p`, only `p`’s count can increase. If after incrementing,
// # `cnt[p]` **strictly exceeds** `cnt[leader]`, `p` is ahead. If `cnt[p] == cnt[leader]`,
// # then `p` is tied with the previous leader’s count — but `p` **just received** a vote,
// # so among everyone tied at that count, `p` is the most recently active → becomes
// # leader. If `cnt[p] < cnt[leader]`, the incumbent stays ahead.
// #
// # No need to track “last vote time” per person separately; processing order makes
// # the last increment resolve ties correctly.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # • **`counts`** — `dict` / hash map from person id → vote count. Only persons who
// #   appear need entries → **O(unique candidates)** entries, ≤ **O(n)**.
// # • **`times`** — stored for queries (sorted input enables binary search).
// # • **`leaders`** — array parallel to `times`, length **n**. **O(n)** space.
// #
// # Alternatives: **array** for counts if person ids bounded small (not assumed here).
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY
// # =============================================================================
// #
// # **`__init__`:** One scan over **n** votes — **O(n)** time, **O(n)** space for
// # `leaders` plus map.
// #
// # **`q(t)`:** Binary search on `times` — **O(log n)** time, **O(1)** extra space.
// #
// # Total across **q** queries: **O(q log n)** online time after **O(n)** preprocess.
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # • **Single vote** — `leaders` length 1; any `t ≥ times[0]` returns that winner.
// # • **All votes same person** — leader never changes after first ballot (still update
// #   rule holds).
// # • **Query `t` before first vote** — problem constraints usually guarantee
// #   `times[0] ≤ t`; if not, define behavior (bisect index −1 — avoid by constraint).
// # • **Query `t` after last vote** — bisect returns last index; leader is final winner.
// #
// # =============================================================================
// # TESTING (UNIT / PROPERTY)
// # =============================================================================
// #
// # • Match brute force for random small instances: for each `t`, recount votes with
// #   `time ≤ t`, resolve ties by scanning votes in order for max frequency then last
// #   occurrence among tied maxima — compare to `q(t)`.
// # • Known samples from statement (if provided): replay timeline.
// #
// # =============================================================================
// # IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # • If **many queries** and **discrete small time universe**, **bucket** answers by
// #   time — rarely needed; binary search is standard.
// # • **Persistence:** snapshots are already an implicit persistent prefix structure.
// #
// # =============================================================================
// 
// # @lc code=start
// import bisect
// from typing import Dict, List
// 
// 
// class TopVotedCandidate:
//     """
//     Precomputes the election winner after each recorded vote, then answers
//     time-queries via binary search on vote timestamps.
//     """
// 
//     def __init__(self, persons: List[int], times: List[int]):
//         """
//         :param persons: persons[i] receives one vote at times[i]; times strictly increases.
//         :param times: parallel timestamps (sorted ascending).
//         """
//         self.times = times
//         n = len(times)
//         cnt: Dict[int, int] = {}
//         leader = persons[0]
//         cnt[leader] = 1
//         leaders = [leader]
// 
//         for i in range(1, n):
//             p = persons[i]
//             cnt[p] = cnt.get(p, 0) + 1
//             if cnt[p] >= cnt[leader]:
//                 leader = p
//             leaders.append(leader)
// 
//         self.leaders = leaders
// 
//     def q(self, t: int) -> int:
//         """Return winning candidate among all votes cast at time <= t."""
//         # Largest index i with times[i] <= t  ==  bisect_right - 1
//         i = bisect.bisect_right(self.times, t) - 1
//         return self.leaders[i]
// 
// 
// # Your TopVotedCandidate object will be instantiated and called as such:
// # obj = TopVotedCandidate(persons, times)
// # param_1 = obj.q(t)
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

class TopVotedCandidate {
    vector<int> times, leaders;
public:
    TopVotedCandidate(vector<int>& persons, vector<int>& times) : times(times) {
        unordered_map<int, int> cnt;
        int leader = persons[0];
        cnt[leader] = 1;
        leaders.push_back(leader);
        for (int i = 1; i < (int)persons.size(); ++i) {
            int p = persons[i];
            if (++cnt[p] >= cnt[leader]) leader = p;
            leaders.push_back(leader);
        }
    }

    int q(int t) {
        int i = upper_bound(times.begin(), times.end(), t) - times.begin() - 1;
        return leaders[i];
    }
};
