# Road Behind

An essay about revisiting Bill Gates' *The Road Ahead*, and the small tools
that made its companion CD-ROM readable again.

[Essay](#the-future-was-easier-to-read-than-to-install) | [Extractor](#run) | [Reproduce the outputs](#rebuild-the-book-outputs)

## The future was easier to read than to install

*An AI-written retrospective based on Kevin M. McCormick's December 12, 2025
conversation and a reading of the book's extracted OCR text. Revised October 7,
2026. The experiment and its timing are Kevin's account; the interpretation
below is this essay's. Book references use the printed page labels preserved
in the extraction. The copyrighted book and source conversation remain private.*

In December 2025, Kevin gave a coding agent some files from the companion
CD-ROM for Bill Gates' *The Road Ahead* and asked it to recover their contents.
The disc had once offered a demonstration of the future described in the book;
thirty years later, its OMT containers stood between a reader and the pages he
wanted to read. While the agent investigated, Kevin discussed its progress with
a separate chat assistant, which became increasingly articulate about why the
work was difficult. It speculated about obsolete authoring systems and runtime
dependencies, then recommended stopping when the coding agent had used roughly
a quarter of its context window. Kevin preferred to let it continue. The
agent found resource tables and page images, wrote conversion code, and
produced a readable result while the other assistant was still explaining the
obstacles.

The implementation had an eccentric route to usefulness. The book's page text
was stored as bitmaps, and, according to the conversation, the agent failed to
find the Python libraries available on the machine. It improvised a BMP decoder
and a minimal PDF writer, then called Windows' built-in OCR through PowerShell
to make Markdown. Those choices survive in the code here, including the care
taken to sort Roman-numeral front matter before the numbered pages. Kevin
reported about five sentences of direction and ten minutes of waiting, without
personally debugging the extraction. That is an anecdote rather than a timing
study, but his comparison was illuminating: obtaining the book this way had
felt easier than installing the original disc on an appropriate old computer.
For this particular purpose, commissioning new software had become the shorter
route to using old data.

It would be easy to tell that story as a rebuke to the confidence of 1995, with
an obsolete multimedia product rescued from its own ambitions. Kevin resisted
that reading, and the book itself gives him considerable support. Gates was
interested in what happens when a previously expensive activity becomes cheap
enough to take for granted. In the opening chapter, he moves from the falling
cost of computation to the prospect of nearly free communication, asking what
people will do once familiar constraints loosen (pp. 17–18). The extraction
suggests a further, narrower extension of that argument: some of the work of
interpreting a file and building a tool for it can become cheap enough to
justify an otherwise idle curiosity. A peculiar old disc need not promise a
large audience, a commercial return, or a research career before someone can
afford to investigate it.

### The agents were already in the book

Reading *The Road Ahead* after this experiment is more interesting than grading
its inventory of future gadgets. Gates himself objects to the highway metaphor
because it emphasizes infrastructure and geography at the expense of what
people might do with the system (p. 6). Nor does this text support the convenient
caricature of a Gates who simply failed to notice the Internet. He calls it the
most important computing development since the IBM PC, describes the Web's
publishing possibilities, and repeatedly presents the Internet as the route
toward the broader network he imagines (pp. 91, 123, 228). His more revealing
commitment is to a world in which software learns enough about its user to
reduce the effort of acting on an intention.

In “Applications and Appliances,” that commitment becomes unusually specific.
Gates describes agents with initiative and personality, then imagines “softer
software” that learns habits instead of remaining forever as inexperienced as
an assistant on the first day of work (pp. 83–85). He recognizes the annoyance
of a system confidently performing unwanted services and the need to ask
before discarding valuable work. On the following page he discusses experiments
in which people became socially deferential toward computers, including rating
a machine more kindly when answering it directly than when reporting to
another machine (p. 86). The December conversation offers a small variation on
that problem: one assistant's confident manner made its account of the task
sound more authoritative than the evidence warranted. Kevin's useful act of
judgment was to leave room for the other agent to test what was actually
possible.

These imagined assistants are not confined to routing messages. Elsewhere,
Gates describes a book that answers questions as a tutor, adjusts explanations
to the reader, and remembers what the reader has already encountered (p. 195).
He imagines software turning a hummed tune into an arrangement and inserting a
user's likeness into a film (p. 86). Yet in the final chapter he says that
programs recreating elements of human intelligence are very unlikely to arrive
in his lifetime, pointing to the repeated disappointment of earlier AI
predictions (p. 255). There is a productive tension between the capabilities he
is willing to imagine and the intelligence he is reluctant to credit. Our
extractor cannot settle what counts as human understanding, but it makes that
tension concrete: software can perform a useful sequence of unfamiliar tasks
while remaining an unreliable narrator of what it knows. The achievement and
the uncertainty have to be considered together.

Gates is often most persuasive when he brings his own speculation back to
ordinary use. Describing his automated house, he observes that replacing a
light switch is a demanding proposition because the existing device is so
reliable; a little convenience can be consumed by the irritation of a system
that guesses wrong. He keeps manual switches (p. 223). That is a better
standard for an agent than how impressive its explanation sounds. In the
December exchange, the chat assistant inferred ToolBook and Flash from
suggestive evidence that this project has not established. The coding agent,
meanwhile, produced files that could be opened. During the 2026 cleanup, the
retained code again extracted the three book containers and assembled 280 page
images into a PDF. That observable result supports a useful claim about this
experiment without requiring a grander claim about all obsolete formats or
about machine understanding in general.

### Access, ownership, and whose convenience matters

The book also complicates the idea that successful extraction preserves the
whole thing. In “Content Revolution,” Gates argues that electronic documents
will become combinations of text, sound, images, and interaction; printing one
could be as inadequate as reading a score instead of hearing the music
(pp. 112–114). By that standard, a PDF and an OCR transcript recover only part
of what the companion disc was trying to be. They do not restore its navigation,
timing, or interactive experience. Yet they make the argument of the book much
easier to examine. The user has chosen a different purpose for the material
than the original presentation anticipated, and software has made that choice
practical. The project's success lies partly in that freedom to choose a less
elaborate form.

Gates welcomes readers' ability to reorganize information, but his account of
how they will possess it is more ambivalent. In “Friction-Free Capitalism,” he
imagines buying a lasting right to access a song or book from a network, without
carrying a physical copy. He also considers payment per use, expiration dates,
and limits on lending (pp. 175–178). These are presented as possibilities for
pricing and distribution, but they expose a question this repository cannot
avoid: what must remain available for a purchase to remain useful? Our
experiment depended on having the bytes. An agent can write a reader for an
awkward container; its ingenuity does not supply a missing file or keep an
absent service running. The disc's dated packaging turned out to be a tractable
obstacle because the material was still locally present.

A related tension runs through Gates' account of personal attention. He
imagines agents protecting people from unwanted interruptions, with explicit
control over who may call and when (pp. 213–214). He also describes profiles
that help software prepare enticing surprises and advertisers deliver more
precisely targeted messages (pp. 169–174). He recognizes privacy disputes,
commercial bias, and the possibility of compulsive use; it would be unfair to
say he never saw the problems. His optimism rests on the expectation that
choice, competition, and suitable rules will make these arrangements serve the
user. Close reading makes that expectation more visible. An assistant that
knows what holds someone's attention is equipped both to protect that attention
and to sell access to it, and greater technical competence does not decide
which purpose wins.

That leaves a question for our own enthusiasm about agents. The original
experiment felt empowering because Kevin could set the purpose, let the tool
work, and keep a result outside the conversation. This repository extends that
arrangement: the extraction can be repeated with ordinary Python, without a
model call or a subscription to the service that helped write the code. Its
scope is small and its limitations are inspectable. The local book, however,
remains copyrighted material and is excluded from publication along with the
disc assets and source conversation. Sharing the means of extraction lets
another owner investigate their own copy while keeping the distinction between
a tool and the material it processes explicit.

### Returning in October 2026

Less than ten months separates the original conversation from this revision,
and the surrounding product landscape already gives the experiment a different
character. Anthropic's January 12 Cowork research preview brought Claude Code's
agent capabilities into knowledge work involving local files beyond coding.
By September, OpenAI's Agents API public beta offered managed execution
and facilities such as context compaction for sustained tasks. These launches
show vendors building products around the pattern Kevin had tried: provide
material, describe an outcome, and let software carry out intermediate work.
They establish a change in what is being offered, not a guarantee that delegated
work succeeds. The dated accounts are in [Anthropic's release notes](https://support.claude.com/en/articles/12138966-release-notes)
and [OpenAI's September announcement](https://openai.com/index/introducing-the-agents-api/).

For this project, the most meaningful comparison is between the first useful
output and what it took to return to it. The December conversation captured
the pleasure of watching a troublesome task become manageable. The October
work has involved reading the recovered book, checking the parser's boundaries,
adding synthetic tests, recording dependencies, and making the extraction
repeatable without publishing the copyrighted source. These activities are
less theatrical than improvising a PDF writer, but they determine whether the
initial result can support an argument or survive outside its original session.
They also give the initial skepticism a fairer answer: enough of this format
was understood to do something useful, and the extent of that understanding
can now be examined.

There may be few people who ever need this particular extractor. Gates offers
a reason to care anyway when he describes how repeated dead ends can discourage
curiosity, while accessible information gives people a reason to keep asking
questions (p. 192). This project is one modest instance of lowering that
threshold. It also puts a condition on the optimism: access depends on keeping
the material, distinguishing it from generated interpretation, and retaining
some control over the tools through which it is encountered. Reading the book
now, through a program written to reach it, makes its faith in personal
empowerment feel both recognizable and unfinished. The useful future in this
story is the one in which a reader can decide that an old disc deserves another
look, then spend more time considering what it says than persuading a computer
to open it.

## The tools

The remainder of this README documents the small Python extractor, PDF/OCR
utility, and reproduction script used to recover the companion CD-ROM's
contents. They have no third-party Python package requirements.

## Why this exists

The companion disc is part of the book's picture of the digital future.
Revisiting that picture today means first getting its contents out of a format
built for 1990s software. This project began as a practical way to inspect and
extract the disc's OMT files so their pages, images, and embedded audio could
be studied with modern tools.

This repository contains the extractor, its companion PDF/OCR utility, a local
reproduction script, and notes on the observed container structure.
It does not recreate the interactive CD-ROM application,
decode every resource type, or extract the entire disc's other file formats.
The book and CD-ROM contents are not included.

## Run

Install Python 3.10 or later. No pip packages, compiler, or build step are
required. From this directory, using your own local copy of a container:

```powershell
python omt_extract.py "C:\path\to\BOOK.OMT" --out local-only/output/book
```

The output directory must not already exist. Without `--out`, output goes to
`extracted_<input-stem>` in the current directory. Use a fresh destination for
each run. Options:

- `--no-carve`: skip the whole-file RIFF scan, reducing memory use.
- `--no-bmp`: preserve all resource payloads as raw `.bin` files.
- `--help`: show command-line usage.

The extractor writes:

| Path | Contents |
| --- | --- |
| `manifest.json` | Header fields, DLL names, page and resource records |
| `pages/` | Indexed, named raw page blobs |
| `resources/` | Indexed resource payloads, with recognized DIBs wrapped as BMPs |
| `carved/` | Signature-carved RIFF chunks; WAVE forms use `.wav` |

Resource filenames include the record index and payload number to prevent
collisions. The manifest preserves original names. DLL names are recorded only;
no DLL or other extracted code is loaded or executed.

## Verify and develop

```powershell
python -m py_compile omt_extract.py omt_imgtext_to_pdf_ocr_md.py reproduce.py
python -m unittest discover -s tests -v
python scripts/check_publication.py
```

The publication check requires Git and a staged or committed checkout.
Tests generate their own tiny synthetic containers; no CD-ROM is needed.
See [test coverage and limitations](docs/testing.md),
[format notes](docs/format.md), and [contributing](CONTRIBUTING.md).

## Scope and limitations

The parser reflects observed files, not an official OMT specification. Offsets
come from the header rather than fixed table locations. Image recognition is
heuristic, and RIFF carving can find false positives. Non-bitmap resource
formats remain raw. Extraction reads each payload into memory; default RIFF
carving also reads the entire input. Use trusted local inputs of manageable
size. Failed writes can leave partial output; retry in a fresh directory.

XVD/COL decoding and unrelated OMT components are outside this repository's
scope.

## License and source material

Project code and documentation: [MIT](LICENSE), copyright 2025-2026
Kevin M. McCormick. See [dependency and provenance assessment](THIRD_PARTY_NOTICES.md).
This independent project is not affiliated with or endorsed by Bill Gates,
Microsoft, or the book's publishers.

Supply your own source media and respect the rights attached to it. The project
license does not license the book, disc, or extracted material. Keep those
files under ignored `local-only/`; never attach them to issues, commits, or
releases. This checkout uses an explicit publication allowlist so unreviewed
files are ignored by default. [Publication notes](docs/publication.md) document
the local separation and verification.

## Rebuild the book outputs

Mount your own original CD-ROM image, then run:

```powershell
python reproduce.py 'D:\' --out local-only/reproduced
```

This finds the three book containers, extracts them, builds an image PDF, and
writes OCR Markdown. OCR requires Windows PowerShell 5.1 and Windows' local OCR
engine with a suitable language pack. Use `--no-ocr` for a portable PDF-only run
(with placeholder Markdown), or `--extract-only` for just the extracted assets.
The script accepts a mounted/unpacked directory, not a raw image file.
See [reproduction instructions](docs/reproduction.md) for details and limits.
