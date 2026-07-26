# FLORES-200

Meta's FLORES-200 benchmark dataset for evaluating NLLB translations.

## Download
https://github.com/facebookresearch/flores

## Expected Format

### CSV Format
```csv
source_lang,target_lang,source_text,target_text
en,fr,Hello,Bonjour
en,ta,Good morning,காலை வணக்கம்
```

### JSON Format
```json
[
  {"source_lang": "en", "target_lang": "fr", "source_text": "Hello", "target_text": "Bonjour"},
  {"source_lang": "en", "target_lang": "ta", "source_text": "Good morning", "target_text": "காலை வணக்கம்"}
]
```

### TSV Format (tab-separated)
```
en\tfr\tHello\tBonjour
en\tta\tGood morning\tகாலை வணக்கம்
```

Place your files in this folder and restart the application.
