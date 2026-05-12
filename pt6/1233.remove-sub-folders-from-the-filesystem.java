import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<String> removeSubfolders(String[] folder) {
        Arrays.sort(folder);
        List<String> roots = new ArrayList<>();

        for (String path : folder) {
            if (roots.isEmpty() || !path.startsWith(roots.get(roots.size() - 1) + "/")) {
                roots.add(path);
            }
        }

        return roots;
    }
}

/*
Explanation

After lexicographic sorting, a parent folder appears before its subfolders.
Keep the last accepted root folder; a new path is a subfolder exactly when it
starts with root + "/".

The slash check is critical: "/a/b" is under "/a", but "/ab" is not. Sorting
acts like a lightweight trie because descendants are grouped after parents.

Edge cases: sibling folders with common prefixes; deep nested chains; first
folder is always accepted.

Time complexity: O(n log n * L) for sorting and prefix checks.
Space complexity: O(n) for the result.
*/
