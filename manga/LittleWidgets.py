import concurrent.futures
import imghdr
import os
import shutil
import time

import requests

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from bs4 import BeautifulSoup


class MyLabel(QLabel):
    clicked_left = pyqtSignal()
    clicked_right = pyqtSignal()

    def __init__(self,parent=None):
        super(MyLabel, self).__init__(parent)

    def setImage(self,imagePath):
        pixMap = QPixmap()
        pixMap.load(imagePath)
        pixMapSize = pixMap.size()
        if pixMapSize.height() >= pixMapSize.width():
            newPixMap= pixMap.scaledToHeight(self.size().height())
        else:
            newPixMap = pixMap.scaledToWidth(self.size().width())
        self.setPixmap(newPixMap)



    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == 1:
            self.clicked_left.emit()
        elif ev.button() == 2:
            self.clicked_right.emit()


class MyTagQuickLabel(QLabel):
    add_tag = pyqtSignal(str)
    remove_tag = pyqtSignal(str)

    def __init__(self,parent=None):
        super(MyTagQuickLabel, self).__init__(parent)
        #
        self.setAlignment(Qt.AlignCenter)
        #
        self.click_state = "Release"
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(0)

    def change_label(self):
        if self.click_state == "Release":
            self.setLineWidth(3)
            self.click_state = 'Press'
            self.add_tag.emit(self.text())

        else:
            self.setLineWidth(0)
            self.click_state = 'Release'
            self.remove_tag.emit(self.text())


    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == 1:
            self.change_label()
        elif ev.button() == 2:
            pass


class Downloader(QObject):

    print_signal = pyqtSignal(str)

    def __init__(self,parent=None):
        super(QObject, self).__init__(parent)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,es;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'ipb_member_id=3083140; ipb_pass_hash=b366dd931afe2ffcc73f6f9818304b0c; s=bf0bd94a5; sk=98fjyl6pl67an26uqf3q0tit4zzu; igneous=f4f3fdd9c; sp=3; lv=1552536403-1552538420',
            'Host': 'exhentai.org',
            'Referer': 'https://exhentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0&f_gamecg=0&f_western=0&f_non-h=0&f_imageset=0&f_cosplay=0&f_asianporn=0&f_misc=0&f_search=artistyd%24&f_apply=Apply+Filter',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'
        }
        self.url = None
        self.soup = None
        self.page = None
        self.title = None

    def __init_info(self,url):
        self.url = url
        self.soup = self.__get_soup()
        self.page = self.__get_page()
        self.title = self.__get_title()

    def __get_jp_title(self):
        title = self.soup(id='gj')[0].getText()
        return title

    def __get_en_title(self):
        title2 = self.soup(id='gn')[0].getText()
        return title2

    def __get_title(self):
        title = self.__get_jp_title()
        if not title:
            title = self.__get_en_title()
        return title

    def __get_soup(self):
        count = 0
        while True:
            count += 1
            try:
                response = requests.get(self.url, headers=self.headers, verify=False)
            except requests.exceptions.ConnectionError as e:
                self.print_signal.emit('连接失败,等待5秒')
                time.sleep(5)
                response = requests.get(self.url, headers=self.headers, verify=False)
            if response.status_code < 300:  # 正确连接
                break
            if count == 100:
                self.print_signal.emit('已经连接失败100次,返回None')
                return None
        response.close()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def __get_page(self):
        try:
            page = self.soup.find_all(onclick="document.location=this.firstChild.href")[-2].a['href'].split('=')[-1]
        except:
            page = 1
        return int(page)  # 共 page+1页

    def __get_image_urls(self):

        count = 0
        while count < self.page:
            url = self.url + '?p={}'.format(count)
            count += 1
            response = requests.get(url, headers=self.headers, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            response.close()
            image_tags = soup.find_all(class_='gdtl')
            for image_tag in image_tags:
                image_html_url = image_tag.next['href']
                image_url = self.__get_image_url(image_html_url)
                yield image_url

    def __get_image_url(self, image_html_url):
        response = requests.get(image_html_url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        response.close()
        pictureUrl = soup.find(id='img')['src']
        return pictureUrl

    def download(self,url, dst):
        self.__init_info(url)
        # 一些title 不合法
        title = self.title.replace('/', ' ')
        directory = dst + '\\' + title
        self.print_signal.emit('## IN : {}'.format(directory))
        self.__download_images(self.__get_image_urls(), directory)

    def __download_image(self, image_url, dst_dir, file_name, timeout=20, proxy_type=None, proxy=None):
        proxies = None
        if proxy_type is not None:
            proxies = {
                "http": proxy_type + "://" + proxy,
                "https": proxy_type + "://" + proxy
            }
        response = None
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        file_path = os.path.join(dst_dir, file_name)
        try_times = 0
        while True:
            try:
                try_times += 1
                response = requests.get(
                    image_url, headers=self.headers, timeout=timeout, proxies=proxies, verify=False)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                response.close()
                file_type = imghdr.what(file_path)
                # if file_type is not None:
                if file_type in ["jpg", "jpeg", "png", "bmp", "gif"] or file_type == None:
                    new_file_name = "{}.{}".format(file_name, 'jpeg')
                    new_file_path = os.path.join(dst_dir, new_file_name)
                    shutil.move(file_path, new_file_path)
                    self.print_signal.emit("## OK :  {}".format(new_file_name))
                else:
                    os.remove(file_path)
                    self.print_signal.emit("## Err :  {}".format(file_name))
                    self.print_signal.emit("## Err_URL :  {}".format(image_url))
                    self.print_signal.emit(file_type)
                break
            except Exception as e:
                if try_times < 10:
                    time.sleep(2)
                    continue
                if response:
                    response.close()
                self.print_signal.emit("## Fail:  {}  {}".format(image_url, e.args))
                break

    def __download_images(self, image_seq, dst_dir, file_prefix="img", concurrency=10, timeout=20, proxy_type=None,
                          proxy=None):
        """
        Download image according to given urls and automatically rename them in order.
        :param timeout:
        :param proxy:
        :param proxy_type:
        :param image_urls: list of image urls
        :param dst_dir: output the downloaded images to dst_dir
        :param file_prefix: if set to "img", files will be in format "img_xxx.jpg"
        :param concurrency: number of requests process simultaneously
        :return: none
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_list = list()
            count = 1
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            for image_url in image_seq:

                file_name = file_prefix + "_" + "%03d" % count
                future_list.append(
                    executor.submit(self.__download_image, image_url, dst_dir, file_name, timeout, proxy_type, proxy))
                count += 1
            concurrent.futures.wait(future_list, timeout=180)
            self.print_signal.emit('## Finish ##')

    def main(self,url,dst):
        self._get_url(url)
        self.soup = self.__get_soup()
        self.download(dst)