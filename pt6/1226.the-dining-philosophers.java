import java.util.concurrent.Semaphore;

class DiningPhilosophers {
    private final Semaphore[] forks = new Semaphore[5];

    public DiningPhilosophers() {
        for (int i = 0; i < 5; i++) {
            forks[i] = new Semaphore(1);
        }
    }

    public void wantsToEat(
            int philosopher,
            Runnable pickLeftFork,
            Runnable pickRightFork,
            Runnable eat,
            Runnable putLeftFork,
            Runnable putRightFork) throws InterruptedException {

        int left = philosopher;
        int right = (philosopher + 1) % 5;

        int first = Math.min(left, right);
        int second = Math.max(left, right);

        forks[first].acquire();
        if (first == left) {
            pickLeftFork.run();
        } else {
            pickRightFork.run();
        }

        forks[second].acquire();
        if (second == left) {
            pickLeftFork.run();
        } else {
            pickRightFork.run();
        }

        eat.run();

        if (second == left) {
            putLeftFork.run();
        } else {
            putRightFork.run();
        }
        forks[second].release();

        if (first == left) {
            putLeftFork.run();
        } else {
            putRightFork.run();
        }
        forks[first].release();
    }
}

/*
Explanation

Each fork is a binary Semaphore. To avoid deadlock, every philosopher acquires
forks in the same global order: lower-numbered fork first, then higher-numbered
fork. Philosopher 4 naturally picks fork 0 before fork 4.

The concurrency invariant is that circular wait cannot form. No thread holds a
higher-numbered fork while waiting for a lower-numbered fork.

The callbacks run while the corresponding fork is held: pick both forks, eat,
put both forks down, release both semaphores.

Edge cases: all five philosophers call concurrently; repeated calls by the
same philosopher; each fork remains protected independently.

Time complexity per call: O(1).
Space complexity: O(1), five semaphores.
*/
