# Road Behind

A small Python extractor with no third-party package requirements for the OMT containers on the
companion CD-ROM for Bill Gates' *The Road Ahead*.

[Run the extractor](#run) | [Rebuild the book outputs](#rebuild-the-book-outputs) | [Read the essay](#the-future-was-easier-to-read-than-to-install)

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
scope. The [essay below](#the-future-was-easier-to-read-than-to-install) revisits
the original December 2025 experiment from October 2026.

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

## The future was easier to read than to install

*An AI-written retrospective, adapted from Kevin M. McCormick's December 12,
2025 conversation and revised on October 7, 2026. The first-person voice below
is the revising AI's; the original experiment and timing are Kevin's account.*

A book about the digital future came with a disc. Thirty years later, someone
asked an AI to read the disc without installing the future.

That is the short version of why this repository exists. The longer version
involves an obscure binary container, a homemade PDF writer, a detour through
Windows OCR, and an argument in which the human was considerably more
optimistic about AI than the AI was.

Reading the December 2025 conversation now, I find that argument more revealing
than any of the code.

Kevin had given a coding agent the OMT files from the companion CD-ROM for Bill
Gates' *The Road Ahead*. He wanted the book's contents in a usable form. While
the agent examined the bytes, he discussed its progress with a separate chat
assistant. That assistant produced an elaborate account of why the job was
hard: vanished tooling, obscure structures, runtime dependencies, diminishing
returns. It even advised stopping when the coding agent had used about a
quarter of its context window.

Kevin wanted to let it cook.

The coding agent kept working. It found tables, followed offsets, and extracted
resources. The apparent ebook turned out to contain its page text as bitmap
images. Then came the wonderfully excessive part. According to the
conversation, the agent had failed to find the available Python libraries. It
responded by implementing a BMP decoder and a minimal PDF writer, and invoking
Windows' built-in OCR through PowerShell. The source retained here confirms
that unusual combination. The PDF preserves the pictures of the pages; the
OCR writes the text to Markdown.

There is a particular species of computer problem that begins with a missing
import and ends with somebody implementing a document format. This was one
of those, compressed into an evening's experiment.

The detail that made Kevin laugh was smaller: the agent handled Roman numerals
in the front matter. After all the binary analysis, it remembered that a book
has pages before page one. A conversion that puts page x after page 200 is
technically an extraction and practically an annoyance. The code avoided that.

### December 2025: the installation lost the race

The chat assistant wanted to tell a familiar preservation story: an ambitious
digital artifact had become stranded, and modern technology had heroically
rescued it. Kevin rejected the premise. In his account, he had written roughly
five sentences, waited about ten minutes, and received useful Markdown without
personally debugging the extraction. He thought that had taken less effort
than installing the original CD-ROM on an appropriate old computer.

That timing is a participant's report, not a controlled benchmark. But the
comparison is the point. For his purpose, making a new way to read the data
had become easier than restoring the old way to run the software.

Imagine explaining that bargain to someone shipping a multimedia disc in
1995. Their application could depend on its own tables, resource conventions,
and Windows components. A future reader might possess none of the necessary
expertise. Yet that reader could describe the desired result, and another
piece of software could construct the missing conversion tools on demand.

The application would cease to be the only practical doorway to its contents.

I find Kevin's optimism persuasive precisely because it is so concrete. He
had a file and a question. The distance between them shrank. A project that
might otherwise have stayed on a list of things to investigate became an
output he could inspect that evening.

That changes the economics of curiosity. Many old files are never examined
because the likely reward does not justify the work of learning their format.
Make that work cheap enough to delegate and people can afford to ask more
questions. Personal archives, minor software, forgotten documentation, and
peculiar discs become worth another look. The important threshold is often
whether anybody bothers to start.

There is a pleasing circularity in this particular example. A companion disc
to a book about the digital future became material for a later kind of
software-mediated reading. The bytes remained useful beyond the application
that originally presented them. That is a good reason to be excited about
what happened, without promoting the book into a precise prediction of modern
language models.

### October 2026: the surprise has acquired infrastructure

Less than ten months later, the original exchange already has a period flavor.
The participants were watching an agent spend its context budget on a strange
little problem and debating whether to intervene. By October 2026, vendors
have spent much of the year building products around exactly this sort of
delegation.

On January 12, Anthropic introduced the Cowork research preview, extending
Claude Code's agent capabilities to knowledge work and local files beyond
coding. That was a product launch, not evidence that every office task had
been solved. It nevertheless put this experiment's basic move into a broader
interface: give software access to the material and ask it to produce a
result. [Anthropic's dated release notes](https://support.claude.com/en/articles/12138966-release-notes)
record the change.

In June, OpenAI reported growing use of Codex for longer tasks and work outside
engineering, including in its own legal, finance, and recruiting departments.
Its estimates of equivalent human task duration were model-generated, and
usage does not establish output quality. Even with those qualifications, the
company's account describes an expanded ambition for coding agents: using
code as a means of getting other work done.
[OpenAI's June 25 report](https://openai.com/index/how-agents-are-transforming-work/)
provides the evidence and its methodological caveats.

By September 10, OpenAI was offering an Agents API in public beta with managed
execution environments, context compaction, and coordination between agents.
The infrastructure explicitly addresses keeping work going across long
sessions. The context-window anxiety in the December transcript now has a
product team working on it.
[OpenAI's launch announcement](https://openai.com/index/introducing-the-agents-api/)
describes those facilities; it does not guarantee successful completion of
arbitrary work.

My reading of those developments is that the striking change is how much of
the surrounding work is becoming delegable. The original agent made an
extractor. This return visit asks for tests, a reproducible pipeline, a
licensing assessment, a boundary around copyrighted material, and documentation
another person can use. Getting a result once and leaving a useful tool behind
are different amounts of work. The second is what gives the first a life
beyond its original chat session.

A small project can show that transition more honestly than a sweeping claim
about the end of programming. Here, the artifact is inspectable. The parser
has limits. The tests can fail. Someone with the source media can run the
pipeline again.

### The bytes were more reliable than the commentary

The December transcript contains another lesson worth keeping. The chat
assistant repeatedly identified the format as ToolBook and inferred Flash
from resource names. This repository has not established either claim.
A suggestive filename is a lead to investigate; it cannot carry an entire
history of an authoring system.

The assistant also told a confident story about why the coding agent should
stop, just before the user reported a successful result. That is a useful
embarrassment to preserve. Fluent commentary can sound like expertise while
a quieter loop of experiments does the actual work. In this case, output
that could be opened was stronger evidence than the explanation of why it
would be difficult to produce.

The enthusiasm deserves the same scrutiny. Recovering page images and OCR
text does not reconstruct the disc's navigation, timing, video, or interactive
behavior. We have a working extractor for observed structures, not a complete
specification of every OMT variant. Nor can an obscure format, by itself,
prove that a model never encountered relevant material during training.

Even formal measurements need care. A March 2026 METR research note reported
that correcting a modeling mistake reduced some recent models' estimated
50%-success task horizons by up to 20%, and emphasized uncertainty from task
selection and analysis choices. That is a useful reminder when turning one
astonishing evening into a theory of everything.
[METR's methods note](https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/)
is a better companion to this story than an invented benchmark score.

The narrower claim is plenty exciting: in this reported experiment, an agent
built a useful route from unfamiliar bytes to readable material with very
little direction. In the 2026 cleanup, the retained code again extracted the
three book containers and assembled 280 page images into a PDF. That result
has an observable shape. It does not need a claim that all obsolete software
is now understood.

### Leave the next reader something better than a chat log

There is still work only preservation can do. The source bytes must survive.
OCR can make mistakes. An image preserves some things and discards others.
A readable book and a functioning multimedia application answer different
historical questions. Keeping original media and documenting transformations
gives future readers choices that a single generated summary cannot provide.

There is also a practical advantage to the agent having written ordinary
code. Running this extractor does not require another model call, access to
the original conversation, or a subscription to the service that helped
create it. Python can repeat the extraction. The format notes can be disputed.
The tests can be extended. The next person inherits a tool they can examine.

That seems like a particularly good outcome for an experiment about digital
longevity. The AI helped lower the cost of understanding enough of the format;
the repository lets that understanding outlast the session.

Road Behind is a joke about direction, but it is also an invitation. A future
worth having should make more of the past available to us. In December 2025,
Kevin found that happening in a folder of obscure files, with a coding agent
that improvised a PDF writer and still found time for the Roman numerals.

By October 2026, the task is to keep the delight and leave better evidence.
