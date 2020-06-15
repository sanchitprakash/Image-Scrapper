import time, os, io 
from PIL import Image
import requests
from selenium import webdriver
from argparse import ArgumentParser
import hashlib
from concurrent.futures import ThreadPoolExecutor


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    """
    Returns a list of downloadable image links 
    """

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = []
    image_count = 0
    results_start = 0
    exceed_limit = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.append(actual_image.get_attribute('src'))

        image_count = len(image_urls)

        if len(image_urls) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)} image links, done!")
            image_urls = image_urls[:max_links_to_fetch]
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)
        exceed_limit+=1
        if exceed_limit > 10:
            print("No more image links available!")
            print(f"Maximum image links avalable for the search query are {image_count}")
            break

    return image_urls

def download_image(folder_path:str,url:str):
    """
    Download the image from the provided url
    """
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--search-query",type=str,help="search key for images to download", required=True)
    parser.add_argument("--driver-path",type=str,help="path to browser driver", required=True)
    parser.add_argument("--target-path",type=str,help="path to save the images", required=False, default="./images")
    parser.add_argument("--n-images",type=int,help='number of images to download',required=True)
    parser.add_argument("--n-threads",type=int,help='number of threads to download images at parallel',required=False, default=1)
    args = parser.parse_args()

    search_term = args.search_query
    number_images = args.n_images
    MAXWORKERS = args.n_threads
    driver_path = args.driver_path
    target_folder = os.path.join(args.target_path,'_'.join(search_term.lower().split(' ')))
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    #initiating web driver to fetch links
    with webdriver.Chrome(executable_path=driver_path) as wd:
        urls = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)
    
    #Download images parallely depending upon number of threads
    with ThreadPoolExecutor(max_workers=MAXWORKERS) as e:
        for link in urls:
            download = e.submit(download_image,target_folder,link)
            try:
                print(download.result())
            except:
                print(f"Unable to download from this {link}")

    print("Images downloaded successfully")

if __name__ == "__main__":
    main()

