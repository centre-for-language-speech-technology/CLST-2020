import argparse
import codecs
import os
import sys
import numpy as np
from .praat import textgrid
from pathlib import Path

DATA_TEXT_FILE = 'text'
DATA_SEGMENTS_FILE = 'segments'
DATA_UTT2SPK_FILE = 'utt2spk'
DATA_WAV_SCP_FILE = 'wav.scp'

FOLDER_DICT = 'dict'

DATA_LEXICON = os.path.join(FOLDER_DICT, 'lexicon.txt')
DATA_LEXICONP = os.path.join(FOLDER_DICT, 'lexiconp.txt')
DATA_MISSING_WORDS = os.path.join(FOLDER_DICT, 'missing_words.txt')

CHARACTER_REPLACEMENT = ['++', '<cut-off>', '.', ',', '?', '*r']

# This script is used to prepare a folder for forced alignment
# Author: Lars van Rhijn
# Based on a python2 kaldi script
# Last modified: 29-02-2020
# This script requires the sort command to be installed on the host
# This script also requires a praat folder, containing praat classes and a utils folder containing utt2spk_to_spk2utt.pl


# Opens files to store content, files must be located in one data folder
def open_content_files(data_folder):
    fid_txt = codecs.open(os.path.join(data_folder, DATA_TEXT_FILE), "w", "utf-8")
    fid_seg = codecs.open(os.path.join(data_folder, DATA_SEGMENTS_FILE), "w", "utf-8")
    fid_utt = codecs.open(os.path.join(data_folder, DATA_UTT2SPK_FILE), "w", "utf-8")
    fid_wav = codecs.open(os.path.join(data_folder, DATA_WAV_SCP_FILE), "w", "utf-8")

    return fid_txt, fid_seg, fid_utt, fid_wav


# Opens dict files to store content, files must be located in one data folder
def open_dict_files(data_folder):
    part_dict = codecs.open(os.path.join(data_folder, DATA_LEXICON), "w", "utf-8")
    dictp = codecs.open(os.path.join(data_folder, DATA_LEXICONP), "w", "utf-8")
    missing = codecs.open(os.path.join(data_folder, DATA_MISSING_WORDS), "w", "utf-8")

    return part_dict, dictp, missing


# Opens dictionary file
def open_dictionary(dict_file):
    return codecs.open(dict_file, "rb", "utf-8")


# Reads the trans tier from a textgrid file
def get_trans_tier(textgrid_file, align_tier_name):
    textgrid_fp = textgrid.Textgrid()
    textgrid_fp.read(textgrid_file)
    return textgrid_fp.get_tier_by_name(align_tier_name)


# Replaces characters with empty string
def replace_characters_with_empty(string):
    for characters in CHARACTER_REPLACEMENT:
        string = string.replace(characters, '')
    return string


# Reads a buffer from trans_tier intervals
def receive_buffer_from_trans_tier(trans_tier, spkr_noise_sym, gen_noise_sym):
    text_buffer = list()
    s_time_buffer = list()
    e_time_buffer = list()
    for interval in trans_tier.intervals:
        if interval.text != "" and '<empty>' not in interval.text and '<leeg>' not in interval.text:
            text = replace_characters_with_empty(interval.text)
            text = ''.join(c for c in text if c not in ('!', '.', ':', '?', ',', '\n', '\r', '"', '|', ';', '(', ')', '[', ']', '{', '}', '#', '_', '+', '&lt', '&gt', '\\'))
            fields = text.lower().split()
            for ele in fields:
                if '*' in ele or 'xxx' in ele or 'mm' in ele or 'ggg' in ele:
                    ind=fields.index(ele)
                    fields[ind]=args.spkr_noise_sym
                elif '<opn>' in ele or '<spk>' in ele:
                    ind=fields.index(ele)
                    fields[ind]=args.spkr_noise_sym
            text = ' '.join(fields)
            temp=text.strip().lower().split()
            text = ' '.join(temp)
            text = text.replace(spkr_noise_sym.lower(), spkr_noise_sym).replace(gen_noise_sym.lower(), gen_noise_sym).replace("<sil>", "<SIL>")
            text_buffer.append(text)
            s_time_buffer.append("{:.3f}".format(interval.btime))
            e_time_buffer.append("{:.3f}".format(interval.etime))

    return text_buffer, s_time_buffer, e_time_buffer


# Computes the fid file data
def get_fid_file_data(text_buffer, speaker, file_path, text, speaker_adapt):
    new_wav = ''
    new_txt = ''
    new_seg = ''
    new_utt = ''

    utt_id = Path(file_path).stem

    if speaker_adapt == 'SA' and text != '' and text_buffer != []:
        new_wav = new_wav + utt_id + ' ' + file_path + '\n'
        new_txt = new_txt + utt_id + ' ' + ' '.join(text_buffer) + '\n'
        new_seg = new_seg + utt_id + ' ' + utt_id + ' ' + s_time_buffer[0] + ' ' + e_time_buffer[-1] + '\n'
        new_utt = new_utt + utt_id + ' ' + speaker + '\n'
    elif speaker_adapt == 'SI' and text != '' and text_buffer != []:
        new_wav = new_wav + utt_id + ' ' + file_path
        new_txt = new_txt + utt_id + ' ' + ' '.join(text_buffer) + '\n'
        new_seg = new_seg + utt_id + ' ' + utt_id + ' ' + s_time_buffer[0] + ' ' + e_time_buffer[-1] + '\n'
        new_utt = new_utt + utt_id + ' ' + utt_id + '_' + str("{:04.0f}".format(0)) + '\n'

    return new_wav, new_txt, new_seg, new_utt


# Writes data to fid files
def write_to_fid_files(data_folder, speaker, file_path, text_buffer, text, speaker_adapt):
    fid_txt, fid_seg, fid_utt, fid_wav = open_content_files(data_folder)

    new_wav, new_txt, new_seg, new_utt = get_fid_file_data(text_buffer, speaker, file_path, text, speaker_adapt)

    fid_txt.write(new_txt)
    fid_seg.write(new_seg)
    fid_utt.write(new_utt)
    fid_wav.write(new_wav)

    fid_txt.close()
    fid_seg.close()
    fid_utt.close()
    fid_wav.close()


# Creates dict files and writes corresponding data to them
def create_dict_files(data_folder, spkr_noise_sym, tg_file, dict_file):
    full_dict = open_dictionary(dict_file)

    part_dict, dictp, missing = open_dict_files(data_folder)

    part_dict.write("<SIL>\tSIL\n")
    part_dict.write(args.spkr_noise_sym + "\t[SPN]\n")
    part_dict.write("<UNK>\t[SPN]\n")
    dictp.write("<SIL>\t1.0\tSIL\n")
    dictp.write(args.spkr_noise_sym + "\t1.0\t[SPN]\n")
    dictp.write("<UNK>\t1.0\t[SPN]\n")

    lexicon = full_dict.read()
    newlexicon = []

    lexicon = lexicon.split("\n")
    for words in lexicon:
        words = words.split("\t")
        words = list(words)
        newlexicon.append(words)
    newlexicon.pop()

    newlexicon = np.asarray(newlexicon)

    wordset = set()
    [wordset.add(word) for word in text.split()]

    for word in wordset:
        print(word)
        if word not in [spkr_noise_sym, "<UNK>", "<SIL>"]:
            found = False
            for dictword in newlexicon:
                if word == dictword[0]:
                    dictline = dictword[0] + "\t" + dictword[1] + "\n"
                    part_dict.write(dictline)
                    dictpline = dictword[0] + "\t" + "1.0" + "\t" + dictword[1] + "\n"
                    dictp.write(dictpline)
                    found = True
            if not found:
                missing.write(tg_file + "\t" + word + "\n")

    missing.close()
    part_dict.close()
    dictp.close()


# Run as: python3 data_prep.py --speaker_adapt [SA/SI] --wav_file [wav_file] --tg_file [corresponding_tg_file]
# --data_folder [folder_to_store_output_files] --align_tier_name [transcription] --dict_file [dictionary_to_use]
# --speaker [speaker_name]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lexicon preparation')
    parser.add_argument('--speaker_adapt', help='indicates speaker dependent or independent recognition. values: SA or SI resp.', type=str, required=True)
    parser.add_argument('--wav_file', help='the wav file that is being preprocessed', type=str, required=True)
    parser.add_argument('--tg_file', help='the tg file corresponding to the wav file', type=str, required=True)
    parser.add_argument('--data_folder', help='the data folder with the dictionaries, text, segments, utt2spk and wav.scp files', type=str,required=True)
    parser.add_argument('--align_tier_name', help='Prepare the text from the tier with this name in every textgrid file. Default: transcription', type=str, default="transcription")
    parser.add_argument('--dict_file', help='Main lexicon that contains phoneme translations of regular words.', type=str, required=True)
    parser.add_argument('--spkr_noise_sym', help='The word in the lexicon denoting speaker noise (e.g. lip smacks, tongue clicks, heavy breathing, etc). Default: <SPN>', \
        type=str, default=u"<SPN>")
    parser.add_argument('--gen_noise_sym', help='The word in the lexicon denoting general noise (e.g. environmental, microphone clicks, etc.). Default: <NSN>', \
        type=str, default=u"<NSN>")
    parser.add_argument('--speaker', help='Name of the speaker in the wav file.', required=True, type=str)

    args = parser.parse_args()

    trans_tier = get_trans_tier(args.tg_file, args.align_tier_name)
    if trans_tier is None:
        sys.stderr.write("Error in processing file '" + args.tg_file + "'! Could not find tier '" + args.align_tier_name + "' to process!\nAborting...\n")
        sys.exit(1)

    text_buffer, s_time_buffer, e_time_buffer = receive_buffer_from_trans_tier(trans_tier, args.spkr_noise_sym, args.gen_noise_sym)

    text = ' '.join(text_buffer)

    write_to_fid_files(args.data_folder, args.speaker, args.wav_file, text_buffer, text, args.speaker_adapt)

    create_dict_files(args.data_folder, args.spkr_noise_sym, args.tg_file, args.dict_file)

    os.system('env LC_ALL=C sort -o ' + args.data_folder + '/text' + ' ' + args.data_folder + '/text')
    os.system('env LC_ALL=C sort -o ' + args.data_folder + '/segments' + ' ' + args.data_folder + '/segments')
    os.system('env LC_ALL=C sort -u -o  ' + args.data_folder + '/wav.scp' + ' ' + args.data_folder + '/wav.scp')
    os.system('env LC_ALL=C sort -o ' + args.data_folder + '/utt2spk' + ' ' + args.data_folder + '/utt2spk')
    os.system('utils/utt2spk_to_spk2utt.pl ' + args.data_folder + '/utt2spk' + ' > ' + args.data_folder + '/spk2utt')
