# process on videos in one dir './video'

##### video #####
# #### step 1: gain all subvideo to save_root
# python video_seg_lian.py --data_root='./video' --save_root='./video_sub' --max_len_one_video=-1

# #### step 2: generate gene_trans_file according to select_type (three select_type: 1,2,3)
# #CUDA_VISIBLE_DEVICES=1 python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=1 --min_len=1 --min_score=0.5  ## select_type=1
# #CUDA_VISIBLE_DEVICES=1 python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=2 --min_len=1 --min_score=0.5  ## select_type=2
# python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=3 --min_len=4 ## select_type=3


# #### step 3: analyze gene_trans_file and save collect video into save_root
# python video_seg_lian.py --data_root='./video' --save_root='./video_sub_sub' --gene_trans_file='./video_sub/trans_gene.txt' --max_len_one_video=-1




##### video2 #####
#### step 1: gain all subvideo to save_root
python video_seg_lian.py --data_root='./video2' --save_root='./video2_sub' --max_len_one_video=-1

#### step 2: generate gene_trans_file according to select_type (three select_type: 1,2,3)
#CUDA_VISIBLE_DEVICES=1 python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=1 --min_len=1 --min_score=0.5  ## select_type=1
#CUDA_VISIBLE_DEVICES=1 python video_select.py --data_root='./video_sub' --gene_trans_file='./video_sub/trans_gene.txt' --select_type=2 --min_len=1 --min_score=0.5  ## select_type=2
python video_select.py --data_root='./video2_sub' --gene_trans_file='./video2_sub/trans_gene.txt' --select_type=3 --min_len=4 --max_len=10 ## select_type=3


#### step 3: analyze gene_trans_file and save collect video into save_root
python video_seg_lian.py --data_root='./video2' --save_root='./video2_sub_sub' --gene_trans_file='./video2_sub/trans_gene.txt' --max_len_one_video=-1
