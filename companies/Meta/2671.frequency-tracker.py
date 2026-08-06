#
# @lc app=leetcode id=2671 lang=python3
#
# [2671] Frequency Tracker
#
# https://leetcode.com/problems/frequency-tracker/description/
#
# algorithms
# Medium (31.47%)
# Likes:    347
# Dislikes: 31
# Total Accepted:    30.3K
# Total Submissions: 96.2K
# Testcase Example:  "[\"FrequencyTracker\",\"add\",\"add\",\"hasFrequency\"]\n[[],[3],[3],[2]]"
#
# Design a data structure that keeps track of the values in it and answers some
# queries regarding their frequencies.
#
# Implement the FrequencyTracker class.
#
#
# FrequencyTracker(): Initializes the FrequencyTracker object with an empty
# array initially.
#
#
# void add(int number): Adds number to the data structure.
#
#
# void deleteOne(int number): Deletes one occurrence of number from the data
# structure. The data structure may not contain number, and in this case nothing
# is deleted.
#
#
# bool hasFrequency(int frequency): Returns true if there is a number in the
# data structure that occurs frequency number of times, otherwise, it returns
# false.
#
#
#
# Example 1:
#
# Input
# ["FrequencyTracker", "add", "add", "hasFrequency"]
# [[], [3], [3], [2]]
# Output
# [null, null, null, true]
#
# Explanation
# FrequencyTracker frequencyTracker = new FrequencyTracker();
# frequencyTracker.add(3); // The data structure now contains [3]
# frequencyTracker.add(3); // The data structure now contains [3, 3]
# frequencyTracker.hasFrequency(2); // Returns true, because 3 occurs twice
#
# Example 2:
#
# Input
# ["FrequencyTracker", "add", "deleteOne", "hasFrequency"]
# [[], [1], [1], [1]]
# Output
# [null, null, null, false]
#
# Explanation
# FrequencyTracker frequencyTracker = new FrequencyTracker();
# frequencyTracker.add(1); // The data structure now contains [1]
# frequencyTracker.deleteOne(1); // The data structure becomes empty []
# frequencyTracker.hasFrequency(1); // Returns false, because the data structure
# is empty
#
# Example 3:
#
# Input
# ["FrequencyTracker", "hasFrequency", "add", "hasFrequency"]
# [[], [2], [3], [1]]
# Output
# [null, false, null, true]
#
# Explanation
# FrequencyTracker frequencyTracker = new FrequencyTracker();
# frequencyTracker.hasFrequency(2); // Returns false, because the data structure
# is empty
# frequencyTracker.add(3); // The data structure now contains [3]
# frequencyTracker.hasFrequency(1); // Returns true, because 3 occurs once
#
#
#
# Constraints:
#
#
# 1 <= number <= 10^5
#
#
# 1 <= frequency <= 10^5
#
#
# At most, 2 * 10^5 calls will be made to add, deleteOne, and hasFrequency in
# total.
#

# @lc code=start

from collections import defaultdict


class FrequencyTracker:
    def __init__(self):
        """
        Interview explanation:
        Design: track multiset of numbers; support add, deleteOne, and query whether any number
        currently has a given frequency.

        Algorithm:
        - freq[num] and count_of_freq[f]; update both on add/delete.

        Complexity: init O(1).
        """
        self.freq = defaultdict(int)
        self.freq_cnt = defaultdict(int)

    def add(self, number: int) -> None:
        """
        Interview explanation:
        Insert one occurrence of number.

        Algorithm:
        - Decrement old frequency bucket; increment new; bump freq[number].

        Complexity: O(1) amortized.
        """
        f = self.freq[number]
        if f > 0:
            self.freq_cnt[f] -= 1
        self.freq[number] = f + 1
        self.freq_cnt[f + 1] += 1

    def deleteOne(self, number: int) -> None:
        """
        Interview explanation:
        Delete one occurrence of number if present (no-op otherwise).

        Algorithm:
        - If freq>0, move from bucket f to f-1.

        Complexity: O(1) amortized.
        """
        f = self.freq[number]
        if f == 0:
            return
        self.freq_cnt[f] -= 1
        self.freq[number] = f - 1
        if f - 1 > 0:
            self.freq_cnt[f - 1] += 1

    def hasFrequency(self, frequency: int) -> bool:
        """
        Interview explanation:
        Return whether any number currently appears exactly `frequency` times.

        Algorithm:
        - Check freq_cnt[frequency] > 0.

        Complexity: O(1).
        """
        return self.freq_cnt[frequency] > 0
# @lc code=end
