# srt-fuzzy-sync

English | [中文说明](https://github.com/Colin-XKL/srt-fuzzy-sync#srt-fuzzy-sync-%E4%B8%AD%E6%96%87%E8%AF%B4%E6%98%8E)

This is a simple subtitle sync tool, use a reference srt file to make another one sync correctly with the audio.
srt-fuzzy-sync 是一个简单的同步srt字幕的工具, 通过指定一个与音轨匹配的参考字幕文件, 来将另一个未同步的字幕进行匹配,
时间轴修正, 使得其可以与音轨正确对齐.

**Common use case:**

- two subtitles in the same language  (srt A: language A , srt B in language A )
- or use a synced single
  language subtitle to make another dual language subtitle sync correctly. ( srt A in language A , srt B in language
  A&B)

It uses fuzzy sub string matching for find the match, and shift the subtitles.

## Usage

Ensure you have python3 installed. tested on python 3.9, but all python>=3.8 should works fine.

```shell
# use pip 
pip install srt-fuzzy-sync
```

then specify the reference srt file , target srt file to be sync, and the output file in cli args.

```shell
srt-fuzzy-sync run-sync -r mysub/reference.srt -t mysub/not-synced.srt -o mysub/ouput.srt

# manual available via `--help`
srt-fuzzy-sync run-sync --help
#Usage: srt-fuzzy-sync run-sync [OPTIONS]
#
#Options:
#  -r, --reference_sub TEXT   reference srt sub file path  [required]
#  -t, --to_be_sync_sub TEXT  target to be syned srt sub file path  [required]
#  -o, --output_path TEXT     output srt file path  [required]
#  --help                     Show this message and exit.
```

then you can get the correctly synced srt file, now enjoy your shows!

## More information

**Performance:**

For a 25-min episode, syncing two subtitles takes 0.3s on my M1 Mac mini.

**Sync subtitles in batch:**  
In case you need this, here is a sample shell command you can sync many subtitles once in a time.

(reference srt file name like "S01E01.eng.srt", target srt files "S01E01.zho.srt", output srt files "S01E01.new.srt")

```shell
find ../Season\ 28/ -type f -name "*.zho.srt" -exec bash -c 'f="{}"; srt-fuzzy-sync run-sync -r "${f%.zho.srt}.eng.srt" -t "$f" -o "${f%.zho.srt}.new.srt" ' \;
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

确保已经安装了 Python3 的环境. 本机Python 3.9 测试没问题. 理论上来说Python>=3.8都可以正常运行

```shell
# use pip 
pip install srt-fuzzy-sync

# 如果身在墙内安装速度太慢, 可以修改 pypi 镜像源. 
# for pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

```

然后通过命令行调用, 指定要参考的srt字幕文件, 要同步的srt字幕文件, 输出文件位置即可

```shell
srt-fuzzy-sync run-sync -r mysub/reference.srt -t mysub/not-synced.srt -o mysub/ouput.srt

# 获取帮助可使用 `--help`
srt-fuzzy-sync run-sync --help
#Usage: srt-fuzzy-sync run-sync [OPTIONS]
#
#Options:
#  -r, --reference_sub TEXT   reference srt sub file path  [required]  , 即参考字幕
#  -t, --to_be_sync_sub TEXT  target to be syned srt sub file path  [required], 即要同步的字幕
#  -o, --output_path TEXT     output srt file path  [required], 保存文件的位置
#  --help                     Show this message and exit.
```

## 更多信息

**性能**

本地测试中, 对一个25分钟长度的剧集的两个字幕进行对齐同步, 在我的M1 Mac Mini 耗时0.3s

**批量处理字幕**

以下是示例shell
(参考字幕为"S01E01.eng.srt", 要处理的字幕为 "S01E01.zho.srt", 保存位置 "S01E01.new.srt")

```shell
find ../Season\ 28/ -type f -name "*.zho.srt" -exec bash -c 'f="{}"; srt-fuzzy-sync run-sync -r "${f%.zho.srt}.eng.srt" -t "$f" -o "${f%.zho.srt}.new.srt" ' \;

# 转换完成后, 可以删除不需要的字幕文件, 然后使用 rename 命令批量修改文件后缀为zh
rename 's/\.new\.srt/\.zh.srt/' ./*.srt
```

## 许可

MIT