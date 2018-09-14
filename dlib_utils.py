import os
import re
import glob
import dlib
from tqdm import tqdm
import numpy as np
import cv2
import argparse

## cal similaity of faces
def same_face(data1, data2):
    if data1==None or data2==None:
        return False
    diff = 0
    for i in range(len(data1)):
        diff += (data1[i] - data2[i])**2
    diff = np.sqrt(diff)
    if(diff < 0.6):
        return True
    else:
        return False

class face_dlib(object):
    # face_flag: whether return face embedding. If ture, mush have 'face_rec_model_path'
    def __init__(self, predictor_path, face_rec_model_path, face_flag):
        self.face_flag=face_flag
        self.predictor_path=predictor_path
        self.face_rec_model_path=face_rec_model_path
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.predictor_path)
        self.facerec = dlib.face_recognition_model_v1(self.face_rec_model_path)
        assert (face_flag==True and face_rec_model_path!=None) or (face_flag==False)


    ## gain embedding of faces
    def pic_embedding(self, pic_path):
        img = cv2.imread(pic_path)
        dets = self.detector(img, 1)
        if len(dets)==0: return None
        shape = self.predictor(img, dets[0])
        face_descriptor = self.facerec.compute_face_descriptor(img, shape)
        return face_descriptor

    ## return face_rate scores: which shows how much frames has faces
    def face_rate_scores(self, video_path):
        video_root = os.path.split(video_path)[0]
        temp_face_folder = os.path.join(video_root, 'temp_face')

        # split video into frames   
        if os.path.exists(temp_face_folder): os.system('rm -rf %s' %(temp_face_folder))
        if not os.path.exists(temp_face_folder): os.makedirs(temp_face_folder)
        cmd = 'ffmpeg -loglevel quiet -i %s -q:v 2 %s' %(video_path, temp_face_folder+'/%4d.jpg')
        os.system(cmd)

        # calculate face_rate
        num_empty_faces = 0
        num_faces = 0
        img_paths = np.sort(glob.glob(os.path.join(temp_face_folder, "*")))
        for f in img_paths:
            img = cv2.imread(f)
            dets = self.detector(img, 1)
            if len(dets) == 0:
                num_empty_faces += 1
            else:
                num_faces += 1
        print("%s: Number of empty faces: %d   Number of faces: %d" %(video_path, num_empty_faces, num_faces))
        
        # gain face embedding of (start, end) frames
        s_emb, e_emb = None, None
        if self.face_flag==True:
            s_emb = self.pic_embedding(img_paths[0])
            e_emb = self.pic_embedding(img_paths[-1])

        # del temp fold
        cmd = 'rm -rf %s' %(temp_face_folder)
        os.system(cmd)
        return (num_empty_faces, num_faces, s_emb, e_emb)

        
