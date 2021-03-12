# OEKG Integrator

The file `main.py` runs an example script to add and then remove few triples into the OEKG.

For running it, you first need to specify the API URL.

## API methods

Existing API methods for getting OEKG IDs:
1. api/wikidataIds/IDS (e.g., "api/wikipediaIDs/en/Q6279;Q3526570")
2. api/wikidataId/ID (e.g., "api/wikipediaIDs/en/Q6279")
3. api/wikipediaIds/LANGUAGE/IDS (e.g., "api/wikipediaIDs/en/Barack_Obama;Berlin")
4. api/wikipediaId/LANGUAGE/ID (e.g., "api/wikipediaIDs/en/Barack_Obama")
where IDS: Set of IDs separated by ";", ID: single ID, LANGUAGE: language code ("en", "de", ...)

### Components

- EventKG light
- EventKG+Click
- [TIME](https://github.com/cleopatra-itn/TIME_OEKG-Hackathon)
- [InfoSpread](https://github.com/cleopatra-itn/TIME-IPoN-OEKG-Hackathon)
- MLM
- [UNER](https://github.com/cleopatra-itn/UNER-OEKG-Hackathon)
- VQuAnDa
