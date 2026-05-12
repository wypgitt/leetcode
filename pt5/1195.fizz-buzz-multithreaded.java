import java.util.function.IntConsumer;

class FizzBuzz {
    private final int n;
    private int current = 1;

    public FizzBuzz(int n) {
        this.n = n;
    }

    public void fizz(Runnable printFizz) throws InterruptedException {
        runWhen(value -> value % 3 == 0 && value % 5 != 0, value -> printFizz.run());
    }

    public void buzz(Runnable printBuzz) throws InterruptedException {
        runWhen(value -> value % 5 == 0 && value % 3 != 0, value -> printBuzz.run());
    }

    public void fizzbuzz(Runnable printFizzBuzz) throws InterruptedException {
        runWhen(value -> value % 15 == 0, value -> printFizzBuzz.run());
    }

    public void number(IntConsumer printNumber) throws InterruptedException {
        runWhen(value -> value % 3 != 0 && value % 5 != 0, printNumber);
    }

    private synchronized void runWhen(Condition condition, IntConsumer action) throws InterruptedException {
        while (true) {
            while (current <= n && !condition.matches(current)) {
                wait();
            }
            if (current > n) {
                notifyAll();
                return;
            }
            action.accept(current);
            current++;
            notifyAll();
        }
    }

    private interface Condition {
        boolean matches(int value);
    }
}

