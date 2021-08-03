References:
- https://github.com/polm/fugashi#installing-a-dictionary
- https://github.com/PokiDokika/jisho-py

Subtitle Sites:
- https://kitsunekko.net

# How it works
Download a japanese subtitle file. This tool will parse that file and give you the n most common japanese words used. These words will be exported to a new subtitle file with the same time stamps, but only where those words occur.

# Dependencies
- fugashi - package for japanese language tokenization (I'm using it to break the corpus in to separate words)

Currently not using jisho, but may use later to filter out words not found in the dictionary:
- jisho-py - package creates a python api to jisho.org japanese dictionary and returns results with japanese kanji & kana as well as english translations
Note: jisho-py currently must be copied to the site-packages directory because it's pip installation is broken. Just import a package like import numpy as np, then `print(np.__file__)` to get the site-packages location

# Usage
- Export subtitle file with the 10 most common words (default)
    ```
    python subjaptop.py
    ```
- Export subtitle file with the 20 most common words
    ```
    python subjaptop.py --top 20
    ```
- Allow words outside N5-N1 core dictionary (You can also add your own words to MATCH_LISTS dir)
    ```
    python subjaptop.py --skip_match
    ```
    
### optional arguments:
```
  -s, --sub Subtitle path. If arg not used, will process all files in Subtitles dir
  -t, --top Get the top n most common words. Default 10.
  -d, --drop_kana Dont append kana to exported words.
  -i, --ignore_added Exports any added words to the ignore list. Default False
``` 

Notes
- All words will automatically be added to the ignore list under the `IGNORE_LIST/previous_export_words.txt` unless the `--ignore_added True` argument is used.
- The anki deck's card answer will be limited to how many lines are added with the `--max_lines` arg (default 10). The code will continue to iterate words and definitions on jisho.org until the max line count is reached.