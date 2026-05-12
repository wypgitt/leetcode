import java.net.URI;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Queue;
import java.util.Set;

/*
interface HtmlParser {
    List<String> getUrls(String url);
}
*/

class Solution {
    public List<String> crawl(String startUrl, HtmlParser htmlParser) {
        String host = host(startUrl);
        Set<String> seen = new HashSet<>();
        Queue<String> queue = new ArrayDeque<>();

        seen.add(startUrl);
        queue.offer(startUrl);

        while (!queue.isEmpty()) {
            String url = queue.poll();
            for (String next : htmlParser.getUrls(url)) {
                if (!seen.contains(next) && host(next).equals(host)) {
                    seen.add(next);
                    queue.offer(next);
                }
            }
        }

        return new ArrayList<>(seen);
    }

    private String host(String rawUrl) {
        return URI.create(rawUrl).getHost();
    }
}

/*
Explanation

This is graph traversal. Start from startUrl, call HtmlParser.getUrls for each
visited page, and enqueue only unseen URLs with the same hostname.

The queue performs BFS, while the HashSet prevents cycles and duplicate parser
calls. URI parsing extracts the host so paths under the same domain are kept
and external domains are skipped.

Output order is unspecified by the problem, so returning a list built from the
set is acceptable.

Edge cases: no outgoing links; repeated links; links back to already visited
pages; external host links.

Time complexity: O(V + E) over reachable same-host URLs.
Space complexity: O(V).
*/
