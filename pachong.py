import requests
from bs4 import BeautifulSoup
import re
import csv
import multiprocessing

url = 'http://en.heydouga.com/list_provider.html'
# http://en.heydouga.com/list_provider.html
def get_provider(url):
    provide = []
    response = requests.get(url)
    html = BeautifulSoup(response.text,"lxml")
    content = html.findAll("div",attrs={"class":"provider-logo"})
    for i in content:
        provider = i.find("a",attrs={"class":"d-block line-height-0"})
        provider_url = 'http://en.heydouga.com'+ provider["href"]
        provider_name = provider['title']
        provider_item = (provider_url,provider_name)
        provide.append(provider_item)
    return provide

def get_movieurl(url):
    item = []
    response = requests.get(url)
    html = BeautifulSoup(response.text,"lxml")
    # print(html)
    content = html.findAll("div",attrs={"class":re.compile(r"swiper-slide.*?")})
    # print(content[1])
    for i  in content:
        mourl = i.find('a')['href']
        movie_title = i.find('a')['title']
        movie_url = 'http://en.heydouga.com'+mourl
        string = re.compile(r"this.src='(.*?)'")
        img_url = re.findall(string,i.find("img")['onerror'])
        tup = (movie_title,movie_url,img_url)
        item.append(tup)
    return item

# http://en.heydouga.com/moviepages/4111/hzo-1568/index.html

def get_movie(url):
    response = requests.get(url)
    html = BeautifulSoup(response.text,"lxml")
    # views =content.find("p",{"id":"views"}).get_text()
    # print(views)
    movie_info = html.find("div",{"id":"movie-info"})
    all = movie_info.findAll('li')
    date = all[0].findAll('span')[1].get_text()
    actor = all[1].findAll('span')[1].get_text()
    provider = all[2].findAll('span')[1].get_text()
    #print(date,actor,provider)
    return date,actor,provider

def download(url,provider_nam):
    print("创建进程")
    # http://en.heydouga.com/listpages/provider_4017_1.html
    urll = str(url).split('_')
    provider_urllist = [urll[0]+'_'+urll[1]+'_'+'%s.html' %i for i in range(1,300)]
    provider_name = provider_nam
    cscfile = open(provider_name+'.csv','a')
    for provider_url in provider_urllist:
        while requests.get(provider_url):
            movie_item = get_movieurl(provider_url)
            for item in movie_item:
                movie_url = item[1]
                #print(item[0],item[2][0])
                pattern = get_movie(movie_url)
                #print(pattern[0],pattern[1],pattern[2])
                try:
                    writer = csv.writer(cscfile)
                    writer.writerow([str(item[0]),str(item[1]),str(item[2][0]),str(pattern[0]),str(pattern[1]),str(pattern[2])])
                except Exception as e:
                    print("写入错误"+e)
                finally:
                    pass

if __name__ == '__main__':
    providerlist = get_provider(url)
    for provider in providerlist:
        provider_url = provider[0]
        provider_name = provider[1]
        #print(provider_url)
        p = multiprocessing.Process(target = download, args = (provider_url,provider_name,))
        p.start()
        print("创建进程成功")

