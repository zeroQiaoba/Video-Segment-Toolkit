import os
import re
import glob
import dlib
from tqdm import tqdm
import numpy as np
import argparse

## merge transscript-> trans_all.txt: video_path|start|end|text
def merge_trans(data_root, output_trans_path):
    datas = []
    for video_root in glob.glob(data_root+'/*'):
        trans_path = os.path.join(video_root, 'transcript.txt')
        if not os.path.exists(trans_path):
            print ('%s not exist transscript.txt' %(trans_path))
            continue

        f = open(trans_path)
        for line in f.readlines():
            video_name, start, end, text = line.strip().split('|', 3)
            video_path = os.path.join(video_root,'video',video_name+'.mp4')
            audio_path = os.path.join(video_root,'audio',video_name+'.wav')
            datas.append('%s|%s|%s|%s|%s' %(video_path, audio_path, start, end, text))
    np.savez_compressed(output_trans_path,
                        datas=datas)


## select faces with min_scores
def filter_faces(input_trans_path, output_trans_path, faceDlib, min_score=0.5):
    datas = np.load(input_trans_path)['datas']
    s_embs, e_embs, sub_datas, num_empty_facess, num_facess = [], [], [], [], []
    for ii, data in tqdm(enumerate(datas)):
        video_path, audio_path, start, end, text = data.strip().split('|', 4)
        num_empty_faces, num_faces, s_emb, e_emb = faceDlib.face_rate_scores(video_path)
        face_rate = num_faces/float(num_empty_faces+num_faces)
        if face_rate > min_score:
            sub_datas.append(datas[ii])
            s_embs.append(s_emb)
            e_embs.append(e_emb)
            num_facess.append(num_faces)
            num_empty_facess.append(num_empty_faces)

    np.savez_compressed(output_trans_path,
                        datas = sub_datas,
                        s_embs = s_embs,
                        e_embs = e_embs,
                        num_empty_facess = num_empty_facess,
                        num_facess = num_facess,
                        )


## merge videos which is continue [according to s_emb and e_emb]
def merge_video(input_trans_path, output_trans_path, min_score=0.5):
    datas = np.load(input_trans_path)['datas']
    s_embs = np.load(input_trans_path)['s_embs']
    e_embs = np.load(input_trans_path)['e_embs']
    num_facess = np.load(input_trans_path)['num_facess']
    num_empty_facess = np.load(input_trans_path)['num_empty_facess']

    # split items from datas
    video_paths, audio_paths, names, starts, ends, texts = [], [], [], [], [], []
    for data in datas:
        video_path, audio_path, start, end, text = data.strip().split('|', 4)
        video_name = os.path.split(video_path)[-1]
        video_name = video_name[:len(video_name)-len('_0000.mp4')] # no special sub-index
        names.append(video_name)
        starts.append(start)
        ends.append(end)
        texts.append(text)
        video_paths.append(video_path)
        audio_paths.append(audio_path)

    # merge items
    sub_datas = []
    i, j=0, 1
    while(j<len(datas)):
        if names[i]!=names[j] or same_face(e_embs[i], s_embs[j])==False:
            # merge [i, j-1] [append condition]
            num_faces = sum(num_facess[i:j])
            num_empty_faces = sum(num_empty_facess[i:j])
            face_rate = num_faces/float(num_empty_faces+num_faces)
            if face_rate > min_score:
                sub_datas.append('%s|%s|%s|%s|%s' %(video_paths[i], audio_paths[i], starts[i], ends[j-1], "\t".join(texts[i:j])))
            i = j
        j += 1
    num_faces = sum(num_facess[i:j])
    num_empty_faces = sum(num_empty_facess[i:j])
    if face_rate > min_score:
        sub_datas.append('%s|%s|%s|%s|%s' %(video_paths[i], audio_paths[i], starts[i], ends[j-1], "\t".join(texts[i:j])))
    
    np.savez_compressed(output_trans_path,
                        datas = sub_datas)


## select trans_all.txt with min_len
def filter_len(input_trans_path, output_trans_path, min_len=0):
    datas = np.load(input_trans_path)['datas']
    output = open(output_trans_path, 'w')
    for data in datas:
        video_path, audio_path, start, end, text = data.strip().split('|', 4)
        h,m,s = start.split(':')
        ss = float(h)*60*60+float(m)*60+float(s)
        h,m,s = end.split(':')
        tt = float(h)*60*60+float(m)*60+float(s)
        dur = tt - ss
        if dur > min_len and dur < max_len: output.write('%s\n' %(data))
    output.close()


def main(args):
    face_rec_model_path = 'models/dlib_face_recognition_resnet_model_v1.dat'
    predictor_path = 'models/shape_predictor_68_face_landmarks.dat'

    if args.select_type == 1:
        from dlib_utils import * # can install dlib
        faceDlib = face_dlib(predictor_path, face_rec_model_path, False) # Flase: not cal face emb
        output_path1 = os.path.join(args.data_root, 'trans_all.npz')
        output_path2 = os.path.join(args.data_root, 'trans_all_filter_face.npz')
        output_path3 = args.gene_trans_file
        merge_trans(data_root=args.data_root, output_trans_path=output_path1)
        filter_faces(input_trans_path=output_path1, output_trans_path=output_path2,faceDlib=faceDlib, min_score=args.min_score)
        filter_len(input_trans_path=output_path2, output_trans_path=output_path3, min_len=args.min_len)

    if args.select_type == 2:
        from dlib_utils import *  # can install dlib
        faceDlib = face_dlib(predictor_path, face_rec_model_path, True) # True: cal face emb
        output_path0 = os.path.join(args.data_root, 'trans_all.npz')
        output_path1 = os.path.join(args.data_root, 'trans_all_faces_emb.npz')
        output_path2 = os.path.join(args.data_root, 'trans_all_faces_emb_merge.npz')
        output_path3 = args.gene_trans_file
        merge_trans(data_root=args.data_root, output_trans_path=output_path0)
        filter_faces(input_trans_path=output_path0, output_trans_path=output_path1, faceDlib=faceDlib, min_score=-1) # save all faces
        merge_video(input_trans_path=output_path1, output_trans_path=output_path2, min_score=args.min_score) # filter faces scores
        filter_len(input_trans_path=output_path2, output_trans_path=output_path3, min_len=args.min_len)

    if args.select_type == 3:  # can't install dlib (the faster process)
        output_path0 = os.path.join(args.data_root, 'trans_all.npz')
        output_path3 = args.gene_trans_file
        merge_trans(data_root=args.data_root, output_trans_path=output_path0)
        filter_len(input_trans_path=output_path0, output_trans_path=output_path3, min_len=args.min_len)

if __name__ == '__main__':

    # Gain paramters
    parser = argparse.ArgumentParser(description='filter sub-videos')
    parser.add_argument('--data_root', default='./video_sub', type=str, help='data root for subvideo')
    parser.add_argument('--gene_trans_file', default='./xx/trans_gene.txt', type=str, help='save new transfiles')
    parser.add_argument('--min_len', default=2, type=float, help='min len of subvideo')
    parser.add_argument('--max_len', default=10, type=float, help='max len of subvideo')
    parser.add_argument('--min_score', default=0.5, type=float, help='min face rate in the whole faces')
    parser.add_argument('--select_type', default=1, type=int, help='select type 1 or 2')
    global args
    args = parser.parse_args()

    ## change all <movie,ass> pair into sub videos
    main(args)