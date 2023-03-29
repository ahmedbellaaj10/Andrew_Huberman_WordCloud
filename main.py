import matplotlib.pyplot as plt 
from os import path, getcwd
import numpy as np

from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

from PIL import Image

import utils

#webpage 
base_url = 'https://readthatpodcast.com'

#gets word soup from website 
soupout = utils.get_data(base_url)

#gets links from website     
h_links = utils.get_links(soupout)

#remove the irrelevant links
h_links = h_links[12::]

"""
optional
you can uncomment the following lines of code to work with a subset of links to make the process faster
"""
# n = 10
# h_links = get_random_elements(h_links, n)

#return list of all episode text 
text_return_list = utils.get_transcripts(base_url,h_links)
all_text = utils.get_text(text_return_list)

#removed punctuation and stop words 
filteredlst = utils.punctuation_stop(all_text)

#list of unwanted words (based on trial and error)
unwanted = ['um','little','bit','within','without','with','might','two','one','yes','yeah','andrew''huberman','podcast','guest','guy','really','me','you','us','talk','little bit','thing','say','go','actually','even','probably','going','said','something','okay','maybe','got','well','way']

#remove unwanted words 
text = " ".join([ele for ele in filteredlst if ele not in unwanted])

d = getcwd()
utils.make_silhouette("andrewhuberman.png", "andrewhuberman_silouhette.png")

#numpy image file of mask image 
mask_logo = np.array(Image.open(path.join(d, "andrewhuberman_silouhette.png")))

#create the word cloud object 
wc= WordCloud(background_color="white", max_words=5000, max_font_size=90, random_state=1, mask=mask_logo, stopwords=STOPWORDS)
wc.generate(text)

image_colors = ImageColorGenerator(mask_logo)

# plot the wordcloud silhouette
plt.figure(figsize=[10,10])
plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis('off')
plt.show()