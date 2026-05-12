import java.util.*;

class Solution {
    public List<String> mostVisitedPattern(String[] username, int[] timestamp, String[] website) {
        Integer[] order = new Integer[username.length];
        for (int i = 0; i < order.length; i++) {
            order[i] = i;
        }
        Arrays.sort(order, Comparator.comparingInt(i -> timestamp[i]));

        Map<String, List<String>> visits = new HashMap<>();
        for (int index : order) {
            visits.computeIfAbsent(username[index], key -> new ArrayList<>()).add(website[index]);
        }

        Map<List<String>, Integer> patternCount = new HashMap<>();
        for (List<String> sites : visits.values()) {
            Set<List<String>> seen = new HashSet<>();
            for (int i = 0; i < sites.size(); i++) {
                for (int j = i + 1; j < sites.size(); j++) {
                    for (int k = j + 1; k < sites.size(); k++) {
                        seen.add(Arrays.asList(sites.get(i), sites.get(j), sites.get(k)));
                    }
                }
            }
            for (List<String> pattern : seen) {
                patternCount.put(pattern, patternCount.getOrDefault(pattern, 0) + 1);
            }
        }

        List<String> best = new ArrayList<>();
        int bestCount = -1;
        for (Map.Entry<List<String>, Integer> entry : patternCount.entrySet()) {
            List<String> pattern = entry.getKey();
            int count = entry.getValue();
            if (count > bestCount || count == bestCount && lexicographicallySmaller(pattern, best)) {
                best = pattern;
                bestCount = count;
            }
        }

        return best;
    }

    private boolean lexicographicallySmaller(List<String> a, List<String> b) {
        if (b.isEmpty()) {
            return true;
        }
        for (int i = 0; i < 3; i++) {
            int cmp = a.get(i).compareTo(b.get(i));
            if (cmp != 0) {
                return cmp < 0;
            }
        }
        return false;
    }
}

