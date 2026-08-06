import java.util.*;

/**
 * Algorithm:
 * Generate a uniform polar angle and choose radius as R * sqrt(u). The square
 * root is necessary because circle area grows with r^2; using R * u would
 * over-sample the center.
 *
 * Java data structures:
 * java.util.Random supplies uniform doubles in [0, 1).
 *
 * Complexity:
 * O(1) time and O(1) space per point.
 */
class Solution {
    private final double radius;
    private final double xCenter;
    private final double yCenter;
    private final Random random;

    public Solution(double radius, double x_center, double y_center) {
        this.radius = radius;
        this.xCenter = x_center;
        this.yCenter = y_center;
        this.random = new Random();
    }

    public double[] randPoint() {
        double angle = random.nextDouble() * 2.0 * Math.PI;
        double distance = radius * Math.sqrt(random.nextDouble());
        return new double[] {
            xCenter + distance * Math.cos(angle),
            yCenter + distance * Math.sin(angle)
        };
    }
}

