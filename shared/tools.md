# Available Firecrawl MCP Tools

## Tools List

1. **mcp__firecrawl__firecrawl_scrape**
   - Scrape content from a single URL with advanced options
   - Best for: Single page content extraction
   - Supports: markdown, HTML, screenshots, JSON extraction

2. **mcp__firecrawl__firecrawl_map**
   - Map a website to discover all indexed URLs
   - Best for: Discovering URLs on a website before scraping
   - Returns: Array of URLs found on the site

3. **mcp__firecrawl__firecrawl_crawl**
   - Start a crawl job on a website and extract content from all pages
   - Best for: Extracting content from multiple related pages
   - Returns: Operation ID for status checking

4. **mcp__firecrawl__firecrawl_check_crawl_status**
   - Check the status of a crawl job
   - Returns: Status and progress of crawl job, including results

5. **mcp__firecrawl__firecrawl_search**
   - Search the web and optionally extract content from search results
   - Best for: Finding specific information across multiple websites
   - Sources: web, images, news

6. **mcp__firecrawl__firecrawl_extract**
   - Extract structured information from web pages using LLM capabilities
   - Best for: Extracting specific structured data (prices, names, details)
   - Supports: Custom prompts and JSON schemas for structured extraction