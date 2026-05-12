/*
 * 1038. Binary Search Tree to Greater Sum Tree
 */

// LeetCode provides this class:
// class TreeNode {
//     int val;
//     TreeNode left;
//     TreeNode right;
//     TreeNode() {}
//     TreeNode(int val) { this.val = val; }
//     TreeNode(int val, TreeNode left, TreeNode right) {
//         this.val = val;
//         this.left = left;
//         this.right = right;
//     }
// }

class Solution {
    private int runningSum = 0;

    public TreeNode bstToGst(TreeNode root) {
        reverseInorder(root);
        return root;
    }

    private void reverseInorder(TreeNode node) {
        if (node == null) {
            return;
        }

        reverseInorder(node.right);
        runningSum += node.val;
        node.val = runningSum;
        reverseInorder(node.left);
    }
}

/*
Interview Explanation

Core idea:
A normal inorder traversal of a BST visits values in ascending order. Reverse
inorder visits descending order, so when we process a node, every greater value
has already been accumulated.

Java data structures:
- The TreeNode links define the BST.
- The recursion stack performs reverse inorder traversal.
- runningSum is an instance field so recursive calls can share the accumulated
  total without wrapping it in an array or object.

Algorithm:
1. Visit the right subtree.
2. Add the current node's original value to runningSum.
3. Replace node.val with runningSum.
4. Visit the left subtree.

Correctness:
When a node is processed, reverse inorder has already visited exactly the nodes
with greater values and none of the smaller nodes. Therefore runningSum plus
the current original value is exactly the required greater-sum-tree value.

Complexity:
Each node is visited once, so time is O(n). Recursion stack space is O(h),
where h is the tree height.

Edge cases:
- Single-node tree remains unchanged.
- Left- or right-skewed trees still follow sorted BST order.
- Value 0 contributes normally to the running sum.
*/
