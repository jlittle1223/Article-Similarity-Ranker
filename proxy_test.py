import scholarly
import requests

IP_ADDRESS = "13.235.226.80"
PORT = "80"
PROXY_ADDRESS = IP_ADDRESS + ":" + PORT



def check_proxy(proxy_address):
    try:
        s = requests.Session()
        s.proxies = {
          "http": proxy_address,
          "https": proxy_address,
        }
        r = s.get("http://toscrape.com")

        return True
    except:
        return False


def test_search(proxy_address):
    # default values are shown below
    proxies = {'http' : proxy_address,
               'https': proxy_address}
    scholarly.use_proxy(**proxies)
    # If proxy is correctly set up, the following runs through it

    query = "Efficacy of cognitive-behavioral and pharmacological treatments for children with social anxiety"
    result = list(scholarly.search_pubs_query(query))
    publication = result[0].fill()

    print(publication)
    


if __name__ == "__main__":
    if check_proxy(PROXY_ADDRESS):
        print("Proxy is working!")
        test_search(PROXY_ADDRESS)
    else:
        print("Proxy Failed")




