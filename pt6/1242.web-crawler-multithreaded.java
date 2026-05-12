import java.net.URI;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/*
interface HtmlParser {
    List<String> getUrls(String url);
}
*/

class Solution {
    public List<String> crawl(String startUrl, HtmlParser htmlParser) {
        String hostname = host(startUrl);
        Set<String> seen = ConcurrentHashMap.newKeySet();
        Queue<Future<List<String>>> futures = new ArrayDeque<>();
        ExecutorService executor = Executors.newFixedThreadPool(16);

        seen.add(startUrl);
        futures.offer(executor.submit(() -> htmlParser.getUrls(startUrl)));

        try {
            while (!futures.isEmpty()) {
                Future<List<String>> future = futures.poll();
                for (String next : future.get()) {
                    if (host(next).equals(hostname) && seen.add(next)) {
                        futures.offer(executor.submit(() -> htmlParser.getUrls(next)));
                    }
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (ExecutionException e) {
            throw new RuntimeException(e);
        } finally {
            executor.shutdown();
        }

        return new ArrayList<>(seen);
    }

    private String host(String rawUrl) {
        return URI.create(rawUrl).getHost();
    }
}

/*
Explanation

This is the graph traversal from the single-threaded crawler, but calls to
HtmlParser.getUrls are submitted to an ExecutorService so multiple blocking URL
fetches can run concurrently.

ConcurrentHashMap.newKeySet() is the key Java data structure: it lets us mark a
URL as seen atomically with seen.add(next), preventing duplicate crawl tasks
when multiple pages link to the same URL. A queue tracks submitted Future
objects whose results still need to be processed.

Edge cases: repeated links, cycles, external host links, and arbitrary task
completion order. Output order is unspecified.

Time complexity: O(V + E) over reachable same-host links, ignoring wait time.
Space complexity: O(V) for seen URLs and pending futures.
*/
