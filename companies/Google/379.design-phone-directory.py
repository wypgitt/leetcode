#
# @lc app=leetcode id=379 lang=python3
#
# [379] Design Phone Directory
#
# https://leetcode.com/problems/design-phone-directory/description/
#
# algorithms
# Medium (53.21%)
# Likes:    369
# Dislikes: 486
# Total Accepted:    77.6K
# Total Submissions: 145.9K
# Testcase Example:  "[\"PhoneDirectory\",\"get\",\"get\",\"check\",\"get\",\"check\",\"release\",\"check\"]\n[[3],[],[],[2],[],[2],[2],[2]]"
#
#
# Design a phone directory that initially has maxNumbers empty slots that
# can store numbers. The directory should store numbers, check if a
# certain slot is empty or not, and empty a given slot.
#
# Implement the PhoneDirectory class:
#
# PhoneDirectory(int maxNumbers) Initializes the phone directory with the
# number of available slots maxNumbers.
#
# int get() Provides a number that is not assigned to anyone. Returns -1
# if no number is available.
#
# bool check(int number) Returns true if the slot number is available and
# false otherwise.
#
# void release(int number) Recycles or releases the slot number.
#
# Example 1:
#
# Input
# ["PhoneDirectory", "get", "get", "check", "get", "check", "release",
# "check"]
# [[3], [], [], [2], [], [2], [2], [2]]
# Output
# [null, 0, 1, true, 2, false, null, true]
#
# Explanation
# PhoneDirectory phoneDirectory = new PhoneDirectory(3);
# phoneDirectory.get();      // It can return any available phone number.
# Here we assume it returns 0.
# phoneDirectory.get();      // Assume it returns 1.
# phoneDirectory.check(2);   // The number 2 is available, so return true.
# phoneDirectory.get();      // It returns 2, the only number that is
# left.
# phoneDirectory.check(2);   // The number 2 is no longer available, so
# return false.
# phoneDirectory.release(2); // Release number 2 back to the pool.
# phoneDirectory.check(2);   // Number 2 is available again, return true.
#
# Constraints:
#
# 1 <= maxNumbers <= 10^4
#
# 0 <= number < maxNumbers
#
# At most 2 * 10^4 calls will be made to get, check, and release.
#
# @lc code=start
from collections import deque


class PhoneDirectory:
    """
    Interview explanation:
    Premium design: allocate/release phone numbers in [0, maxNumbers).
    Maintain available numbers in a queue (or set) for O(1) get/release/check.

    Algorithm:
    - __init__: enqueue 0..maxNumbers-1; track available set for O(1) check.
    - get: popleft if any, else -1; remove from set.
    - check: number in available set.
    - release: if not available, add back to set and queue.

    Complexity: O(1) amortized per op, O(maxNumbers) space.
    """

    def __init__(self, maxNumbers: int):
        """
        Interview explanation:
        Preload numbers [0, maxNumbers) into a free queue and an available set
        for O(1) allocate/check/release.

        Algorithm:
        - available = set(range(max)); free = deque(range(max)).

        Complexity: O(maxNumbers) time and space.
        """
        self.available = set(range(maxNumbers))
        self.free = deque(range(maxNumbers))

    def get(self) -> int:
        """
        Interview explanation:
        Allocate the next free number, or -1 if none remain.

        Algorithm:
        - If free empty return -1; else popleft, remove from available, return.

        Complexity: O(1) time, O(1) space.
        """
        if not self.free:
            return -1
        num = self.free.popleft()
        self.available.discard(num)
        return num

    def check(self, number: int) -> bool:
        """
        Interview explanation:
        True iff number is currently unallocated.

        Algorithm:
        - Return number in available.

        Complexity: O(1) time, O(1) space.
        """
        return number in self.available

    def release(self, number: int) -> None:
        """
        Interview explanation:
        Return a number to the pool only if it is not already free (idempotent).

        Algorithm:
        - If not in available: add to set and append to free queue.

        Complexity: O(1) time, O(1) space.
        """
        if number not in self.available:
            self.available.add(number)
            self.free.append(number)


# Your PhoneDirectory object will be instantiated and called as such:
# obj = PhoneDirectory(maxNumbers)
# param_1 = obj.get()
# param_2 = obj.check(number)
# obj.release(number)
# @lc code=end
