#JAV Capture for DSM7 video station

### 介绍
群晖videostation插件 Javdb源 仅支持DSM7

### 安装
1. release中下载videostation插件包，群晖docker注册表中添加镜像`nanjozy/javcapture`
2. docker中启动javcapture镜像，需要映射本地路径到/data/data/,5004端口到5004
3. 打开本地docker映射目录，docker启动后会自动生成`config.dev.json`文件：
    ```{
        "main": {
            "dev": false,
            "proxy": "", //系统代理
            "no_proxy": "127.0.0.1,localhost,local,.local",
            "RUNTIME": null,
            "LOG": null
        },
        "javdb": {
            "host": "https://javdb39.com", //javdb地址
            "local": "http://127.0.0.1:5004"
        }, //用于videostation从api抓取图片，如果127.0.0.1无法正常使用，可以尝试172.17.0.1（docker子网）
        "FLASK": {
            "secret_key": "",
            "session_enabled": false,
            "session_expired": 86400,
            "session_type": "filesystem",
            "cookie_prefix": "",
            "uwsgi_cache_enabled": false
        }
    }`
4. video station导入插件。
5. video station插件默认使用`http://127.0.0.1:5004`地址连接api
6. docker映射目录下`runtime`内是采集的缓存信息，删除可刷新缓存

### 二次开发

#### 文件说明
1. `com.zanjo.javdb`: video station插件目录
2. `javapi`: javcapture代码
3. `pylibz`: 基础库

#### 群晖插件官方文档：
[Synology_Video_Stat_API_enu.pdf](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)