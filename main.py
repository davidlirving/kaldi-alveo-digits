# Author: David L. Irving (david.l.irving@gmail.com)

import os
import sys
from inspect import getsourcefile

import pandas as pd
import pyalveo

AAU_ENV_NAME = 'ALVEO_API_URL'
AAK_ENV_NAME = 'ALVEO_API_KEY'

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

for key in settings:
    setting = settings[key]
    setting['value'] = os.environ.get(key)
    if setting['required'] and setting['value'] == None:
        print('%s environment variable is not set. Cannot proceed.' % key)
        sys.exit()

audio_data_dir = './audio_data'
dataset_csv_path = 'dataset.csv'

word_dict = {
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
    #use_cache=False, # Means not to download if it isn't cached, which doesn't seem quite clear
    #update_cache=True, # This means to store the value in cache if we alter something
    cache_dir=os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
)
print('PyAlveo loaded successfully.')

print('Importing CSV %s...' % dataset_csv_path)
df = pd.read_csv(dataset_csv_path)

# We need this because our CSV doesn't tell us exactly where the item is at
item_prefix = 'catalog/austalk/' 

def numerate(text):
    for i, j in word_dict.items():
        text = text.replace(i, j)
    return text

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

print('Preparation complete. \n\nRetrieving data...')
# Format our 'prompt' column into their numbers
for index, row in df.iterrows():
    row['prompt'] = numerate(row['prompt'])

    # Generate the paths for the file, locally and remotely
    file_path = os.path.join(audio_data_dir, row['speaker'], '%s.wav' % row['prompt'])
    speechfile_url = item_prefix + row['item'] + '/document/' + row['media']

    # Download the wave file into the correct directory
    print('Downloading %s -> %s' % (speechfile_url,file_path))
    doc = client.get_document(speechfile_url)
    with open(file_path, 'wb') as wav:
        wav.write(doc)

print('All operations completed successfully.')