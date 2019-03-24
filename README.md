This is an example project that demonstrates how to use the Alveo dataset to create an automatic digit recognition model with Kaldi. For this project, we will pull data from Alveo of various speakers saying various numbers at random, prepare the data for Kaldi, then train Kaldi on the data that has been prepared for it. This guide is based on [http://kaldi-asr.org/doc/kaldi_for_dummies.html] (http://kaldi-asr.org/doc/kaldi_for_dummies.html) which includes some troubleshooting information and more in-depth reading; the guide is built from parts of the Yesno, Voxforge and LibriSpeech examples.

Requirements:
- Python 3
- PyAlveo library for Python
- Pandas library for Python
- Kaldi with OpenFst support and SRILM (see `kaldi/tools/install_srilm.sh`).

To build our dataset, we will use 10 speakers with 10 different audio clips from each speaker, totalling at 100 audio clips. To use the Alveo dataset, you can register for an account [here] (http://app.alveo.edu.au/), then prepare your dataset by using the [AusTalk query tool] (https://austalk-query.apps.alveo.edu.au/). Some scripts have been written for you to simplify the process from start to finish and can be found in this repository.

AusTalk Query will allow you to search through the metadata of over a few hundred thousand audio files as well as their speakers. In your first data set, you should have a mix of male and female speakers, with roughly 10 audio clips from each speaker, totalling us at around 400 words as each speech file has four spoken numbers in total. You may wish to use a less variable dataset by keeping the speaker age fairly narrow (e.g 18-30) with the speaker’s first language as English. After choosing your speakers, export the data as CSV and put it in the root directory of your local repository. Make sure that there are no duplicate digit readouts from the same speaker, Kaldi does not like this.

To run the scripts, you will need to use Python 3, and the dependencies from requirements.txt. Set environment variables `ALVEO_API_URL` to `https://app.alveo.edu.au`, `ALVEO_API_KEY` to your API key obtained on the Alveo website. When set, `python main.py` will begin pulling and setting up some of the data for you. This script will:
- Authenticate with your API key to download the speech files
- Automatically name the downloaded speech files based on their transcription
- Automatically create a ratio for test (20%) and training data (80%) from your dataset
- Generate the ‘wav.scp’, ‘spk2gender’, ‘text’ and ‘utt2spk’ files in both the ‘test’ and ‘train’ directories.
- - These files all have labels automatically generated for you.
- - The utterances are in the format of `SpeakerID__UtteranceID`
- Partially generates the `local` directory
- - Generates `corpus.txt` from your dataset

Now it’s your turn to take care of the remaining files.
1. Create a folder called `dict` inside `data/local`
2. Copy `lexicon.txt` from your Kaldi `/egs/voxforge` directory to `data/local/dict`
3. Create `nonsilence_phones.txt`, `silence_phones.txt` and `optional_silence.txt` in `data/local/dict` (see http://kaldi-asr.org/doc/kaldi_for_dummies.html for examples)
4. Inside the `kaldi_prep` directory, create symlinks for `kaldi/egs/wsj/s5/util` and `kaldi/egs/wsj/s5/steps`.
5. Inside the `kaldi_prep/local` directory (create it), create a symlink for `kaldi/egs/voxforge/s5/local/score.sh`, or simply copy it
6. Create `conf` directory in `kaldi_prep`
7. Create `decode.config` in `conf` directory
```
first_beam=10.0
beam=13.0
lattice_beam=6.0
```
7. Create `mfcc.conf` in `conf` directory
```
--use-energy=false
```
8. Head to the [Kaldi for Dummies guide] (http://kaldi-asr.org/doc/kaldi_for_dummies.html#kaldi_for_dummies_running) and put the scripts into the `kaldi_prep` directory.

Finally, use `run.sh` to start running Kaldi on the prepared data. Sort through the log if there are any problems. Results will be in `kaldi_prep/exp/tri1/decode` and `kaldi_prep/exp/mono/decode` in the form of `wer_{number}`.

### ArchLinux Specific
You make need alias `/usr/bin/python` to `/usr/bin/python23`.
