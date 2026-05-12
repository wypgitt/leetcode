import java.util.concurrent.Semaphore;
import java.util.function.IntConsumer;

class ZeroEvenOdd {
    private final int n;
    private final Semaphore zeroTurn = new Semaphore(1);
    private final Semaphore oddTurn = new Semaphore(0);
    private final Semaphore evenTurn = new Semaphore(0);

    public ZeroEvenOdd(int n) {
        this.n = n;
    }

    public void zero(IntConsumer printNumber) throws InterruptedException {
        for (int value = 1; value <= n; value++) {
            zeroTurn.acquire();
            printNumber.accept(0);
            if ((value & 1) == 1) {
                oddTurn.release();
            } else {
                evenTurn.release();
            }
        }
    }

    public void even(IntConsumer printNumber) throws InterruptedException {
        for (int value = 2; value <= n; value += 2) {
            evenTurn.acquire();
            printNumber.accept(value);
            zeroTurn.release();
        }
    }

    public void odd(IntConsumer printNumber) throws InterruptedException {
        for (int value = 1; value <= n; value += 2) {
            oddTurn.acquire();
            printNumber.accept(value);
            zeroTurn.release();
        }
    }
}

