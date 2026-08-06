/*
 * Definition for a QuadTree node is provided by LeetCode:
 * class Node {
 *     public boolean val;
 *     public boolean isLeaf;
 *     public Node topLeft;
 *     public Node topRight;
 *     public Node bottomLeft;
 *     public Node bottomRight;
 *     public Node() {}
 *     public Node(boolean val, boolean isLeaf) {}
 *     public Node(boolean val, boolean isLeaf, Node topLeft, Node topRight,
 *                 Node bottomLeft, Node bottomRight) {}
 * }
 */

/**
 * Algorithm:
 * Recursively OR matching quadrants. A true leaf dominates because true OR
 * anything is true; a false leaf can return the other subtree. After combining
 * children, compress four equal leaf children into one leaf.
 *
 * Complexity:
 * Time O(n), visiting paired nodes as needed. Recursion space O(height).
 */
class Solution {
    public Node intersect(Node quadTree1, Node quadTree2) {
        if (quadTree1.isLeaf) {
            return quadTree1.val ? new Node(true, true) : quadTree2;
        }
        if (quadTree2.isLeaf) {
            return quadTree2.val ? new Node(true, true) : quadTree1;
        }

        Node topLeft = intersect(quadTree1.topLeft, quadTree2.topLeft);
        Node topRight = intersect(quadTree1.topRight, quadTree2.topRight);
        Node bottomLeft = intersect(quadTree1.bottomLeft, quadTree2.bottomLeft);
        Node bottomRight = intersect(quadTree1.bottomRight, quadTree2.bottomRight);

        if (topLeft.isLeaf && topRight.isLeaf && bottomLeft.isLeaf && bottomRight.isLeaf &&
            topLeft.val == topRight.val && topLeft.val == bottomLeft.val && topLeft.val == bottomRight.val) {
            return new Node(topLeft.val, true);
        }
        return new Node(false, false, topLeft, topRight, bottomLeft, bottomRight);
    }
}
