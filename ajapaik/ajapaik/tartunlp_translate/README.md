# TartuNLP translate
Mitmekeelne mitme-valdkonnaline neuromasintõlge. Käesolev versioon toetab sisend- ja väljundkeelena seitset keelt: eesti, läti, leedu, inglise, vene, saksa ja soome.

Arengu staatust kajastab projekti [GitHubi leht](https://github.com/tartunlp/kama).

## Kasutamine

Käesolev masintõlkepakett sisaldab skripte ja treenitud mudeleid. Seda saab kasutada otse Linuxi skriptina või lihtsa serverina, mis laeb mudelid mällu ning vastab tõlkimispäringutele.

Töötav veebiversioon asub aadressil https://translate.ut.ee, mis töötab nii veebidemona kui ka võimaldab lõimimist SDL Studio, MemoQ ja MemSource tõlkeraamistikega.

Kõige paremini töötavad masintõlkes valdkonna-spetsiifilised erilahendused. Kui teid huvitab selline võimalus, võtke ühendust [TartuNLP](https://tartunlp.ai) uurimisrühmaga!

## Tarkvara vajadused

```
pip3 install mxnet sentencepiece sockeye==1.18.106
```

## Kasutamine käsurea skriptina:

```
cat input_text | ./nmt.py  translation_model  truecaser_model  segmenter_model [output_lang [output_domain]]

translation_model: treenitud Sockeye tõlkemudeli kaust (siin: models/translation)
truecaser_model: treenitud tähtede registri normaliseerija mudel (siin: models/preprocessing/truecasing.model)
segmenter_model: treenitud Google SentencePiece segmenteerimismudel (siin: models/preprocessing/sentencepiece.model)

output_lang: väljundi keel (et, lv, lt, en, ru, de, fi)
output_domain: väljundi stiil / valdkond (nc, jr, ep, em, os)
```

Tekstivaldkonnad ning korpused, millel nad põhinevad:
* nc: uudised (News crawl corpus)
* jr: juriidiline tekst (JRC-Acquis)
* ep: ametlik kõne (Europarl)
* em: meditsiin (EMEA)
* os: subtiitrid (OPUS OpenSubs)

## Kasutamine serverina:

```
./nmt.py translation_model  truecaser_model  segmenter_model
```

Server võtab vastu otseühendusega päringuid socket'i kaudu; suhtlemisprotokoll on sama nagu [Sauroni](https://github.com/TartuNLP/sauron) kasutatav protokoll.
