#!/usr/bin/python3

import sys
import html
import json

from time import time
from nltk import sent_tokenize

from ajapaik.ajapaik.tartunlp_translate import sock, translator
from .constraints import getPolitenessConstraints as getCnstrs
from .log import log

# IP and port for the server
MY_IP = "localhost"
MY_PORT = 12346

supportedStyles = {"os", "un", "dg", "jr", "ep", "pc", "em", "nc"}
supportedOutLangs = {"et", "lv", "en", "ru", "fi", "lt", "de"}
extraSupportedOutLangs = {
    "est": "et",
    "lav": "lv",
    "eng": "en",
    "rus": "ru",
    "fin": "fi",
    "lit": "lt",
    "ger": "de",
}
defaultStyle = "nc"
defaultOutLang = "en"

USAGE_MSG = """\nUsage: nmtnazgul.py  translation_model  truecaser_model  segmenter_model [output_lang [output_style]]
	
	translation_model: path to a trained Sockeye model folder
	truecaser_model: path to a trained TartuNLP truecaser model file
	segmenter_model: path to a trained Google SentencePiece model file
	
Without the output language and any further parameters an NMT server is started; otherwise the script translates STDIN
	
	output_lang: output language (one of the following: {0})
	output_style: output style (one of the following: {1}; default: {2})
	
Further info: http://github.com/tartunlp/nazgul\n\n""".format(
    ", ".join(list(supportedOutLangs)), ", ".join(list(supportedStyles)), defaultStyle
)


#############################################################################################
###################################### STDIN and Server #####################################
#############################################################################################


def getConf(rawConf):
    style = defaultStyle
    outlang = defaultOutLang

    for field in rawConf.split(","):
        if field in supportedStyles:
            style = field
        if field in supportedOutLangs:
            outlang = field
        if field in extraSupportedOutLangs:
            outlang = extraSupportedOutLangs[field]

    return style, outlang


def parseInput(rawText):
    global supportedStyles, defaultStyle, supportedOutLangs, defaultOutLang

    try:
        fullText = rawText["src"]
        rawStyle, rawOutLang = getConf(rawText["conf"])

        livesubs = "|" in fullText

        sentences = fullText.split("|") if livesubs else sent_tokenize(fullText)
        delim = "|" if livesubs else " "

    except KeyError:
        sentences = rawText["sentences"]
        rawStyle = rawText["outStyle"]
        rawOutLang = rawText["outLang"]
        delim = False

    if rawStyle not in supportedStyles:
        # raise ValueError("style bad: " + rawStyle)
        rawStyle = defaultStyle

    if rawOutLang not in supportedOutLangs:
        # raise ValueError("out lang bad: " + rawOutLang)
        rawOutLang = defaultOutLang

    outputLang = rawOutLang
    outputStyle = rawStyle

    return sentences, outputLang, outputStyle, delim


def decodeRequest(rawMessage):
    struct = json.loads(rawMessage.decode("utf-8"))

    segments, outputLang, outputStyle, delim = parseInput(struct)

    return segments, outputLang, outputStyle, delim


def encodeResponse(translationList, delim):
    translationText = delim.join(translationList)

    result = json.dumps(
        {"raw_trans": ["-"], "raw_input": ["-"], "final_trans": translationText}
    )

    return bytes(result, "utf-8")


def serverTranslationFunc(rawMessage, models):
    segments, outputLang, outputStyle, delim = decodeRequest(rawMessage)

    translations, _, _, _ = translator.translate(
        models, segments, outputLang, outputStyle, getCnstrs()
    )

    return encodeResponse(translations, delim)


def startTranslationServer(models, ip, port):
    log("started server")

    # start listening as a socket server; apply serverTranslationFunc to incoming messages to genereate the response
    sock.startServer(serverTranslationFunc, (models,), port=port, host=ip)


def translateStdinInBatches(models, outputLang, outputStyle):
    """Read lines from STDIN and treat each as a segment to translate;
	translate them and print out tab-separated scores (decoder log-prob)
	and the translation outputs"""

    # read STDIN as a list of segments
    lines = [line.strip() for line in sys.stdin]

    # translate segments and get translations and scores
    translations, scores, _, _ = translator.translate(
        models, lines, outputLang, outputStyle, getCnstrs()
    )

    # print each score and translation, separated with a tab
    for translation, score in zip(translations, scores):
        print("{0}\t{1}".format(score, translation))


#############################################################################################
################################## Cmdline and main block ###################################
#############################################################################################


def readCmdlineModels():
    """Read translation, truecaser and segmenter model paths from cmdline;
	show usage info if failed"""

    # This is a quick hack for reading cmdline args, should use argparse instead
    try:
        translationModelPath = sys.argv[1]
        truecaserModelPath = sys.argv[2]
        segmenterModelPath = sys.argv[3]
    except IndexError:
        sys.stderr.write(USAGE_MSG)
        sys.exit(-1)

    return translationModelPath, truecaserModelPath, segmenterModelPath


def readLangAndStyle():
    """Read output language and style off cmdline.
	Language is optional -- if not given, a server is started.
	Style is optional -- if not given, default (auto) is used."""

    # EAFP
    try:
        outputLanguage = sys.argv[4]

        try:
            outputStyle = sys.argv[5]
        except IndexError:
            outputStyle = defaultStyle

    except IndexError:
        outputLanguage = None
        outputStyle = None

    return outputLanguage, outputStyle


if __name__ == "__main__":
    # read translation and preprocessing model paths off cmdline
    modelPaths = readCmdlineModels()

    # read output language and style off cmdline -- both are optional and will be "None" if not given
    olang, ostyle = readLangAndStyle()

    # load translation and preprocessing models using paths
    models = translator.loadModels(*modelPaths)

    # if language is given, STDIN is translated; otherwise a server is started
    if olang:
        translateStdinInBatches(models, olang, ostyle)
    else:
        # when argparse is finally used, set MY_IP and MY_PORT to cmdline arguments
        startTranslationServer(models, MY_IP, MY_PORT)
