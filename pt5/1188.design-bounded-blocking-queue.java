import java.util.*;
import java.util.concurrent.Semaphore;
import java.util.concurrent.locks.ReentrantLock;

class BoundedBlockingQueue {
    private final int capacity;
    private final Deque<Integer> queue = new ArrayDeque<>();
    private final Semaphore emptySlots;
    private final Semaphore availableItems = new Semaphore(0);
    private final ReentrantLock lock = new ReentrantLock();

    public BoundedBlockingQueue(int capacity) {
        this.capacity = capacity;
        this.emptySlots = new Semaphore(capacity);
    }

    public void enqueue(int element) throws InterruptedException {
        emptySlots.acquire();
        lock.lock();
        try {
            queue.addFirst(element);
        } finally {
            lock.unlock();
        }
        availableItems.release();
    }

    public int dequeue() throws InterruptedException {
        availableItems.acquire();
        lock.lock();
        try {
            return queue.removeLast();
        } finally {
            lock.unlock();
            emptySlots.release();
        }
    }

    public int size() {
        lock.lock();
        try {
            return queue.size();
        } finally {
            lock.unlock();
        }
    }
}

