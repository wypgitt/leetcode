package main

import "sync"

type DiningPhilosophers struct {
	forks [5]sync.Mutex
}

func Constructor() DiningPhilosophers {
	return DiningPhilosophers{}
}

func (d *DiningPhilosophers) WantsToEat(
	philosopher int,
	pickLeftFork func(),
	pickRightFork func(),
	eat func(),
	putLeftFork func(),
	putRightFork func(),
) {
	left, right := philosopher, (philosopher+1)%5

	firstFork, secondFork := left, right
	firstPick, secondPick := pickLeftFork, pickRightFork
	firstPut, secondPut := putLeftFork, putRightFork
	if right < left {
		firstFork, secondFork = right, left
		firstPick, secondPick = pickRightFork, pickLeftFork
		firstPut, secondPut = putRightFork, putLeftFork
	}

	d.forks[firstFork].Lock()
	firstPick()
	d.forks[secondFork].Lock()
	secondPick()

	eat()

	secondPut()
	d.forks[secondFork].Unlock()
	firstPut()
	d.forks[firstFork].Unlock()
}

/*
Explanation

Each fork is a sync.Mutex. To avoid deadlock, every philosopher acquires forks
in the same global order: lower fork number first, higher fork number second.
Philosopher 4 is the only one whose right fork has the smaller number, so that
philosopher picks the right fork first.

The important concurrency invariant is that a circular wait cannot form. No
goroutine can hold a higher-numbered fork while waiting for a lower-numbered
fork, because the code always locks the lower one first.

Callbacks are invoked while the matching fork locks are held: pick both forks,
eat, put both forks down, unlock. The problem allows either fork to be picked
first as long as eating happens only with both forks held.

Edge cases: all five philosophers call concurrently; the same philosopher can
call multiple times; each fork remains protected by exactly one mutex.

Time complexity per call: O(1).
Space complexity: O(1), five mutexes.
*/
