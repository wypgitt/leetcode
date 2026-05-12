/*
 * LeetCode 1344 - Angle Between Hands of a Clock
 */
class Solution {
    public double angleClock(int hour, int minutes) {
        hour %= 12;
        double minuteAngle = minutes * 6.0;
        double hourAngle = hour * 30.0 + minutes * 0.5;
        double difference = Math.abs(hourAngle - minuteAngle);
        return Math.min(difference, 360.0 - difference);
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Convert both hands to degrees from 12 o'clock, compute their absolute
 * difference, and return the smaller angle between the hands.
 *
 * Math:
 * - Minute hand moves 360 / 60 = 6 degrees per minute.
 * - Hour hand moves 360 / 12 = 30 degrees per hour, plus 0.5 degrees per
 *   minute because it moves continuously.
 *
 * Edge cases:
 * - Hour 12 maps to 0 degrees using `hour %= 12`.
 * - If the direct difference exceeds 180, the smaller angle is 360 - difference.
 *
 * Complexity:
 * Time O(1).
 * Space O(1).
 */
