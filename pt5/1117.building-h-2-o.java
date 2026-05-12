import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Semaphore;

class H2O {
    private final Semaphore hydrogenSlots = new Semaphore(2);
    private final Semaphore oxygenSlots = new Semaphore(1);
    private final CyclicBarrier moleculeBarrier = new CyclicBarrier(3);

    public H2O() {}

    public void hydrogen(Runnable releaseHydrogen) throws InterruptedException {
        hydrogenSlots.acquire();
        releaseHydrogen.run();
        awaitMolecule();
        hydrogenSlots.release();
    }

    public void oxygen(Runnable releaseOxygen) throws InterruptedException {
        oxygenSlots.acquire();
        releaseOxygen.run();
        awaitMolecule();
        oxygenSlots.release();
    }

    private void awaitMolecule() throws InterruptedException {
        try {
            moleculeBarrier.await();
        } catch (BrokenBarrierException ex) {
            throw new RuntimeException(ex);
        }
    }
}

