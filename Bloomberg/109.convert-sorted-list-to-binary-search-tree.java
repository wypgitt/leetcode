/**
 * Algorithm:
 * Count the linked-list length, then simulate inorder construction. Build the
 * left subtree for the first half, consume the current list node as root, and
 * build the right subtree from the remaining nodes. This preserves sorted order
 * while producing a balanced BST.
 *
 * Java data structures:
 * A field pointer `current` replaces Python's nonlocal variable.
 *
 * Complexity:
 * Time O(n), recursion space O(log n) for the balanced output tree.
 */
class Solution {
    private ListNode current;

    public TreeNode sortedListToBST(ListNode head) {
        int length = 0;
        for (ListNode node = head; node != null; node = node.next) {
            length++;
        }
        current = head;
        return build(length);
    }

    private TreeNode build(int size) {
        if (size <= 0) {
            return null;
        }
        TreeNode left = build(size / 2);
        TreeNode root = new TreeNode(current.val);
        current = current.next;
        root.left = left;
        root.right = build(size - size / 2 - 1);
        return root;
    }
}

