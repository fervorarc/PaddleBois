import numpy as np
import numpy
import paramiko
from scp import SCPClient
import cv2
import os.path
import urllib
import json
import requests
import scipy
import math
from scipy import spatial
import tarfile,sys

HOSTNAME = '35.167.14.53'
PORT_sentiment_analysis = 8000
PORT_machine_translation = 6000
PORT_image_recognition = 2000
IMAGE_SIZE = 28

#BACKEND_URL = "ip-172-31-42-171"
# 1
class word2vec:

    word_dict = dict()
    embedding_table = ""

    def __init__(self):
        self.load_files()
        self.word_dict = dict()
        with open("models/word2vec/word_dict", "r") as f:
            for line in f:
                key, value = line.strip().split(" ")
                self.word_dict[key] = value
        self.embedding_table = numpy.loadtxt("models/word2vec/embedding_table", delimiter=",")

    def run(self, s1, s2):
        i1 = int(self.word_dict[s1])
        i2 = int(self.word_dict[s2])

        print(spatial.distance.cosine(self.embedding_table[i1], self.embedding_table[i2]))
        return spatial.distance.cosine(self.embedding_table[i1], self.embedding_table[i2])

    def load_files(self):
        if not os.path.isdir("models/word2vec/"):
            os.mkdir("models/word2vec/")

        if not os.path.isfile("models/word2vec/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/04.word2vec/inference_topology.pkl",
                               "models/word2vec/inference_topology.pkl")
            print("Loading models/word2vec/inference_topology.pkl . . .")

        if not os.path.isfile("models/word2vec/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/04.word2vec/param.tar",
                               "models/word2vec/param.tar")
            extract_tar("models/word2vec/param.tar")
            print("Loading models/word2vec/param.tar . . .")

        if not os.path.isfile("models/word2vec/word_dict"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/04.word2vec/word_dict",
                               "models/word2vec/word_dict")
            print("Loading models/word2vec/word_dict . . .")

        if not os.path.isfile("models/word2vec/embedding_table"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/04.word2vec/embedding_table",
                               "models/word2vec/embedding_table")
            print("Loading models/word2vec/embedding_table . . .")

# 2
class image_classification:

    def __init__(self):
        self.load_files()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file("hackmit-paddlepaddle-1.pem")
        client.connect(hostname='35.167.14.53', username='ubuntu',pkey=k)
        scp = SCPClient(client.get_transport())
        stdin, stdout, stderr = client.exec_command('mkdir models')
        stdin, stdout, stderr = client.exec_command('mkdir models/image_classification')
        client.exec_command('cd models/image_classification')

        #move files to remote server
        scp.put('models/image_classification/inference_topology.pkl','models/image_classification/inference_topology.pkl') 
        scp.put('models/image_classification/param.tar','models/image_classification/param.tar') 
       
        #run docker commamdn
        stdin, stdout, stderr = client.exec_command('nvidia-docker run --name=my_svr -v `pwd`:/data -d -p 8000:80 -e WITH_GPU=1 paddlepaddle/book:serve-gpu')
        scp.close()
        client.close()


    def load_files(self):
        if not os.path.isdir("models/image_classification/"):
            os.mkdir("models/image_classification/")
            print("making image_classification dir")

        if not os.path.isfile("models/image_classification/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/03.image_classification/inference_topology.pkl",
                               "models/image_classification/inference_topology.pkl")
            print("Loading models/image_classification/inference_topology.pkl . . .")

        if not os.path.isfile("models/image_classification/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/03.image_classification/param.tar",
                               "models/image_classification/param.tar")
            extract_tar("models/image_classification/param.tar")
            print("Loading models/image_classification/param.tar . . .")

    def run(self, img_file):
        BACKEND_URL = "http://35.167.14.53:8000"
        img = cv2.imread(img_file)
        print("read in image")
        img = np.swapaxes(img, 1, 2)
        img = np.swapaxes(img, 1, 0)
        arr = img.flatten()
        arr = arr / 255.0
        req = {"image": arr.tolist()}
        print(req)
        res = requests.request("POST", url=BACKEND_URL, json=req)
        print("printing json")
        print(json.dumps(res.json()))


# 3
class sentiment_classification:

    def __init__(self):
        self.load_files()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file("hackmit-paddlepaddle-1.pem")
        client.connect(hostname='35.167.14.53', username='ubuntu',pkey=k)
        scp = SCPClient(client.get_transport())
        stdin, stdout, stderr = client.exec_command('mkdir models')
        stdin, stdout, stderr = client.exec_command('mkdir models/sentiment_classification')
        client.exec_command('cd models/sentiment_classification')

        #move files to remote server
        scp.put('models/sentiment_classification/inference_topology.pkl','models/sentiment_classification/inference_topology.pkl') 
        scp.put('models/sentiment_classification/param.tar','models/sentiment_classification/param.tar') 
        scp.put('models/sentiment_classification/word_dict.tar','models/sentiment_classification/word_dict.tar')
       
        #run docker commamdn
        stdin, stdout, stderr = client.exec_command('docker run --name sentimentdocker -v `pwd`:/data -d -p 3000:80 -e WITH_GPU=0 paddlepaddle/book:serve')
        scp.close()
        client.close()


    def load_files(self):
        if not os.path.isdir("models/sentiment_classification/"):
            os.mkdir("models/sentiment_classification/")
            print("Making sentiment_classification dir")

        if not os.path.isfile("models/sentiment_classification/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/06.understand_sentiment/inference_topology.pkl",
                               "models/sentiment_classification/inference_topology.pkl")
            print("Loading models/sentiment_classification/inference_topology.pkl . . .")

        if not os.path.isfile("models/sentiment_classification/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/06.understand_sentiment/param.tar",
                               "models/sentiment_classification/param.tar")
            extract_tar("models/sentiment_classification/param.tar")
            print("Loading models/sentiment_classification/param.tar . . .")

        if not os.path.isfile("models/sentiment_classification/word_dict.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/06.understand_sentiment/word_dict.tar",
                               "models/sentiment_classification/word_dict.tar")
            extract_tar("models/sentiment_classification/word_dict.tar")
            print("Loading models/sentiment_classification/word_dict.tar . . .")

    def run(self, indices):
        BACKEND_URL = "http://35.167.14.53:3000"
        req = {"word":indices}
        print(req)
        res = requests.request("POST", url=BACKEND_URL, json=req)
        print(json.dumps(res.json()))



# 4
class machine_translation:

    def __init__(self):
        self.load_files()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file("hackmit-paddlepaddle-1.pem")
        client.connect(hostname='35.167.14.53', username='ubuntu',pkey=k)
        scp = SCPClient(client.get_transport())
        stdin, stdout, stderr = client.exec_command('mkdir models')
        stdin, stdout, stderr = client.exec_command('mkdir models/machine_translation')
        client.exec_command('cd models/machine_translation')
        client.exec_command('docker run --name mcn_trl_svr -v $(pwd):/data -d -p 6000:80 -e WITH_GPU=0 -e OUTPUT_FILE=prob, id paddlepaddle/book:serve')
        scp.put('models/machine_translation/inference_topology.pkl',
                'models/machine_translation/inference_topology.pkl')
        scp.put("models/machine_translation/param.tar",
                "models/machine_translation/param.tar")
        scp.put("models/machine_translation/src_dict.txt",
                "models/machine_translation/src_dict.txt")
        scp.put("models/machine_translation/trg_dict.txt",
                "models/machine_translation/trg_dict.txt")
        scp.close()
        client.close()

    def load_files(self):
        if not os.path.isdir("models/machine_translation/"):
            os.mkdir("models/machine_translation/")
            print("making machine_translation dir")

        if not os.path.isfile("models/machine_translation/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/08.machine_translation/inference_topology.pkl",
                               "models/machine_translation/inference_topology.pkl")
            print("Loading models/machine_translation/inference_topology.pkl . . .")

        if not os.path.isfile("models/machine_translation/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/08.machine_translation/param.tar",
                               "models/machine_translation/param.tar")
            extract_tar("models/machine_translation/param.tar")
            print("Loading models/machine_translation/param.tar . . .")

        if not os.path.isfile("models/machine_translation/src_dict.txt"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/08.machine_translation/src_dict.txt",
                               "models/machine_translation/src_dict.txt")
            print("Loading models/machine_translation/src_dict.txt . . .")

        if not os.path.isfile("models/machine_translation/trg_dict.txt"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/08.machine_translation/trg_dict.txt",
                               "models/machine_translation/trg_dict.txt")
            print("Loading models/machine_translation/trg_dict.txt . . .")

    def run(self, sample):
        src_dic_path = 'data/src_dict.txt'
        trg_dic_path = 'data/trg_dict.txt'

        r = requests.post("http://35.167.14.53:6000/",
                json = {'source_language_word': sample})

        # get result
        data = eval(r.text)
        beam_result = map(np.array, data['data'])

        beam_size = 3
        gen_data = [1]

        def load_dic(path):
            words = []
            with open(path) as f:
                for line in f:
                    words.append(line.strip())
            return words

        # load the dictionary
        src_dict, trg_dict = load_dic(src_dic_path), load_dic(trg_dic_path)

        gen_sen_idx = np.where(beam_result[1] == -1)[0]
        assert len(gen_sen_idx) == len(gen_data) * beam_size

        # -1 is the delimiter of generated sequences.
        # the first element of each generated sequence its length.
        start_pos, end_pos = 1, 0

        # source sentence
        print(" ".join(src_dict[w] for w in sample))

        for j in range(beam_size):
            end_pos = gen_sen_idx[j]
            prob = math.exp(beam_result[0][0][j])
            print("%dth %.6f\t%s" % (j, prob, " ".join(trg_dict[w] for w in beam_result[1][start_pos:end_pos])))
            start_pos = end_pos + 2


# 5
class recognize_digits:

    def __init__(self):
        self.load_files()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file("hackmit-paddlepaddle-1.pem")
        client.connect(hostname='35.167.14.53', username='ubuntu',pkey=k)
        scp = SCPClient(client.get_transport())
        stdin, stdout, stderr = client.exec_command('mkdir models')
        stdin, stdout, stderr = client.exec_command('mkdir models/recognize_digits')
        client.exec_command('cd models/recognize_digits')

        #move files to remote server
        scp.put('models/recognize_digits/inference_topology.pkl','models/recognize_digits/inference_topology.pkl') 
        scp.put('models/recognize_digits/param.tar','models/recognize_digits/param.tar') 
       
        #run docker commamdn
        stdin, stdout, stderr = client.exec_command('nvidia-docker run --name my_svr -d -v $PWD:/data -p 2000:80 -e WITH_GPU=1 paddlepaddle/book:serve-gpu')
        scp.close()
        client.close()





    def load_files(self):
        if not os.path.isdir("models/recognize_digits/"):
            os.mkdir("models/recognize_digits/")
            print("making recognizing_digits dir")

        if not os.path.isfile("models/recognize_digits/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/inference_topology.pkl",
                               "models/recognize_digits/inference_topology.pkl")
            print("Loading models/recognize_digits/inference_topology.pkl . . .")

        if not os.path.isfile("models/recognize_digits/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/param.tar",
                              "models/recognize_digits/param.tar")
            extract_tar("models/recognize_digits/param.tar")
            print("Loading models/recognize_digits/param.tar . . .")

    def run(self, img_file):
        BACKEND_URL = "http://35.167.14.53:2000"
        img = cv2.imread(img_file, 0)
        img.resize((IMAGE_SIZE, IMAGE_SIZE))
        img = img.flatten()
        req = {"img": img.tolist()}
        res = requests.request("POST", url=BACKEND_URL, json=req)
        print("printing json")
        print(json.dumps(res.json()))



# 6
class object_detection:

    def __init__(self):
        self.load_files()

    def load_files(self):
        if not os.path.isfile("models/object_detection/inference_topology.pkl"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/SSD/inference_topology.pkl",
                               "models/object_detection/inference_topology.pkl")
            print("Loading models/object_detection/inference_topology.pkl . . .")

        if not os.path.isfile("models/object_detection/param.tar"):
            urllib.request.urlretrieve("https://s3.us-east-2.amazonaws.com/models.paddlepaddle/SSD/param.tar",
                              "models/object_detection/param.tar")
            extract_tar("models/object_detection/param.tar")
            print("Loading models/object_detection/param.tar . . .")


def extract_tar(file_path):
    tar = tarfile.open(file_path)
    tar.extractall()
    tar.close()
