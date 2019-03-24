import os

def numerate(text, word_dict):
    """
        Replaces all instances of %text with everything contained in %word_dict
    """
    for i, j in word_dict.items():
        text = text.replace(i, j)
    return text

def gen_internal_data(df, digit_dict, audio_data_dir):
    """
        Generates data that we use internally, so that we can generate data in an
        easy to read fashion.
    """
    for index, row in df.iterrows():
        row['number_prompt'] = numerate(row['prompt'], digit_dict)
        row['saved_file_path'] = os.path.abspath(
            os.path.join(audio_data_dir, row['speaker'], '%s.wav' % row['number_prompt'])
        )
        row['utterance_id'] = "%s__%s" % (row['speaker'], row['number_prompt'])
        row['prompt_fmt'] = row['prompt'].replace(', ', ' ')
    return df

def gen_wavscp(df, file_path):
    """
        Generate wav.scp file
        <utterance_id> <absolute_file_path>

        We use the folder__filename for the utterance ID, without an extension.
        e.g 1_122__1_2_1_9
    """
    data = ""
    for index, row in df.iterrows():
        data += "%s %s\n" % (
            row['utterance_id'],
            row['saved_file_path']
        )

    with open(file_path, 'w') as data_file:
        data_file.write(data)

def gen_text(df, file_path):
    """
        Generate our text file
        Associate the prompt with the utterance_ID we've created in wav.scp

        <utterance_id> number_one number_two number_three number_four
        e.g
            1_248__3_2_4_4 three two four four
            1_242__1_0_9_2 one zero nine two
    """
    data = ""
    for index, row in df.iterrows():
        data += '%s %s\n' % (
            row['utterance_id'],
            row['prompt_fmt']
        )

    with open(file_path, 'w') as data_file:
        data_file.write(data)

def gen_utt2spk(df, file_path):
    """
        Associate all the utterance_ids with a speaker_id
    """
    data = ""
    for index, row in df.iterrows():
        data += '%s %s\n' % (
            row['utterance_id'],
            row['speaker']
        )

    with open(file_path, 'w') as data_file:
        data_file.write(data)

def gen_corpus(df, file_path):
    """
        Generate corpus
        This file has one line with a transcription of all audio
    """
    data = ""
    for index, row in df.iterrows():
        data += '%s \n' % row['prompt_fmt']

    with open(file_path, 'w') as data_file:
        data_file.write(data)

def gen_set_data(df, output_dir):
    """
        Generate all of our needed data for a specific set (e.g test/train)
    """
    print("Generating wav.scp...")
    gen_wavscp(df, os.path.join(output_dir, 'wav.scp'))
    print("Generating text...")
    gen_text(df, os.path.join(output_dir, 'text'))
    print("Generating utt2spk...")
    gen_utt2spk(df, os.path.join(output_dir, 'utt2spk'))

def gen_local_data(df, output_dir):
    """
        Generate all of the needed data for the local dir
    """
    print("Generating corpus...")
    gen_corpus(df, os.path.join(output_dir, 'corpus.txt'))
