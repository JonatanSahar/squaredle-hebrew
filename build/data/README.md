## Data provisioning

### Vendored Hebrew word data

The repository vendors Hebrew word data from `eyaler/hebrew_wordlists`:

- `https://raw.githubusercontent.com/eyaler/hebrew_wordlists/main/hspell_simple.txt`
  Saved as `build/data/hspell/words.txt`
- `https://raw.githubusercontent.com/eyaler/hebrew_wordlists/main/cc100_intersect_no_fatverb.csv`
  Saved as `build/data/cc100_intersect_no_fatverb.csv`
- `https://raw.githubusercontent.com/eyaler/hebrew_wordlists/main/COPYING`
  Saved as `LICENSES/HSPELL.txt`
- `https://raw.githubusercontent.com/eyaler/hebrew_wordlists/main/LICENSE`
  Saved as `LICENSES/HSPELL-ATTRIBUTION.txt`

`hspell_simple.txt` is derived from Hspell. Hspell is copyright
Nadav Har'El and Dan Kenigsberg, 2000-2017, and is distributed under the
GNU Affero General Public License v3. The exact upstream AGPL text used for the
vendored data is kept in `LICENSES/HSPELL.txt`, and the upstream attribution
note from `eyaler/hebrew_wordlists` is kept in
`LICENSES/HSPELL-ATTRIBUTION.txt`.

Caveats called out by the upstream repository:

- The underlying Hspell dictionary has not been updated with new words since
  2017.
- The dictionary was not updated for the 2017 Hebrew spelling reform, so some
  modern full-spelling variants may be missing while older spellings may still
  appear.

### Frequency list used by the generator

The current `build/squaredle/dictionary.py` loader expects a whitespace-delimited
frequency file and reads the first token from each line as the candidate word.
Because `cc100_intersect_no_fatverb.csv` is comma-separated (`word,count`), it
is vendored for reference but not used directly by the generator.

For puzzle generation, use the OpenSubtitles Hebrew frequency list:

- `https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/he/he_full.txt`
  Saved as `build/data/opensubtitles-he-freq.txt`

### Blacklist

Keep manual exclusions in:

- `build/data/blacklist.txt`
