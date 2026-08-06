/**
 * Algorithm:
 * Use a fixed-size circular array. front points to the first element and size
 * determines both emptiness and the rear position.
 *
 * Java data structures:
 * int[] is the circular buffer. Modulo arithmetic wraps indices.
 *
 * Complexity:
 * Every operation is O(1), space O(k).
 */
class MyCircularDeque {
    private final int[] data;
    private final int k;
    private int front;
    private int size;

    public MyCircularDeque(int k) {
        data = new int[k];
        this.k = k;
        front = 0;
        size = 0;
    }

    public boolean insertFront(int value) {
        if (isFull()) {
            return false;
        }
        front = (front - 1 + k) % k;
        data[front] = value;
        size++;
        return true;
    }

    public boolean insertLast(int value) {
        if (isFull()) {
            return false;
        }
        int rear = (front + size) % k;
        data[rear] = value;
        size++;
        return true;
    }

    public boolean deleteFront() {
        if (isEmpty()) {
            return false;
        }
        front = (front + 1) % k;
        size--;
        return true;
    }

    public boolean deleteLast() {
        if (isEmpty()) {
            return false;
        }
        size--;
        return true;
    }

    public int getFront() {
        return isEmpty() ? -1 : data[front];
    }

    public int getRear() {
        if (isEmpty()) {
            return -1;
        }
        return data[(front + size - 1) % k];
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public boolean isFull() {
        return size == k;
    }
}

