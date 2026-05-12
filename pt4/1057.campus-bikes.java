import java.util.ArrayList;
import java.util.List;

/*
 * 1057. Campus Bikes
 */
class Solution {
    public int[] assignBikes(int[][] workers, int[][] bikes) {
        @SuppressWarnings("unchecked")
        List<int[]>[] buckets = new ArrayList[2000];

        for (int worker = 0; worker < workers.length; worker++) {
            for (int bike = 0; bike < bikes.length; bike++) {
                int distance =
                    Math.abs(workers[worker][0] - bikes[bike][0]) +
                    Math.abs(workers[worker][1] - bikes[bike][1]);

                if (buckets[distance] == null) {
                    buckets[distance] = new ArrayList<>();
                }
                buckets[distance].add(new int[] {worker, bike});
            }
        }

        int[] assignment = new int[workers.length];
        boolean[] bikeUsed = new boolean[bikes.length];
        for (int i = 0; i < assignment.length; i++) {
            assignment[i] = -1;
        }

        int assigned = 0;
        for (List<int[]> bucket : buckets) {
            if (bucket == null) {
                continue;
            }

            for (int[] pair : bucket) {
                int worker = pair[0];
                int bike = pair[1];
                if (assignment[worker] == -1 && !bikeUsed[bike]) {
                    assignment[worker] = bike;
                    bikeUsed[bike] = true;
                    assigned++;

                    if (assigned == workers.length) {
                        return assignment;
                    }
                }
            }
        }

        return assignment;
    }
}

/*
Interview Explanation

Core idea:
The problem's rule is global ordering by (distance, worker index, bike index).
Coordinates are under 1000, so Manhattan distance is at most 1998. Bucket sort
lets us process pairs in exactly that order.

Java data structures:
- List<int[]>[] buckets groups pairs by distance.
- int[] assignment tracks which bike each worker has.
- boolean[] bikeUsed tracks unavailable bikes.

Algorithm:
1. Generate every worker-bike pair.
2. Put each pair in its distance bucket. Because loops run worker first then
   bike, pairs inside a bucket are already ordered by worker index then bike
   index.
3. Scan buckets from smallest distance to largest.
4. Assign a pair if both worker and bike are still available.
5. Stop once every worker is assigned.

Correctness:
Bucket order gives increasing distance, and insertion order inside each bucket
matches the required tie-breakers. Skipping already-assigned workers or used
bikes simulates the repeated selection process exactly. Therefore every chosen
pair is the pair the problem would choose at that step.

Complexity:
Let W be workers and B be bikes. Generating and processing pairs costs O(WB).
Space is O(WB) for buckets.

Edge cases:
- Ties by distance are resolved by worker then bike index.
- More bikes than workers leaves some bikes unused.
- One worker is assigned the nearest bike.
*/
