/*
 * LeetCode 1367 - Linked List in Binary Tree
 *
 * ListNode and TreeNode are provided by LeetCode.
 */
class Solution {
    public boolean isSubPath(ListNode head, TreeNode root) {
        if (root == null) {
            return false;
        }

        return matches(head, root)
                || isSubPath(head, root.left)
                || isSubPath(head, root.right);
    }

    private boolean matches(ListNode listNode, TreeNode treeNode) {
        if (listNode == null) {
            return true;
        }
        if (treeNode == null || treeNode.val != listNode.val) {
            return false;
        }

        return matches(listNode.next, treeNode.left)
                || matches(listNode.next, treeNode.right);
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * The linked list may start at any tree node. For each possible start, try to
 * match the list downward through left/right child choices.
 *
 * Java data structures:
 * Recursion handles both layers:
 * - `isSubPath` scans tree nodes as starting positions.
 * - `matches` checks whether the linked list matches a downward path.
 *
 * Edge cases:
 * - Empty tree cannot contain a non-empty list.
 * - If the list is fully consumed, the match succeeds.
 * - Duplicate values require checking every possible start.
 *
 * Complexity:
 * Time O(n * m) in the worst case, where n is tree nodes and m is list length.
 * Space O(h + m), for recursion depth.
 */
