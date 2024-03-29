# 喜马拉\* xm文件解密工具 简易GUI版

### 说明

本人书友，有离线下载音频需求。看到原作者的代码后，简单地套了一个GUI，方便使用

打开后可选择单个文件或文件夹，然后选择输出目录，若取消选择输出目录，则默认输出到根目录下，自动开始转换，完成后弹框提示。


对于Windows用户，可以直接下载简单封装的.exe [点击下载](https://raw.githubusercontent.com/Xinjian-Zhang/Ximalaya-XM-Decrypt-GUI/main/喜玛拉x音频解密工具.exe)<br>
[下载xm_encryptor.wasm](https://raw.githubusercontent.com/Xinjian-Zhang/Ximalaya-XM-Decrypt-GUI/main/xm_encryptor.wasm)

> 注：需要将`xm_encryptor.wasm`与`喜玛拉x音频解密工具.exe`放在同一目录下使用

**感谢**<br>
原作者：[Daxiaozhang](https://github.com/Diaoxiaozhang/)
原项目：[Repo](https://github.com/Diaoxiaozhang/Ximalaya-XM-Decrypt)

----
----

### 以下为原作者README

<h1 align="center">喜马拉*xm文件解密工具</h1>
<h4 align="center">Ximalaya-XM-Decrypt</h4>


### 说明

由于喜马拉\*官方客户端下载的音频文件为加密格式，无法在普通播放器中播放，所以我写了这个小工具来解密喜马拉\*下载的音频文件。本工具参考@aynakeya的[博文](https://www.aynakeya.com/2023/03/15/ctf/xi-ma-la-ya-xm-wen-jian-jie-mi-ni-xiang-fen-xi/)，并加入了批量解密的功能。我还写了一个程序[Ximalaya-Downloader](https://github.com/Diaoxiaozhang/Ximalaya-Downloader)，用于直接爬取未加密的喜马拉\*音频文件。本工具作为Ximalaya-Downloader的补充，当每日下载vip音频达到上限时，可以使用客户端下载加密的xm文件并使用本工具解密。

在使用该软件时，请确保xm_encryptor.wasm文件与主程序文件处在同一目录下，最好是一个单独的文件夹。