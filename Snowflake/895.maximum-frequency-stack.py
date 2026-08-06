#
# @lc app=leetcode id=895 lang=python3
#
# [895] Maximum Frequency Stack
#
# https://leetcode.com/problems/maximum-frequency-stack/description/
#
# algorithms
# Hard (67.0%)
# Likes:    4993
# Dislikes: 79
# Total Accepted:    237K
# Total Submissions: 353K
# Testcase Example:  "[\"FreqStack\",\"push\",\"push\",\"push\",\"push\",\"push\",\"push\",\"pop\",\"pop\",\"pop\",\"pop\"]"
#
# Design a stack-like data structure to push elements to the stack and pop the
# most frequent element from the stack.
#
# Implement the FreqStack class:
#
# FreqStack() constructs an empty frequency stack.
#
# void push(int val) pushes an integer val onto the top of the stack.
#
# int pop() removes and returns the most frequent element in the stack.
#
# If there is a tie for the most frequent element, the element closest to the
# stack's top is removed and returned.
#
# Example 1:
#
# Input
# ["FreqStack", "push", "push", "push", "push", "push", "push", "pop", "pop",
# "pop", "pop"]
# [[], [5], [7], [5], [7], [4], [5], [], [], [], []]
# Output
# [null, null, null, null, null, null, null, 5, 7, 5, 4]
#
# Explanation
# FreqStack freqStack = new FreqStack();
# freqStack.push(5); // The stack is [5]
# freqStack.push(7); // The stack is [5,7]
# freqStack.push(5); // The stack is [5,7,5]
# freqStack.push(7); // The stack is [5,7,5,7]
# freqStack.push(4); // The stack is [5,7,5,7,4]
# freqStack.push(5); // The stack is [5,7,5,7,4,5]
# freqStack.pop(); // return 5, as 5 is the most frequent. The stack becomes
# [5,7,5,7,4].
# freqStack.pop(); // return 7, as 5 and 7 is the most frequent, but 7 is
# closest to the top. The stack becomes [5,7,5,4].
# freqStack.pop(); // return 5, as 5 is the most frequent. The stack becomes
# [5,7,4].
# freqStack.pop(); // return 4, as 4, 5 and 7 is the most frequent, but 4 is
# closest to the top. The stack becomes [5,7].
#
# Constraints:
#
# 0 <= val <= 10^9
#
# At most 2 * 10^4 calls will be made to push and pop.
#
# It is guaranteed that there will be at least one element in the stack before
# calling pop.
#

# @lc code=start
from collections import defaultdict


class FreqStack:
    def __init__(self):
        """
        Interview explanation:
        Stack that pops the most frequent element (ties → most recent). Keep
        freq map and stacks grouped by frequency; track maxfreq.

        Algorithm:
        - freq[x], group[f] = stack of vals with that freq; maxfreq.

        Complexity: O(1) init.
        """
        self.freq = defaultdict(int)
        self.group = defaultdict(list)
        self.maxfreq = 0

    def push(self, val: int) -> None:
        """
        Interview explanation:
        Increment val's frequency and push onto that frequency's stack.

        Algorithm:
        - freq[val]+=1; group[freq].append(val); update maxfreq.

        Complexity: O(1) amortized.
        """
        f = self.freq[val] + 1
        self.freq[val] = f
        if f > self.maxfreq:
            self.maxfreq = f
        self.group[f].append(val)

    def pop(self) -> int:
        """
        Interview explanation:
        Pop from maxfreq stack; decrement freq; shrink maxfreq if empty.

        Algorithm:
        - x=group[maxfreq].pop(); freq[x]--; if group empty maxfreq--.

        Complexity: O(1) amortized.
        """
        x = self.group[self.maxfreq].pop()
        self.freq[x] -= 1
        if not self.group[self.maxfreq]:
            self.maxfreq -= 1
        return x


# Your FreqStack object will be instantiated and called as such:
# obj = FreqStack()
# obj.push(val)
# param_2 = obj.pop()
# @lc code=end

