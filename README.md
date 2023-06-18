# srt-fuzzy-sync

This is a simple subtitle sync tool, use a reference srt file to make another one sync correctly with the audio.

**Common use case:**

- two subtitles in the same language  (srt A: language A , srt B in language A )
- or use a synced single
  language subtitle to make another dual language subtitle sync correctly. ( srt A in language A , srt B in language
  A&B)

It uses fuzzy sub string matching for find the match, and shift the subtitles.

## Usage

first clone the repo. enter the directory.

ensure you have python3 installed. tested on python 3.9, but all python>=3.8 should works fine.

```shell
# use pip 
python -m pip install .

# or you can use poetry
poetry install
```

then specify the reference srt file , target srt file to be sync, and the output file in cli args.

```shell
python3 ./main mysub/reference.srt mysub/no-synced.srt mysub/ouput.srt
```

then you can get the correctly synced srt file, now enjoy your shows!

## More information

**Performance:**

For a 25min episode, syncing two subtitles takes 0.3s on my M1 Mac mini.

**Sync subtitles in batch:**  
In case you need this, here is a sample shell command you can sync many subtitles once in a time.

(reference srt file name like "S01E01_ref.srt", target srt files "S01E01_old.srt", output srt files "S01E01_new.srt")

```shell
find . -type f -name "*_old.srt" -exec sh -c 'python3 ./main.py $(basename {}  _old.srt)_ref.srt {} $(basename {}  _old.srt)_new.srt  ' \;
```

## License

MIT

## srt-fuzzy-sync 中文说明

srt-fuzzy-sync 是一个简单的同步srt字幕的工具, 通过指定一个与音轨匹配的参考字幕文件, 来将另一个未同步的字幕进行匹配,
时间轴修正, 使得其可以与音轨正确对齐.

使用场景说明:

- 将两个同样语言的字幕文件进行对齐
- 用一个正确对齐的A语言字幕, 来将另一个A和B的双语字幕进行同步. 如通过影片官方或内嵌的英文字幕, 来将另一个下载来的双语字幕进行对齐同步

本工具使用模糊子字符串匹配算法来寻找两个字幕文件之间的关联匹配的部分, 然后计算时间偏移量, 来修正目标字幕的时间轴

## 使用说明

克隆本项目, 进入项目根目录

确保已经安装了Python3 的环境. 本机Python 3.9 测试没问题. 理论上来说Python>=3.8都可以正常运行

```shell
# 使用pip 安装依赖
python -m pip install .
# 或者可以使用 poetry
poetry install

# 如果身在墙内安装速度太慢, 可以修改 pypi 镜像源. 

# for pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# for poetry
poetry source add --default mirrors https://pypi.tuna.tsinghua.edu.cn/simple/
```

然后通过命令行调用, 指定要参考的srt字幕文件, 要同步的srt字幕文件, 输出文件位置即可

```shell
python3 ./main mysub/reference.srt mysub/no-synced.srt mysub/ouput.srt
```

## 许可

MIT