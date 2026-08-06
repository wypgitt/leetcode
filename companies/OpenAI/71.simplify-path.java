import java.util.*;

/**
 * Algorithm:
 * Unix path simplification is stack-based. Directory names push, ".." pops one
 * directory if possible, and "." or empty components are ignored.
 *
 * Java data structures:
 * ArrayDeque<String> acts as a stack of path components.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public String simplifyPath(String path) {
        Deque<String> stack = new ArrayDeque<>();
        for (String part : path.split("/")) {
            if (part.isEmpty() || part.equals(".")) {
                continue;
            }
            if (part.equals("..")) {
                if (!stack.isEmpty()) {
                    stack.removeLast();
                }
            } else {
                stack.addLast(part);
            }
        }
        StringBuilder ans = new StringBuilder();
        for (String part : stack) {
            ans.append('/').append(part);
        }
        return ans.length() == 0 ? "/" : ans.toString();
    }
}

