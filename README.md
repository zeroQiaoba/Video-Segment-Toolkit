# Video Segment Toolkit

## Install

- dlib
- tqdm
- argparse
- cv2
- ffmpeg

## Files
- `model/`: save `dlib_face_recognition_resnet_model_v1.dat` and `shape_predictor_68_face_landmarks.dat` (which is utilized in dlib)
- `video/`: save `<video, trans>` pairs. For example: <`1911.Revolution.2011.BluRay.iPad.720p.AAC.2Audio.x264-HDSPad.ass`, `1911.Revolution.2011.BluRay.iPad.720p.AAC.2Audio.x264-HDSPad.mp4`>
- `dlib_utils.py`: for all dlib related process
- `video_seg_lian.py` : gain video segments from original transcript or selected transcripts
- `video_select.py`: select video segments by different select methods(1,2,3)
- `run_all.sh`: main process. Combine `video_seg_lian.py` and `video_select.py` together.



## Input Data Format

- All `<video, transcript>` pairs save in `./video` 
- transcript mush in .ass format (you can convert into .ass through aegisub toolkit)
- transcript mush must in utf8 encoding method. (you can convert into .ass through notepad)
- video and transcript mush have the same name; There are no space in the name.


## Bash command for all process

```sh
## origin datas：./video  <video, transscript> pairs
## middle folder: save to video_sub
## save to: ./video_sub_sub
sh run_all.sh
```

### Video Segment
`video_seg_lian.py`: the main file

`--data_root`: input data root

`--save_root`: save generate data root

`--max_len_one_video`: -1 无限制长度。否则，限制长度

```sh
# only extract 100 subvideo from original video
python video_seg_lian.py --data_root='./video' --save_root='./video_sub' --max_len_one_video=100

# gain all video from original video
python video_seg_lian.py --data_root='./video' --save_root='./video_sub' --max_len_one_video=-1
```

- ffmpeg: video segment commond comparison
```sh
## 切分格式1 高清，但是视屏对齐（最好的切分方法）
video_subpath = os.path.join(video_save_root, video_subname+'.mp4')
cmd = 'ffmpeg -i %s -acodec copy -ss %s -to %s %s' %(video_path, start, end, video_subpath)

## 低清，但是内容完整，不会报错
#video_subpath = os.path.join(video_save_root, video_subname+'.avi')
#cmd = 'ffmpeg -i %s -ss %s -to %s %s' %(video_path, start, end, video_subpath)
```

| target format | -acodec | -vcodec | video_size                          |
| ------------- | ------- | ------- | ----------------------------------- |
| avi           | None    | None    | 408kb(not clear)                    |
| avi           | None    | yes     | 0                                   |
| avi           | yes     | None    | 619kb                               |
| avi           | yes     | yes     | 255kb                               |
| mp4           | None    | None    | 0                                   |
| mp4           | None    | yes     | 0                                   |
| mp4           | yes     | None    | 853kb（clear）                        |
| mp4           | yes     | yes     | 593kb（clear, but begining is wrong） |


### Segment Selection

`video_select.py` : generate `--gene_trans_file` from original transcript.txt of each video

`--data_root`: data save root

`--gene_trans_file`: gene_trans_file save path

`--select_type`: selection type

`--min_len and --max_len`: only save video in such range

`--min_score`: min face rate scores

- type 1：
  - 1 filter according to lens (gain video in [`min_len`, `max_len`])
  - 2 filter according to how much frames in the video has faces (`min_score`)
```sh
python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=1 --min_len=1 --max_len=10 --min_score=0.5 
```

- type 2：
  - 1 merge continuous video if they have the same person inside
  - 2 filter according to how much frames in the video has faces (`min_score`)
  - 3 filter according to lens (gain video in [`min_len`, `max_len`])
```sh
python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=2 --min_len=1 --max_len=10 --min_score=0.5 
```

- type 3：
  - 1 filter according to lens (gain video in [`min_len`, `max_len`])
```sh
# len至少为4的数据保留，其余的都删除（不需要安装dlib和opencv）
python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=3 --min_len=1 --max_len=10
```

### Gain new subvideos after selection
`video_seg_lian.py`: gain subvideo according to `gene_trans_file`

`--data_root`: input data root

`--save_root`: save generate data root

`--max_len_one_video`: -1 无限制长度。否则，限制长度

`--gene_trans_file`: generate trans_file path

```sh
python video_seg_lian.py --data_root='./video' --save_root='./video_sub_sub' --gene_trans_file='./video_sub/trans_gene.txt' --max_len_one_video=-1
```


## Labeling Toolkit for each segment (unfinished)
