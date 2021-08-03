import fugashi
from fugashi import Tagger
import argparse
import os
from collections import Counter
import random
import ntpath

# defaults
N_MOST_COMMON_WORDS = 10 # Top n most common words
INCLUDE_KANA = True # Include on Anki card's Question next to Kanji
INCLUDE_TEXT = False # Include full subtitle
IGNORE_ADDED = False
DEFAULT_DECK_NAME = 'exported.apkg'
IGNORE_FILENAME = 'previous_export_words.txt'
OUTPUT_DIR = 'New_Subs'
SUB_DIR = 'Subtitles'
IGNORE_DIR = 'Ignore_Lists'
MATCH_DIR = 'Match_Lists'
valid_extensions = ['.srt']

# Intialization
tagger = Tagger()
for dir_name in [SUB_DIR, IGNORE_DIR, OUTPUT_DIR, MATCH_DIR]:
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        
# Import match list
match = []
for match_file in [f for f in os.listdir(MATCH_DIR) if f.endswith('.txt')]:
    match_file = os.path.join(MATCH_DIR, match_file)
    with open(match_file, 'r', encoding="utf-8") as file:
        for line in file:
            for word in line.replace(',', '\n').split('\n'):
                for token in tagger(word):
                    match += [token.surface]

parser = argparse.ArgumentParser(description='Convert a japanese subtitle file to a list of the most common words from that file & export as Anki flash card deck.')
parser.add_argument('-s', '--sub', type=str, help='Subtitle path. If arg not used, will process all files in Subtitles dir')
parser.add_argument('-t', '--top', type=int, help='Get the top n most common words. Default 10.')
parser.add_argument('-d', '--drop_kana', action='store_true', help='Dont append kana to exported words.')
parser.add_argument('-i', '--ignore_added', action='store_true', help='Dont add words to the ignore list after each subtitle is analyzed')
parser.add_argument('-list', '--export_list', action='store_true', help='Exports any added words to the ignore list')
parser.add_argument('-skip', '--skip_match', action='store_true', help='Dont filter out words in MATCH_LIST dir')

args = parser.parse_args()
include_kana = not(args.drop_kana)
n_most_common = args.top if args.top else N_MOST_COMMON_WORDS
process_all = args.sub == None

if process_all:
    sub_files = [os.path.join(SUB_DIR, f) for f in os.listdir(SUB_DIR) if f.endswith('|'.join(valid_extensions))]
else:
    sub_files = [args.sub]
sub_files = sorted(sub_files)
    
for sub_idx, sub_file in enumerate(sub_files):       
    
    """
    Part 1: Get n most common Words --------------
    """
    
    # Import ignore list
    ignore = []
    for ignore_file in [f for f in os.listdir(IGNORE_DIR) if f.endswith('.txt')]:
        ignore_file = os.path.join(IGNORE_DIR, ignore_file)
        with open(ignore_file, 'r', encoding="utf-8") as file:
            for line in file:
                ignore += [line.replace('\n', '')]

    all_words = []
    subs = []
    body = []
    with open(sub_file, 'r', encoding="utf-8") as file:
        for i, line in enumerate(file):
            line = line.replace('\ufeff', '')
            if line in ['', ' ']:
                continue

            # Parse sub as list of tuples (timestamps, words)
            if line.strip().isdigit():
                if i > 0:
                    subs += [(body[0], body[1:])]
                body = []
            else:
                body += [line]

            # Split japanese words
            for word in tagger(line):
                all_words += [word.surface]
     
    filtered = [w for w in all_words if w not in ['　'] and w.split()[0] not in ignore and not w.isdigit()]
    if not args.skip_match:
        filtered = [w for w in filtered if w.split()[0] in match]
    print(f'Found {len(all_words)} words, Filtered to {len(filtered)} words')
    word_counts = Counter(filtered)
    
    mc = [word.split()[0] for word, _ in word_counts.most_common()[:n_most_common]]
    print(''.join([str(w) + '\n' for w in word_counts.most_common()[:n_most_common]]))

    # Export new subtitle file with just most common words
    new_sub = []
    idx = 1
    # Iterate subs in sub file
    for time, body in subs:
        match_cnt = 0
        for line in body:
            for word in tagger(line):
                if word.surface in mc:
                    if match_cnt == 0:
                        new_sub += [str(idx)+'\n'] + [time]

                    kana_str = ''
                    if include_kana and word.feature.kana:
                        kana_str = '('+word.feature.kana+')'

                    new_sub += [f'{word.surface} {kana_str}\n']
                    match_cnt += 1

        if match_cnt > 0:
            if INCLUDE_TEXT:
                new_sub += body 
            else:
                new_sub += ['\n']
            idx += 1 

        export_name = ntpath.basename(sub_file).split('.')[0] + '_Top' + str(n_most_common) + '.srt'
        with open(os.path.join(OUTPUT_DIR, export_name), 'w', encoding="utf-8") as file:
            file.writelines([w for w in new_sub])

    # Export words to ignore for future decks
    if IGNORE_ADDED:
        IGNORE_FILENAME = 'previous_export_words.txt'
        ignore_file = os.path.join(IGNORE_DIR, IGNORE_FILENAME)
        new_ignores = skipped + words_added

        if os.path.isfile(ignore_file):
            with open(ignore_file, 'r', encoding="utf-8") as file:
                for line in file:
                    new_ignores += [line.replace('\n', '')]

        new_ignores = sorted(set(new_ignores))

        with open(ignore_file, 'w', encoding="utf-8") as file:
            file.writelines([w + '\n' for w in new_ignores])
    
    ignored = '' if IGNORE_ADDED else ' not'
    print(f'Export complete... Most common words were{ignored} added to the ignore list.')

