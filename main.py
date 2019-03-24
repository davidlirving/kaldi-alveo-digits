# Author: David L. Irving (david.l.irving@gmail.com)

import os
import sys
from inspect import getsourcefile
from generator import gen_set_data
from generator import gen_local_data
from generator import gen_internal_data

import pandas as pd
import pyalveo

# Set up our environment variable dict
settings = {
    'ALVEO_API_URL': {
        'required': True,
        'value': None 
    },
    'ALVEO_API_KEY': {
        'required': True,
        'value': None
    }
}

# Load all environment variables
for key in settings:
    setting = settings[key]
    setting['value'] = os.environ.get(key)
    if setting['required'] and setting['value'] == None:
        print('%s environment variable is not set. Cannot proceed.' % key)
        sys.exit()

audio_data_dir = './audio_data'
dataset_csv_path = 'dataset.csv'
kaldi_data_dir = './kaldi'
train_dir = os.path.join(kaldi_data_dir, "data/train")
test_dir = os.path.join(kaldi_data_dir, "data/test")
local_dir = os.path.join(kaldi_data_dir, "data/local")

# Describe our word dictionary for our digits
digit_dict = {
    'oh': '0',
    'zero': '0',
    'one': '1',
    'two': '2',
    'three': '3',
    'four': '4',
    'five': '5',
    'six': '6',
    'seven': '7',
    'eight': '8',
    'nine': '9',
    ' ': '_'
}

print('Loading PyAlveo...')
client = pyalveo.Client(
    api_url=settings['ALVEO_API_URL']['value'],
    api_key=settings['ALVEO_API_KEY']['value'],
    cache_dir=os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
)
print('PyAlveo loaded successfully.')

print('Importing CSV %s...' % dataset_csv_path)
df = pd.read_csv(dataset_csv_path)
# Add extra columns for our use
df['number_prompt'] = None
df['saved_file_path'] = None
df['utterance_id'] = None
df['prompt_fmt'] = None

# We need this because our CSV doesn't tell us exactly where the item is at
item_prefix = 'catalog/austalk/' 

# Create our needed directories
if not os.path.exists(audio_data_dir):
    print('Creating %s...' % audio_data_dir)
    os.makedirs(audio_data_dir)

# Create a directory for each speaker_id, inside audio_data_dir
print('Creating speaker directories...')
for speaker in df['speaker'].unique():
    path = os.path.join(audio_data_dir, speaker)
    if not os.path.exists(path):
        print('mkdir %s' % path)
        os.makedirs(path)

print('Caching data...')
df = gen_internal_data(
    df,
    digit_dict=digit_dict,
    audio_data_dir=audio_data_dir
)

print('Sorting data for Kaldi...')
df = df.sort_values('speaker')
df = df.sort_values('utterance_id')

print('Preparation complete. \n\nRetrieving data...')
# Format our 'prompt' column into their numbers
for index, row in df.iterrows():
    # Generate the paths for the file, locally and remotely
    file_path = row['saved_file_path']
    speechfile_url = item_prefix + row['item'] + '/document/' + row['media']

    # Download the wave file into the correct directory
    print('Downloading %s -> %s' % (speechfile_url,file_path))
    doc = client.get_document(speechfile_url)
    with open(file_path, 'wb') as wav:
        wav.write(doc)

# Next, we'll need to start generating data such as wav.scp (connecting utterances to speakers)
# text - <utterance ID> <prompt>
# utt2spk - <utterance ID> <speaker ID>
# corpus - one line per audio file

# Create our kaldi dataset directory
if not os.path.exists(kaldi_data_dir):
    print('Creating %s...' % kaldi_data_dir)
    os.makedirs(kaldi_data_dir)
if not os.path.exists(train_dir):
    print('Creating %s...' % train_dir)
    os.makedirs(train_dir)
if not os.path.exists(test_dir):
    print('Creating %s...' % test_dir)
    os.makedirs(test_dir)
if not os.path.exists(local_dir):
    print('Creating %s...' % test_dir)
    os.makedirs(local_dir)

train_set = df.sample(frac=0.8, random_state=100)
test_set = df.drop(train_set.index)
train_set = train_set.sort_values('speaker')
train_set = train_set.sort_values('utterance_id')
test_set = test_set.sort_values('speaker')
test_set = test_set.sort_values('utterance_id')

print("Generating train dataset...")
gen_set_data(train_set, train_dir)
print("Generating test dataset...")
gen_set_data(test_set, test_dir)
print("Generating local data...")
gen_local_data(df, local_dir)

print('All operations completed successfully.')
