import numpy as np

def load_data_and_labels_as_list(filename):
    """Loads data and label from a file.
    Args:
        filename (str): path to the file.
        The file format is tab-separated values.
        A blank line is required at the end of a sentence.
        For example:
        ```
        EU	B-ORG
        rejects	O
        German	B-MISC
        call	O
        to	O
        boycott	O
        British	B-MISC
        lamb	O
        .	O
        Peter	B-PER
        Blackburn	I-PER
        ...
        ```
    Returns:
        tuple(numpy array, numpy array): data and labels.
    Example:
        >>> filename = 'conll2003/en/ner/train.txt'
        >>> data, labels = load_data_and_labels(filename)
    """
    wordlist, labellist, label2list = [] ,[],[]
    with open(filename, encoding='utf-8') as f:
        words, tags = [], []
        for line in f:
            line = line.rstrip()
            if not line.startswith('#') and not len(line) == 0 and not line.startswith('-DOCSTART-'):
                zahl, word, tag, tag2= line.split('\t')
                wordlist.append(word)
                labellist.append(tag)
                label2list.append(tag2)
    print("Data loaded")
    return np.asarray(wordlist), np.asarray(labellist), np.asarray(label2list)

def load_data_and_labels_as_sents(filename):
    """Loads data and label from a file.
    Args:
        filename (str): path to the file.
        The file format is tab-separated values.
        A blank line is required at the end of a sentence.
        For example:
        ```
        EU	B-ORG
        rejects	O
        German	B-MISC
        call	O
        to	O
        boycott	O
        British	B-MISC
        lamb	O
        .	O
        Peter	B-PER
        Blackburn	I-PER
        ...
        ```
    Returns:
        tuple(numpy array, numpy array): data and labels.
    Example:
        >>> filename = 'conll2003/en/ner/train.txt'
        >>> data, labels = load_data_and_labels(filename)
    """
    sents, labels , labels2= [], [] ,[]
    with open(filename, encoding='utf-8') as f:
        words, tags ,tags2= [], [], []
        for line in f:
            line = line.rstrip()
            if len(line) == 0 or line.startswith('-DOCSTART-'):
                if len(words) != 0:
                    sents.append(words)
                    labels.append(tags)
                    labels2.append(tags2)
                    words, tags , tags2= [], []
            else:
               if not line.startswith('#'):
                    zahl, word, tag, tag2= line.split('\t')
                    words.append(word)
                    tags.append(tag)
                    tags2.append(tag2)
    print("Data loaded")
    return np.asarray(sents), np.asarray(labels) , np.asarray(labels2)

def load_data_and_labels_as_both(filename):
    """Loads data and label from a file.
    Args:
        filename (str): path to the file.
        The file format is tab-separated values.
        A blank line is required at the end of a sentence.
        For example:
        ```
        EU	B-ORG
        rejects	O
        German	B-MISC
        call	O
        to	O
        boycott	O
        British	B-MISC
        lamb	O
        .	O
        Peter	B-PER
        Blackburn	I-PER
        ...
        ```
    Returns:
        tuple(numpy array, numpy array): data and labels.
    Example:
        >>> filename = 'conll2003/en/ner/train.txt'
        >>> data, labels = load_data_and_labels(filename)
    """
    sents, labels, labels2 = [], [], []
    wordlist, labellist, label2list= [], [], []
    with open(filename, encoding='utf-8') as f:
        words, tags, tags2 = [], [], []
        for line in f:
            line = line.rstrip()
            if len(line) == 0 or line.startswith('-DOCSTART-'):
                if len(words) != 0:
                    sents.append(words)
                    labels.append(tags)
                    labels2.append(tags2)
                    words, tags, tags2 = [], [], []
            else:
               if not line.startswith('#'):
                    zahl, word, tag, tag2= line.split('\t')
                    words.append(word)
                    wordlist.append(word)
                    tags.append(tag)
                    labellist.append(tag)
                    tags2.append(tag2)
                    label2list.append(tag2)
    print("Data loaded")
    return np.asarray(sents), np.asarray(labels), np.asarray(wordlist) , np.asarray(labellist) , np.asarray(labels2) , np.asarray(label2list)