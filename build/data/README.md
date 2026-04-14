## Data provisioning

### Hspell

Download the Hspell source archive from:

- `http://hspell.sourceforge.net/hspell-1.4.tar.gz`

The upstream archive contains the AGPL license text in `COPYING` and the
lexicon sources in files such as `milot.hif`. The repository already carries
the project notice and a placeholder license file; when the real Hspell data is
vendored, replace `LICENSES/HSPELL.txt` with the exact upstream `COPYING` text.

For the build pipeline, extract the Hspell lexicon artifacts into:

- `build/data/hspell/`

The current implementation does not yet parse the real Hspell format; Phase 2
only establishes the source location and repo layout.

### OpenSubtitles Hebrew frequency list

Download:

- `https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/he/he_full.txt`

Save it as:

- `build/data/opensubtitles-he-freq.txt`

### Blacklist

Keep manual exclusions in:

- `build/data/blacklist.txt`
