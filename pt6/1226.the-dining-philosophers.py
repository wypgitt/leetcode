#
# @lc app=leetcode id=1226 lang=python3
#
# [1226] The Dining Philosophers
#
# https://leetcode.com/problems/the-dining-philosophers/description/
#
# concurrency
# Medium (53.61%)
# Likes:    411
# Dislikes: 374
# Total Accepted:    56.9K
# Total Submissions: 106.1K
# Testcase Example:  '1'
#
# Five silent philosophers sit at a round table with bowls of spaghetti. Forks
# are placed between each pair of adjacent philosophers.
# 
# Each philosopher must alternately think and eat. However, a philosopher can
# only eat spaghetti when they have both left and right forks. Each fork can be
# held by only one philosopher and so a philosopher can use the fork only if it
# is not being used by another philosopher. After an individual philosopher
# finishes eating, they need to put down both forks so that the forks become
# available to others. A philosopher can take the fork on their right or the
# one on their left as they become available, but cannot start eating before
# getting both forks.
# 
# Eating is not limited by the remaining amounts of spaghetti or stomach space;
# an infinite supply and an infinite demand are assumed.
# 
# Design a discipline of behaviour (a concurrent algorithm) such that no
# philosopher will starve; i.e., each can forever continue to alternate between
# eating and thinking, assuming that no philosopher can know when others may
# want to eat or think.
# 
# 
# 
# The problem statement and the image above are taken from wikipedia.org
# 
# 
# 
# The philosophers' ids are numbered from 0 to 4 in a clockwise order.
# Implement the function void wantsToEat(philosopher, pickLeftFork,
# pickRightFork, eat, putLeftFork, putRightFork) where:
# 
# 
# philosopher is the id of the philosopher who wants to eat.
# pickLeftFork and pickRightFork are functions you can call to pick the
# corresponding forks of that philosopher.
# eat is a function you can call to let the philosopher eat once he has picked
# both forks.
# putLeftFork and putRightFork are functions you can call to put down the
# corresponding forks of that philosopher.
# The philosophers are assumed to be thinking as long as they are not asking to
# eat (the function is not being called with their number).
# 
# 
# Five threads, each representing a philosopher, will simultaneously use one
# object of your class to simulate the process. The function may be called for
# the same philosopher more than once, even before the last call ends.
# 
# 
# Example 1:
# 
# 
# Input: n = 1
# Output:
# [[3,2,1],[3,1,1],[3,0,3],[3,1,2],[3,2,2],[4,2,1],[4,1,1],[2,2,1],[2,1,1],[1,2,1],[2,0,3],[2,1,2],[2,2,2],[4,0,3],[4,1,2],[4,2,2],[1,1,1],[1,0,3],[1,1,2],[1,2,2],[0,1,1],[0,2,1],[0,0,3],[0,1,2],[0,2,2]]
# Explanation:
# n is the number of times each philosopher will call the function.
# The output array describes the calls you made to the functions controlling
# the forks and the eat function, its format is:
# output[i] = [a, b, c] (three integers)
# - a is the id of a philosopher.
# - b specifies the fork: {1 : left, 2 : right}.
# - c specifies the operation: {1 : pick, 2 : put, 3 : eat}.
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 60
# 
# 
#

# @lc code=start
import threading


class DiningPhilosophers:
    def __init__(self):
        self.forks = [threading.Lock() for _ in range(5)]

    # call the functions directly to execute, for example, eat()
    def wantsToEat(self,
                   philosopher: int,
                   pickLeftFork: 'Callable[[], None]',
                   pickRightFork: 'Callable[[], None]',
                   eat: 'Callable[[], None]',
                   putLeftFork: 'Callable[[], None]',
                   putRightFork: 'Callable[[], None]') -> None:
        left = philosopher
        right = (philosopher + 1) % 5

        if left < right:
            first_lock, first_pick, first_put = self.forks[left], pickLeftFork, putLeftFork
            second_lock, second_pick, second_put = self.forks[right], pickRightFork, putRightFork
        else:
            first_lock, first_pick, first_put = self.forks[right], pickRightFork, putRightFork
            second_lock, second_pick, second_put = self.forks[left], pickLeftFork, putLeftFork

        with first_lock:
            first_pick()
            with second_lock:
                second_pick()
                eat()
                second_put()
            first_put()
# @lc code=end

# Explanation
# -----------
# Each fork is represented by a lock. To avoid deadlock, philosophers acquire
# locks in a global order: the lower-numbered fork first, then the
# higher-numbered fork. Philosopher 4 is the special case where the right fork
# is 0, so that philosopher picks the right fork first.
#
# The important invariant is that no cycle of waiting can form. If everyone
# follows the same fork ordering, a thread holding a higher fork while waiting
# for a lower fork cannot exist.
#
# The callbacks are called while the corresponding locks are held: pick both
# forks, eat, then put them down. The actual callback order may differ for
# philosopher 4, which is allowed by the problem.
#
# Edge cases: simultaneous calls for all five philosophers; repeated calls by
# the same philosopher; the implementation still serializes access to each
# fork correctly.
#
# Time complexity per call: O(1). Space complexity: O(1), five locks.
