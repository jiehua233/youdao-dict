### 有道词典终端查询工具

直接在终端下面查询单词短语, 懒得一步一步打开网页查询了....

### 原理

通过抓取 `http://dict.youdao.com/search?q=word` 的内容, 返回数据 

### 安装

    $ pip install -r requirements.txt
    $ chmod +x dict.py
    $ sudo cp dict.py /usr/local/bin/dict

### 使用

    $ python dict.py hello
    $ dict world
