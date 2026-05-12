import java.util.*;

class SnapshotArray {
    private int snapId;
    private final List<int[]>[] history;

    @SuppressWarnings("unchecked")
    public SnapshotArray(int length) {
        history = new ArrayList[length];
        for (int i = 0; i < length; i++) {
            history[i] = new ArrayList<>();
            history[i].add(new int[] {0, 0});
        }
    }

    public void set(int index, int val) {
        List<int[]> records = history[index];
        int[] last = records.get(records.size() - 1);
        if (last[0] == snapId) {
            last[1] = val;
        } else {
            records.add(new int[] {snapId, val});
        }
    }

    public int snap() {
        return snapId++;
    }

    public int get(int index, int snap_id) {
        List<int[]> records = history[index];
        int left = 0;
        int right = records.size() - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (records.get(mid)[0] <= snap_id) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return records.get(right)[1];
    }
}
