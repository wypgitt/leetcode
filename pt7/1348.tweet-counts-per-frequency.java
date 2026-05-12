import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/*
 * LeetCode 1348 - Tweet Counts Per Frequency
 */
class TweetCounts {
    private final Map<String, List<Integer>> tweetsByName;

    public TweetCounts() {
        tweetsByName = new HashMap<>();
    }

    public void recordTweet(String tweetName, int time) {
        List<Integer> times = tweetsByName.computeIfAbsent(tweetName, ignored -> new ArrayList<>());
        int index = Collections.binarySearch(times, time);
        if (index < 0) {
            index = -index - 1;
        }
        times.add(index, time);
    }

    public List<Integer> getTweetCountsPerFrequency(
            String freq,
            String tweetName,
            int startTime,
            int endTime) {

        int interval = getInterval(freq);
        List<Integer> times = tweetsByName.getOrDefault(tweetName, Collections.emptyList());
        List<Integer> answer = new ArrayList<>();

        for (int start = startTime; start <= endTime; start += interval) {
            int end = Math.min(start + interval - 1, endTime);
            int left = lowerBound(times, start);
            int right = upperBound(times, end);
            answer.add(right - left);
        }

        return answer;
    }

    private int getInterval(String freq) {
        if (freq.equals("minute")) {
            return 60;
        }
        if (freq.equals("hour")) {
            return 3600;
        }
        return 86400;
    }

    private int lowerBound(List<Integer> values, int target) {
        int left = 0;
        int right = values.size();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (values.get(mid) < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }

    private int upperBound(List<Integer> values, int target) {
        int left = 0;
        int right = values.size();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (values.get(mid) <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Keep timestamps sorted for each tweet name. A query splits the requested time
 * range into frequency buckets. For each bucket, binary search the first time
 * >= bucket start and the first time > bucket end; their difference is the
 * count in that bucket.
 *
 * Java data structures:
 * `HashMap<String, List<Integer>>` maps tweet names to sorted timestamp lists.
 * `ArrayList<Integer>` supports fast indexed binary search. Insertion is O(m)
 * because elements may shift, but the problem's operation count is small.
 *
 * Edge cases:
 * - The last bucket may be shorter than the interval.
 * - Missing tweet name returns all zero counts.
 * - Boundary timestamps are included because buckets are closed intervals.
 *
 * Complexity:
 * recordTweet is O(m) for one tweet's list.
 * getTweetCountsPerFrequency is O(b log m), where b is number of buckets.
 * Space O(total recorded tweets).
 */
