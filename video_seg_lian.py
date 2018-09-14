import os
import re
import glob
from tqdm import tqdm
import argparse

############################################################################
############################################################################
##### how to gain start_end_text #############
## analyze on .ass files
def trans_process(trans_path):
    assert trans_path.find('.ass')!=-1
    start_end_text = []

    f = open(trans_path)
    for line in f.readlines():
        line = line.strip()#.encode('utf8')
        if line.find('Dialogue')!=-1: # which is a line contains useful info
            line_split = line.split(',', 9)
            start, end = line_split[1], line_split[2]
            text = line_split[-1]
            text = re.sub('{.*?}', '|', text) # change {}->|
            while text.find('||')!=-1: text = text.replace('||','|') # change ||->|
            if len(text)==0: continue # not a useful text
            start_end_text.append((start, end, text))

    return start_end_text


# gain name_startEndText_map map: name->[start, end, text]
def analyze_new_trans(trans_path):
    name_startEndText_map = {}
    f = open(trans_path)
    for line in f.readlines():
        video_path, audio_path, start, end, text = line.strip().split('|', 4)
        video_name = os.path.split(video_path)[-1]
        video_name = video_name.rsplit('_', 1)[0]
        if video_name not in name_startEndText_map:
            name_startEndText_map[video_name] = [(start, end, text)]
        else:
            name_startEndText_map[video_name].append((start, end, text))
    return name_startEndText_map

############################################################################
############################################################################
##### split movies: most important: gene_trans_file is '' or not #############
def split_movies(trans_path, video_path, args):
    '''
    ## gain general files
    # if gene_trans_file == '': 
        generation process: save to video/video_name; 
        gain start_end_text from trans_path
    # if gene_trans_file != '': 
        split: save to video/;
        gain start_end_text from gene_trans_file;

    '''
    video_name = os.path.split(video_path)[-1]
    video_name = video_name.rsplit('.',1)[0]
    if args.gene_trans_file == '': # gain
        save_root = os.path.join(args.save_root, video_name)
        text_save_path = os.path.join(save_root, 'transcript.txt')
        if not os.path.exists(save_root): os.makedirs(save_root)
        output = open(text_save_path, 'w') # replace
        start_end_text = trans_process(trans_path)

    if args.gene_trans_file != '':
        save_root = args.save_root
        text_save_path = os.path.join(save_root, 'transcript.txt')
        if not os.path.exists(save_root): os.makedirs(save_root)
        output = open(text_save_path, 'a') # append behind
        name_startEndText_map = analyze_new_trans(args.gene_trans_file)
        start_end_text = name_startEndText_map[video_name] if video_name in name_startEndText_map else []

    video_save_root = os.path.join(save_root, 'video')
    audio_save_root = os.path.join(save_root, 'audio')
    if not os.path.exists(video_save_root): os.makedirs(video_save_root)
    if not os.path.exists(audio_save_root): os.makedirs(audio_save_root)

    ## split according to start_end_text
    for ii, (start,end,text) in enumerate(start_end_text):
        if args.max_len_one_video==-1 or ii < args.max_len_one_video:
            video_subname = '%s_%04d' %(video_name, ii)
            video_subpath = os.path.join(video_save_root, video_subname+'.mp4')
            audio_subpath = os.path.join(audio_save_root, video_subname+'.wav')

            # gain split video and video
            cmd = 'ffmpeg -loglevel quiet -i %s -acodec copy -ss %s -to %s %s' %(video_path, start, end, video_subpath)
            os.system(cmd)
            cmd = 'ffmpeg -loglevel quiet -i ' + video_subpath + ' -f wav -vn -y ' + audio_subpath # gain split audio
            os.system(cmd)

            # write text info into xxx.txt
            output.write('%s|%s|%s|%s\n' %(video_subname, start, end, text))
    output.close()
############################################################################
############################################################################
##### main process #############
def main(args):

    #### gain trans_file and movie_file from ./video
    ## gain name files map
    name_files_map = {}
    for file in glob.glob(args.data_root+'/*'):
        name = os.path.split(file)[-1]
        name = name.rsplit('.',1)[0]
        if name in name_files_map:
            name_files_map[name].append(file)
        else:
            name_files_map[name] = [file]

    ## show name_files_map is right
    for name in name_files_map:
        files = name_files_map[name]
        if len(files)>2: print ("Error: has too much files in name: %s" %(name))
        if len(files)==1: print ("Error: only one file in name: %s" %(name))

    ## analyze each name files pairs
    for ii, name in tqdm(enumerate(name_files_map)):
        files = name_files_map[name]
        if len(files)!=2: continue
        if files[0].find('.ass')!=-1 and files[1].find('.ass')==-1:
            trans_file = files[0]
            movie_file = files[1]
        elif files[0].find('.ass')==-1 and files[1].find('.ass')!=-1:
            trans_file = files[1]
            movie_file = files[0]
        else:
            print ('Error: There is no avi file and trans file for name: %s' %(name))
            continue

        split_movies(trans_file, movie_file, args)
       
if __name__ == '__main__':
    '''
    ## gain general files
    # if gene_trans_file == '': 
        generation process: save to video/name; 
        gain start_end_text from trans_path
    # if gene_trans_file != '': 
        split: save to video/;
        gain start_end_text from gene_trans_file;

    '''
    # Gain paramters
    parser = argparse.ArgumentParser(description='Video split model')
    parser.add_argument('--data_root', default='./video', type=str, help='data root for processed <video, ass> pairs')
    parser.add_argument('--save_root', default='./video_sub', type=str, help='save_root for sub video')
    parser.add_argument('--max_len_one_video', default=100, type=int, help='max num of subvideo in one video. -1: unlimited')
    parser.add_argument('--gene_trans_file', default='', type=str, help='gene transfile path')
    global args
    args = parser.parse_args()

    ## change all <movie,ass> pair into sub videos
    main(args) 
  

