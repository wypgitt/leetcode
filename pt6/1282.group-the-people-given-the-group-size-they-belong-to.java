import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<List<Integer>> groupThePeople(int[] groupSizes) {
        Map<Integer, List<Integer>> buckets = new HashMap<>();
        List<List<Integer>> ans = new ArrayList<>();

        for (int person = 0; person < groupSizes.length; person++) {
            int size = groupSizes[person];
            buckets.computeIfAbsent(size, key -> new ArrayList<>()).add(person);

            if (buckets.get(size).size() == size) {
                ans.add(buckets.get(size));
                buckets.put(size, new ArrayList<>());
            }
        }

        return ans;
    }
}

/*
Explanation

Bucket people by required group size. Whenever a bucket reaches that size, it
forms a complete group and is added to the answer.

HashMap<Integer, List<Integer>> is the right Java data structure because each
group size owns one current partial group. People with the same size are
interchangeable, and the problem guarantees a valid partition.

Edge cases: group size 1 flushes immediately; many groups may share the same
size; any valid output order is accepted.

Time complexity: O(n).
Space complexity: O(n).
*/
