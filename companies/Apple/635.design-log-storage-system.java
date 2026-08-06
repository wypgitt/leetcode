import java.util.*;

/**
 * Algorithm:
 * Store every (timestamp, id). To retrieve by granularity, compare only the
 * timestamp prefix relevant to that granularity.
 *
 * Java data structures:
 * ArrayList stores logs in insertion order. HashMap maps granularity names to
 * prefix lengths.
 *
 * Complexity:
 * put is O(1). retrieve is O(L), where L is the number of logs, and returns
 * O(k) ids.
 */
class LogSystem {
    private final List<String[]> logs;
    private final Map<String, Integer> index;

    public LogSystem() {
        logs = new ArrayList<>();
        index = new HashMap<>();
        index.put("Year", 4);
        index.put("Month", 7);
        index.put("Day", 10);
        index.put("Hour", 13);
        index.put("Minute", 16);
        index.put("Second", 19);
    }

    public void put(int id, String timestamp) {
        logs.add(new String[] {timestamp, String.valueOf(id)});
    }

    public List<Integer> retrieve(String start, String end, String granularity) {
        int cut = index.get(granularity);
        String lo = start.substring(0, cut);
        String hi = end.substring(0, cut);
        List<Integer> ans = new ArrayList<>();
        for (String[] log : logs) {
            String prefix = log[0].substring(0, cut);
            if (lo.compareTo(prefix) <= 0 && prefix.compareTo(hi) <= 0) {
                ans.add(Integer.parseInt(log[1]));
            }
        }
        return ans;
    }
}

