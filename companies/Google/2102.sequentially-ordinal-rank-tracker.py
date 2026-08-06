#
# @lc app=leetcode id=2102 lang=python3
#
# [2102] Sequentially Ordinal Rank Tracker
#
# https://leetcode.com/problems/sequentially-ordinal-rank-tracker/description/
#
# algorithms
# Hard (61.32%)
# Likes:    410
# Dislikes: 48
# Total Accepted:    20.9K
# Total Submissions: 34.1K
# Testcase Example:  "[\"SORTracker\",\"add\",\"add\",\"get\",\"add\",\"get\",\"add\",\"get\",\"add\",\"get\",\"add\",\"get\",\"get\"]\n[[],[\"bradford\",2],[\"branford\",3],[],[\"alps\",2],[],[\"orland\",2],[],[\"orlando\",3],[],[\"alpine\",2],[],[]]"
#
# A scenic location is represented by its name and attractiveness score, where
# name is a unique string among all locations and score is an integer. Locations
# can be ranked from the best to the worst. The higher the score, the better the
# location. If the scores of two locations are equal, then the location with the
# lexicographically smaller name is better.
#
# You are building a system that tracks the ranking of locations with the system
# initially starting with no locations. It supports:
#
#
# Adding scenic locations, one at a time.
#
#
# Querying the i^th best location of all locations already added, where i is the
# number of times the system has been queried (including the current query).
#
#
#
# For example, when the system is queried for the 4^th time, it returns the 4^th
# best location of all locations already added.
#
#
#
#
#
# Note that the test data are generated so that at any time, the number of
# queries does not exceed the number of locations added to the system.
#
# Implement the SORTracker class:
#
#
# SORTracker() Initializes the tracker system.
#
#
# void add(string name, int score) Adds a scenic location with name and score to
# the system.
#
#
# string get() Queries and returns the i^th best location, where i is the number
# of times this method has been invoked (including this invocation).
#
#
#
# Example 1:
#
# Input
# ["SORTracker", "add", "add", "get", "add", "get", "add", "get", "add", "get",
# "add", "get", "get"]
# [[], ["bradford", 2], ["branford", 3], [], ["alps", 2], [], ["orland", 2], [],
# ["orlando", 3], [], ["alpine", 2], [], []]
# Output
# [null, null, null, "branford", null, "alps", null, "bradford", null,
# "bradford", null, "bradford", "orland"]
#
# Explanation
# SORTracker tracker = new SORTracker(); // Initialize the tracker system.
# tracker.add("bradford", 2); // Add location with name="bradford" and score=2
# to the system.
# tracker.add("branford", 3); // Add location with name="branford" and score=3
# to the system.
# tracker.get();              // The sorted locations, from best to worst, are:
# branford, bradford.
#                             // Note that branford precedes bradford due to its
# higher score (3 > 2).
#                             // This is the 1^st time get() is called, so
# return the best location: "branford".
# tracker.add("alps", 2);     // Add location with name="alps" and score=2 to
# the system.
# tracker.get();              // Sorted locations: branford, alps, bradford.
#                             // Note that alps precedes bradford even though
# they have the same score (2).
#                             // This is because "alps" is lexicographically
# smaller than "bradford".
#                             // Return the 2^nd best location "alps", as it is
# the 2^nd time get() is called.
# tracker.add("orland", 2);   // Add location with name="orland" and score=2 to
# the system.
# tracker.get();              // Sorted locations: branford, alps, bradford,
# orland.
#                             // Return "bradford", as it is the 3^rd time get()
# is called.
# tracker.add("orlando", 3);  // Add location with name="orlando" and score=3 to
# the system.
# tracker.get();              // Sorted locations: branford, orlando, alps,
# bradford, orland.
#                             // Return "bradford".
# tracker.add("alpine", 2);   // Add location with name="alpine" and score=2 to
# the system.
# tracker.get();              // Sorted locations: branford, orlando, alpine,
# alps, bradford, orland.
#                             // Return "bradford".
# tracker.get();              // Sorted locations: branford, orlando, alpine,
# alps, bradford, orland.
#                             // Return "orland".
#
#
#
# Constraints:
#
#
# name consists of lowercase English letters, and is unique among all locations.
#
#
# 1 <= name.length <= 10
#
#
# 1 <= score <= 10^5
#
#
# At any time, the number of calls to get does not exceed the number of calls to
# add.
#
#
# At most 4 * 10^4 calls in total will be made to add and get.
#



# @lc code=start
import heapq


class SORTracker:
    def __init__(self):
        """
        Interview explanation:
        Design: add (name, score) locations; the ith call to get() returns the
        ith best location (higher score first; ties broken by name ascending).

        Algorithm:
        - key = (-score, name) — smaller is better.
        - left: max-heap of the first k best (k = #get calls), top = kth best.
        - right: min-heap of remaining locations.
        - Max-heap of keys via storing (score, inv(name), name).

        Complexity: O(log n) per add/get, O(n) space.
        """
        self.left = []
        self.right = []
        self.k = 0

    @staticmethod
    def _inv(s: str) -> str:
        return ''.join(chr(255 - ord(c)) for c in s)

    def _push_left(self, key) -> None:
        neg_score, name = key
        heapq.heappush(self.left, (-neg_score, self._inv(name), name))

    def _peek_left_key(self):
        score, _, name = self.left[0]
        return (-score, name)

    def _pop_left_key(self):
        score, _, name = heapq.heappop(self.left)
        return (-score, name)

    def add(self, name: str, score: int) -> None:
        """
        Interview explanation:
        Insert a location and keep left as exactly the first k best.

        Algorithm:
        - If k==0, push to right.
        - Else if new key is better than left's worst, displace worst to right;
          otherwise push to right.

        Complexity: O(log n).
        """
        key = (-score, name)
        if self.k == 0:
            heapq.heappush(self.right, key)
            return
        if key < self._peek_left_key():
            heapq.heappush(self.right, self._pop_left_key())
            self._push_left(key)
        else:
            heapq.heappush(self.right, key)

    def get(self) -> str:
        """
        Interview explanation:
        Return the next ordinal best name (1st, 2nd, 3rd, ... across calls).

        Algorithm:
        - k += 1; move the best from right into left; return left's worst name
          (the kth best overall).

        Complexity: O(log n).
        """
        self.k += 1
        self._push_left(heapq.heappop(self.right))
        return self._peek_left_key()[1]


# Your SORTracker object will be instantiated and called as such:
# obj = SORTracker()
# obj.add(name,score)
# param_2 = obj.get()
# @lc code=end


