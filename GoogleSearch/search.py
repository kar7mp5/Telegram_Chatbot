"""
This file is according to Nv7's googlesearch repository (https://github.com/Nv7-GitHub/googlesearch).

MIT License

Copyright (c) 2020 Nv7

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from time import sleep
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import unquote

from get_useragent import get_useragent

def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    """
    Sends a GET request to Google Search and returns the response.

    This function performs a web search query using Google's search engine. 
    It allows customization of the search term, number of results, language, 
    region, and other parameters. Additionally, it includes cookies to bypass 
    the consent page.

    Args:
        term (str): The search query term.
        results (int): The number of search results to fetch (adjusted internally).
        lang (str): The language of the search results (e.g., 'en', 'es').
        start (int): The starting index for the search results.
        proxies (dict): A dictionary of proxy settings to use for the request.
        timeout (float or tuple): The request timeout in seconds.
        safe (str): The safe search level (e.g., 'active', 'off').
        ssl_verify (bool): Whether to verify the SSL certificate.
        region (str): The region for geolocated search results (e.g., 'US', 'KR').

    Returns:
        requests.Response: The HTTP response object from the GET request.

    Raises:
        requests.HTTPError: If the response contains an HTTP error status code.

    Notes:
        - The 'CONSENT' and 'SOCS' cookies are used to bypass Google's consent page.
        - The 'User-Agent' is randomized to mimic different browser profiles.
    """
    resp = get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent(),  # Sets a random user-agent string
            "Accept": "*/*"  # Accepts any content type
        },
        params={
            "q": term,          # The search term
            "num": results + 2, # Fetches additional results to minimize requests
            "hl": lang,         # Sets the language of the results
            "start": start,     # Defines the starting index for results
            "safe": safe,       # Sets the safe search mode
            "gl": region,       # Specifies the region for the search
        },
        proxies=proxies,        # Applies proxy settings if provided
        timeout=timeout,        # Sets the timeout duration
        verify=ssl_verify,      # Enables or disables SSL certificate verification
        cookies={
            'CONSENT': 'PENDING+987',  # Bypasses Google's consent page
            'SOCS': 'CAESHAgBEhIaAB',  # Additional cookie for consent bypass
        }
    )
    resp.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    return resp


class SearchResult:
    def __init__(self, url, title, content):
        self.url = url
        self.title = title
        self.content = content

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, content={self.content})"


def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False):
    """Search the Google search engine"""

    # Proxy setup
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http")) else None

    start = start_num
    fetched_results = 0   # Keep track of the total fetched results
    fetched_links = set() # to keep track of links that are already seen previously

    while fetched_results < num_results:
        # Send request
        resp = _req(term, num_results - start,
                    lang, start, proxies, timeout, safe, ssl_verify, region)
        
        # put in file - comment for debugging purpose
        # with open('google.html', 'w') as f:
        #     f.write(resp.text)
        
        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", class_="ezO2md")
        new_results = 0  # Keep track of new results in this iteration

        for result in result_block:
            # Find the link tag within the result block
            link_tag = result.find("a", href=True)
            # Find the title tag within the link tag
            title_tag = link_tag.find("span", class_="CVA68e") if link_tag else None
            # Find the content tag within the result block
            content_tag = result.find("span", class_="FrIlee")

            # Check if all necessary tags are found
            if link_tag and title_tag and content_tag:
                # Extract and decode the link URL
                link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", "")) if link_tag else ""
            # Extract and decode the link URL
            link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", "")) if link_tag else ""
            # Check if the link has already been fetched and if unique results are required
            if link in fetched_links and unique:
                continue  # Skip this result if the link is not unique
            # Add the link to the set of fetched links
            fetched_links.add(link)
            # Extract the title text
            title = title_tag.text if title_tag else ""
            # Extract the content text
            content = content_tag.text if content_tag else ""
            # Increment the count of fetched results
            fetched_results += 1
            # Increment the count of new results in this iteration
            new_results += 1
            # Yield the result based on the advanced flag
            if advanced:
                yield SearchResult(link, title, content)  # Yield a SearchResult object
            else:
                yield link  # Yield only the link

            if fetched_results >= num_results:
                break  # Stop if we have fetched the desired number of results

        if new_results == 0:
            #If you want to have printed to your screen that the desired amount of queries can not been fulfilled, uncomment the line below:
            #print(f"Only {fetched_results} results found for query requiring {num_results} results. Moving on to the next query.")
            break  # Break the loop if no new results were found in this iteration

        start += 10  # Prepare for the next set of results
        sleep(sleep_interval)


if __name__=="__main__":
    _req()