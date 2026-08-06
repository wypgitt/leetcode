#
# @lc app=leetcode id=1117 lang=python3
#
# [1117] Building H2O
#
# https://leetcode.com/problems/building-h2o/description/
#
# algorithms
# Medium (58.45%)
# Likes:    592
# Dislikes: 201
# Total Accepted:    93.3K
# Total Submissions: 160K
# Testcase Example:  "\"HOH\""
#
# There are two kinds of threads: oxygen and hydrogen. Your goal is to group
# these threads to form water molecules.
#
# There is a barrier where each thread has to wait until a complete molecule
# can be formed. Hydrogen and oxygen threads will be given releaseHydrogen and
# releaseOxygen methods respectively, which will allow them to pass the
# barrier. These threads should pass the barrier in groups of three, and they
# must immediately bond with each other to form a water molecule. You must
# guarantee that all the threads from one molecule bond before any other
# threads from the next molecule do.
#
# In other words:
#
# If an oxygen thread arrives at the barrier when no hydrogen threads are
# present, it must wait for two hydrogen threads.
#
# If a hydrogen thread arrives at the barrier when no other threads are
# present, it must wait for an oxygen thread and another hydrogen thread.
#
# We do not have to worry about matching the threads up explicitly; the threads
# do not necessarily know which other threads they are paired up with. The key
# is that threads pass the barriers in complete sets; thus, if we examine the
# sequence of threads that bind and divide them into groups of three, each
# group should contain one oxygen and two hydrogen threads.
#
# Write synchronization code for oxygen and hydrogen molecules that enforces
# these constraints.
#
# Example 1:
#
# Input: water = "HOH"
# Output: "HHO"
# Explanation: "HOH" and "OHH" are also valid answers.
#
# Example 2:
#
# Input: water = "OOHHHH"
# Output: "HHOHHO"
# Explanation: "HOHHHO", "OHHHHO", "HHOHOH", "HOHHOH", "OHHHOH", "HHOOHH",
# "HOHOHH" and "OHHOHH" are also valid answers.
#
# Constraints:
#
# 3 * n == water.length
#
# 1 <= n <= 20
#
# water[i] is either 'H' or 'O'.
#
# There will be exactly 2 * n 'H' in water.
#
# There will be exactly n 'O' in water.
#

# @lc code=start
import threading
from typing import Callable


class H2O:
    def __init__(self):
        """
        Interview explanation:
        Form molecules of 2H + 1O. Limit concurrent H/O with semaphores and
        synchronize the trio with a Barrier so all three bond before the next
        molecule starts.

        Algorithm (Semaphore + Barrier):
        - h_sem permits 2 hydrogens; o_sem permits 1 oxygen per molecule.
        - Each atom acquires its semaphore, barrier.wait() with 3 parties,
          then release*(), then release the semaphore for the next molecule.

        Complexity: O(1) per atom.
        """
        self.h_sem = threading.Semaphore(2)
        self.o_sem = threading.Semaphore(1)
        self.barrier = threading.Barrier(3)

    def hydrogen(self, releaseHydrogen: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Participate as one of two H atoms in the next water molecule.

        Algorithm:
        - h_sem.acquire(); barrier.wait(); releaseHydrogen(); h_sem.release().

        Complexity: O(1).
        """
        self.h_sem.acquire()
        self.barrier.wait()
        releaseHydrogen()
        self.h_sem.release()

    def oxygen(self, releaseOxygen: "Callable[[], None]") -> None:
        """
        Interview explanation:
        Participate as the O atom in the next water molecule.

        Algorithm:
        - o_sem.acquire(); barrier.wait(); releaseOxygen(); o_sem.release().

        Complexity: O(1).
        """
        self.o_sem.acquire()
        self.barrier.wait()
        releaseOxygen()
        self.o_sem.release()
# @lc code=end
