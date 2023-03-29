
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import re

from PIL import Image, ImageOps


import io
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

# from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

from tqdm import tqdm

import random

def get_data(html):
    """
    Function to retrieve data from a web page 
    and return a BeautifulSoup object
    """

    # Use the requests library to get data from the specified URL 
    #(Setting verify=False is a common approach to ignore SSL certificate errors)
    resp = requests.get(html, verify=False)

    # Determine the encoding of the HTTP response and HTML content
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding

    # Use BeautifulSoup to parse the HTML content and create a soup object
    soup = BeautifulSoup(resp.content, from_encoding=encoding)

    # Return the soup object
    return soup

def get_links(soup):
    """Function to extract links from a web page represented by a BeautifulSoup object"""

    # Initialize an empty list to store the links
    http_link_list = [] 

    # Iterate through all 'a' tags with an href attribute on the page
    for link in soup.find_all('a', href=True):

        # Check if the link does not start with a '/' character, indicating it is not a relative URL
        if link['href'][0] != '/': 

            # Append the link to the http_link_list after removing any surrounding quotes
            http_link_list.append(link['href'].strip("'"))

    # Return the list of links
    return http_link_list

def get_text(text_array):
    """ get text from an array"""
    text = " ".join(text_array)
    return text

def get_transcripts(base_url,episode_list):
    """Get text from all episodes in list"""
    text_return = []
    pbar = tqdm(episode_list)
    for _ , episode_url in enumerate(pbar):
        url = base_url+"/"+episode_url
        text_return.append(get_transcript(url))
        pbar.set_description("getting transcript from {link}".format(link = url))
    return text_return

def get_transcript(url):
    """
    Function to extract text from a PDF file at a given URL, remove a specific sequence,
    and return the remaining text as a string
    """

    try:
        # Fetch the PDF file from the URL
        response = requests.get(url, stream=True)

        # Create a memory stream object for the PDF content
        pdf_stream = io.BytesIO(response.content)

        # Create a PDF resource manager object and set the caching to False
        resource_manager = PDFResourceManager(caching=False)

        # Create a buffer for the extracted text
        output_text = io.StringIO()

        # Create a PDF layout parameters object
        layout_params = LAParams()

        # Create a PDF page interpreter object
        page_interpreter = PDFPageInterpreter(
            resource_manager,
            TextConverter(resource_manager, output_text, laparams=layout_params)
        )

        # Loop through each page in the PDF document and extract text
        for page in PDFPage.get_pages(pdf_stream):
            # Process the page using the page interpreter
            page_interpreter.process_page(page)

        # Get the extracted text as a string
        extracted_text = output_text.getvalue()

        # Define start and end patterns for the sequence to be removed
        start_pattern = r"For recommended water filters, tests and the full show notes, please visit"
        end_pattern = r"Disclaimer: https://hubermanlab.com/disclaimer"

        # Combine the patterns to form a regex pattern for the entire sequence
        sequence_pattern = f"{start_pattern}.*{end_pattern}"

        # Use regex to find and remove the sequence from the extracted text
        extracted_text = re.sub(sequence_pattern, "", extracted_text, flags=re.DOTALL)

        # Return the extracted text as a string
        return extracted_text
    
    except:
        # Return an empty string in case of any error
        return ''
    
def punctuation_stop(text):
    """remove punctuation and stop words"""
    filtered = []
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    for w in word_tokens:
        if w not in stop_words and w.isalpha():
            filtered.append(w.lower())
    return filtered

def make_silhouette(input_path, output_path):
    """Converts a portrait image to a silhouette"""
    # Open input image and convert to grayscale
    with Image.open(input_path) as img:
        img = img.convert('L')

        # Invert image (black becomes white, white becomes black)
        img = ImageOps.invert(img)

        # Apply a threshold to turn all gray pixels to black
        threshold = 255
        img = img.point(lambda x: 0 if x < threshold else 255)

        # Convert image to RGBA and set alpha channel to 0 (transparent)
        img = img.convert('RGBA')
        data = img.getdata()
        new_data = []
        for item in data:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                new_data.append((0, 0, 0, 255))
            else:
                new_data.append((255, 255, 255, 0))
        img.putdata(new_data)

        # Save output image
        img.save(output_path)


def get_random_elements(lst, n):
    """
    Function to get n random elements from a list and return them in a list
    """
    if n > len(lst):
        n = len(lst)
    
    return random.sample(lst, n)