import java.util.HashMap;
import java.util.Map;

/*
 * LeetCode 1396 - Design Underground System
 */
class UndergroundSystem {
    private final Map<Integer, CheckIn> activeTrips;
    private final Map<String, TripStats> routeStats;

    public UndergroundSystem() {
        activeTrips = new HashMap<>();
        routeStats = new HashMap<>();
    }

    public void checkIn(int id, String stationName, int t) {
        activeTrips.put(id, new CheckIn(stationName, t));
    }

    public void checkOut(int id, String stationName, int t) {
        CheckIn checkIn = activeTrips.remove(id);
        String routeKey = checkIn.station + "->" + stationName;
        TripStats stats = routeStats.computeIfAbsent(routeKey, ignored -> new TripStats());
        stats.totalTime += t - checkIn.time;
        stats.tripCount++;
    }

    public double getAverageTime(String startStation, String endStation) {
        TripStats stats = routeStats.get(startStation + "->" + endStation);
        return (double) stats.totalTime / stats.tripCount;
    }

    private static class CheckIn {
        String station;
        int time;

        CheckIn(String station, int time) {
            this.station = station;
            this.time = time;
        }
    }

    private static class TripStats {
        int totalTime;
        int tripCount;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Maintain current check-ins and aggregate completed trips by route. We do not
 * need every historical trip; total time and trip count are enough for averages.
 *
 * Java data structures:
 * - `HashMap<Integer, CheckIn>` maps customer id to active station/time.
 * - `HashMap<String, TripStats>` maps route key to total duration and count.
 * Small helper classes keep the state readable.
 *
 * Edge cases:
 * - Reverse routes are different because route key order is start->end.
 * - Multiple trips on the same route update one aggregate.
 * - LeetCode guarantees consistent check-in/check-out calls and valid average
 *   queries.
 *
 * Complexity:
 * checkIn O(1), checkOut O(1), getAverageTime O(1) average hash-map time.
 * Space O(a + r), where a is active trips and r is distinct routes.
 */
