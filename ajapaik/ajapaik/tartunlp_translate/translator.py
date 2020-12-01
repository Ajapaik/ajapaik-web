"""Sockeye model loading and inference"""

import sys
import sockeye
import mxnet as mx
import sentencepiece as spm
import json

from .truecaser import applytc
from .log import log

from collections import namedtuple
from sockeye.translate import inference


def _preprocess(sentence, index, lang_factor, style_factor, models, constraints):
    truecased_sentence = applytc.processLine(models.truecaser, sentence)
    pieces = models.segmenter.EncodeAsPieces(truecased_sentence)
    segmented_sentence = " ".join(pieces)

    rawlen = len(pieces)
    prejsson = {
        "text": segmented_sentence,
        "factors": [
            " ".join([lang_factor] * rawlen),
            " ".join([style_factor] * rawlen),
            " ".join(["f0"] * rawlen),
            " ".join(["g0"] * rawlen),
        ],
    }

    try:
        if constraints and constraints[index]:
            prejsson["avoid"] = constraints[index]
    except IndexError as e:
        sys.stderr.write(str(constraints) + ", " + str(index))
        raise e

    jsson = json.dumps(prejsson)
    log(
        "PREPROC received '"
        + sentence
        + "', turned it into '"
        + segmented_sentence
        + "'"
    )
    return jsson


def _doMany(many, func, args):
    return [func(one, idx, *args) for idx, one in enumerate(many)]


def _postprocess(sentence, idx, models):
    de_segmented_sentence = models.segmenter.DecodePieces(sentence.split())
    try:
        de_truecased_sentence = (
            de_segmented_sentence[0].upper() + de_segmented_sentence[1:]
        )
    except:
        de_truecased_sentence = de_segmented_sentence

    log(
        "POSTPROC received '"
        + sentence
        + "', turned it into '"
        + de_truecased_sentence
        + "'"
    )

    return de_truecased_sentence


def _forward(sentences, models):
    trans_inputs = [
        inference.make_input_from_json_string(
            sentence_id=i, json_string=sentence, translator=models.translator
        )
        for i, sentence in enumerate(sentences)
    ]
    outputs = models.translator.translate(trans_inputs)
    return [(output.translation, output.score) for output in outputs]


def _loadTranslator(model_folders, ctx=mx.cpu()):
    models, source_vocabs, target_vocab = inference.load_models(
        context=ctx,
        max_input_len=None,
        beam_size=3,
        batch_size=16,
        model_folders=model_folders,
        checkpoints=None,
        softmax_temperature=None,
        max_output_length_num_stds=2,
        decoder_return_logit_inputs=False,
        cache_output_layer_w_b=False,
    )

    return inference.Translator(
        context=ctx,
        ensemble_mode="linear",
        bucket_source_width=10,
        length_penalty=inference.LengthPenalty(1.0, 0.0),
        beam_prune=0,
        beam_search_stop="all",
        models=models,
        source_vocabs=source_vocabs,
        target_vocab=target_vocab,
        restrict_lexicon=None,
        store_beam=False,
        strip_unknown_words=False,
    )


def loadModels(translationModelPath, truecaserModelPath, segmenterModelPath):
    """Load translation, truecasing and segmentation models and
	return them as a named tuple"""

    translationModel = _loadTranslator([translationModelPath,])

    truecaserModel = applytc.loadModel(truecaserModelPath)

    segmenterModel = spm.SentencePieceProcessor()
    segmenterModel.Load(segmenterModelPath)

    Models = namedtuple("Models", ["translator", "truecaser", "segmenter"])

    return Models(translationModel, truecaserModel, segmenterModel)


def translate(models, sentences, outputLanguage, outputStyle, constraints):
    """Take list of sentences, output language and style as well as a list of constraints,
	and feed them through a set of loaded NMT models.
	
	Return list of translations, list of scores, list of preprocessed input sentences and list of raw translations prior to postprocessing."""
    cleaninputs = _doMany(
        sentences, _preprocess, (outputLanguage, outputStyle, models, constraints)
    )

    scoredTranslations = _forward(cleaninputs, models)
    translations, scores = zip(*scoredTranslations)

    postprocessed_translations = _doMany(translations, _postprocess, (models,))

    return postprocessed_translations, scores, cleaninputs, translations
