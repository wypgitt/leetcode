#
# @lc app=leetcode id=2241 lang=python3
#
# [2241] Design an ATM Machine
#
# https://leetcode.com/problems/design-an-atm-machine/description/
#
# algorithms
# Medium (45.82%)
# Likes:    315
# Dislikes: 387
# Total Accepted:    38.6K
# Total Submissions: 84.3K
# Testcase Example:  "[\"ATM\",\"deposit\",\"withdraw\",\"deposit\",\"withdraw\",\"withdraw\"]\n[[],[[0,0,1,2,1]],[600],[[0,1,0,1,1]],[600],[550]]"
#
# There is an ATM machine that stores banknotes of 5 denominations: 20, 50, 100,
# 200, and 500 dollars. Initially the ATM is empty. The user can use the machine
# to deposit or withdraw any amount of money.
#
# When withdrawing, the machine prioritizes using banknotes of larger values.
#
#
# For example, if you want to withdraw $300 and there are 2 $50 banknotes, 1
# $100 banknote, and 1 $200 banknote, then the machine will use the $100 and
# $200 banknotes.
#
#
# However, if you try to withdraw $600 and there are 3 $200 banknotes and 1 $500
# banknote, then the withdraw request will be rejected because the machine will
# first try to use the $500 banknote and then be unable to use banknotes to
# complete the remaining $100. Note that the machine is not allowed to use the
# $200 banknotes instead of the $500 banknote.
#
# Implement the ATM class:
#
#
# ATM() Initializes the ATM object.
#
#
# void deposit(int[] banknotesCount) Deposits new banknotes in the order $20,
# $50, $100, $200, and $500.
#
#
# int[] withdraw(int amount) Returns an array of length 5 of the number of
# banknotes that will be handed to the user in the order $20, $50, $100, $200,
# and $500, and update the number of banknotes in the ATM after withdrawing.
# Returns [-1] if it is not possible (do not withdraw any banknotes in this
# case).
#
#
#
# Example 1:
#
# Input
# ["ATM", "deposit", "withdraw", "deposit", "withdraw", "withdraw"]
# [[], [[0,0,1,2,1]], [600], [[0,1,0,1,1]], [600], [550]]
# Output
# [null, null, [0,0,1,0,1], null, [-1], [0,1,0,0,1]]
#
# Explanation
# ATM atm = new ATM();
# atm.deposit([0,0,1,2,1]); // Deposits 1 $100 banknote, 2 $200 banknotes,
#                           // and 1 $500 banknote.
# atm.withdraw(600);        // Returns [0,0,1,0,1]. The machine uses 1 $100
# banknote
#                           // and 1 $500 banknote. The banknotes left over in
# the
#                           // machine are [0,0,0,2,0].
# atm.deposit([0,1,0,1,1]); // Deposits 1 $50, $200, and $500 banknote.
#                           // The banknotes in the machine are now [0,1,0,3,1].
# atm.withdraw(600);        // Returns [-1]. The machine will try to use a $500
# banknote
#                           // and then be unable to complete the remaining
# $100,
#                           // so the withdraw request will be rejected.
#                           // Since the request is rejected, the number of
# banknotes
#                           // in the machine is not modified.
# atm.withdraw(550);        // Returns [0,1,0,0,1]. The machine uses 1 $50
# banknote
#                           // and 1 $500 banknote.
#
#
#
# Constraints:
#
#
# banknotesCount.length == 5
#
#
# 0 <= banknotesCount[i] <= 10^9
#
#
# 1 <= amount <= 10^9
#
#
# At most 5000 calls in total will be made to withdraw and deposit.
#
#
# At least one call will be made to each function withdraw and deposit.
#
#
# Sum of banknotesCount[i] in all deposits doesn't exceed 10^9
#

# @lc code=start
from typing import List


class ATM:
    def __init__(self):
        """
        Interview explanation:
        ATM holds notes of $20,$50,$100,$200,$500. Support deposit and greedy
        withdraw of largest notes first; fail entirely if cannot make exact amount
        with available notes.

        Algorithm:
        - Store counts[5]; deposit add; withdraw try from largest denomination.

        Complexity: init O(1).
        """
        self.denoms = [20, 50, 100, 200, 500]
        self.cnt = [0] * 5

    def deposit(self, banknotesCount: List[int]) -> None:
        """
        Interview explanation:
        Add banknotesCount[i] notes of denomination i to the machine.

        Algorithm:
        - Element-wise add to counts.

        Complexity: O(1) time, O(1) space.
        """
        for i in range(5):
            self.cnt[i] += banknotesCount[i]

    def withdraw(self, amount: int) -> List[int]:
        """
        Interview explanation:
        Greedy largest-first withdraw; if impossible return [-1] and leave machine
        unchanged; else deduct and return notes used per denomination.

        Algorithm:
        - From 500 down to 20, take min(available, amount//denom); verify remainder 0.

        Complexity: O(1) time, O(1) space.
        """
        take = [0] * 5
        remain = amount
        for i in range(4, -1, -1):
            use = min(self.cnt[i], remain // self.denoms[i])
            take[i] = use
            remain -= use * self.denoms[i]
        if remain != 0:
            return [-1]
        for i in range(5):
            self.cnt[i] -= take[i]
        return take
# @lc code=end
