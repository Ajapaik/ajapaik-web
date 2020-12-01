# truecaser
Simple truecaser that processes sentence-first and all-uppercase words using a unigram probabilistic approach

## Train a model:
```learntc.py textfile modelfile```

or

```cat textfile | learntc.py > modelfile```

## Do true-casing

``` applytc.py modelfile textfile > output```

or

``` cat textfile | applytc.py modelfile > output```
