# TartuNLP translate
Multilingual multi-domain neural machine translation. The current version supports seven languages as input and output language: Estonian, Latvian, Lithuanian, English, Russian, German and Finnish.

Development status is shown on the [GitHub page](https://github.com/tartunlp/kama).

## Usage:

This machine translation package includes scripts and trained models. You can use it directly as a Linux script or as a simple server that loads the models and responds to translation requests.

A working version of the same models is run online at https://translate.ut.ee, which works both as a web demo as well as supports integration with SDL Studio, MemoQ and MemSource.

Neural machine translation works best when it is fine-tuned and customized. If you are interested in such a possibility, contact the [TartuNLP](https://tartunlp.ai) research group!

# Requirements:

```
pip3 install mxnet sentencepiece sockeye
```

# Usage in command-line:

```
cat input_text | ./nmt.py  translation_model  truecaser_model  segmenter_model [output_lang [output_domain]]

translation_model: path to a trained Sockeye model folder (here: models/translation)
truecaser_model: path to a trained TartuNLP truecaser model file (here: models/preprocessing/truecasing.model)
segmenter_model: path to a trained Google SentencePiece model file (here models/preprocessing/sentencepiece.model)

output_lang: output language (one of the following: lt, fi, de, ru, lv, et, en)
output_domain: output domain (one of the following: nc, jr, ep, em, os)
```

Domains, with corpora they are based on:
* nc: news (News crawl corpus)
* jr: legal (JRC-Acquis)
* ep: official speech (Europarl)
* em: medical (EMEA)
* os: subtitles (OPUS OpenSubs)

# Usage as a socket server:

```
./nmt.py translation_model  truecaser_model  segmenter_model
```

The server uses low-level socket communication; the communication protocol is equivalent to what [Sauron](https://github.com/TartuNLP/sauron) uses.
