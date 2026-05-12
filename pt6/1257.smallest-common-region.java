import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Solution {
    public String findSmallestRegion(List<List<String>> regions, String region1, String region2) {
        Map<String, String> parent = new HashMap<>();
        for (List<String> group : regions) {
            String root = group.get(0);
            for (int i = 1; i < group.size(); i++) {
                parent.put(group.get(i), root);
            }
        }

        Set<String> ancestors = new HashSet<>();
        String cur = region1;
        while (cur != null) {
            ancestors.add(cur);
            cur = parent.get(cur);
        }

        cur = region2;
        while (!ancestors.contains(cur)) {
            cur = parent.get(cur);
        }
        return cur;
    }
}

/*
Explanation

The region hierarchy is a tree. Build child -> parent pointers, add all
ancestors of region1 to a HashSet, then climb from region2 until hitting the
first common ancestor. That node is the smallest common region.

HashMap stores parent pointers; HashSet gives constant-time ancestor checks.

Edge cases: one region is an ancestor of the other; both regions are the same;
the answer can be the global root.

Time complexity: O(N), where N is the number of region names.
Space complexity: O(N).
*/
