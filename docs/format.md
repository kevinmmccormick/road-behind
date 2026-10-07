# Observed OMT format

These notes describe the parser, not an official specification. Integers are
little-endian. There is no validated magic signature or version field.
The header occupies 0x2C bytes (eleven unsigned 32-bit integers):

| Byte offset | Field |
| --- | --- |
| 0x00 | Page count |
| 0x04 | Page table byte size |
| 0x08 | Page table offset |
| 0x0C | Resource count |
| 0x10 | Resource table byte size |
| 0x14 | Resource table offset |
| 0x18 | DLL-name count |
| 0x1C | DLL-name list offset |
| 0x20 | Trailer byte size |
| 0x24 | Trailer offset |
| 0x28 | Unknown value, preserved in manifest |

DLL names are NUL-terminated strings. Names decode as ASCII with Latin-1
fallback. No listed DLL is loaded. Page records contain a NUL-terminated name,
one flag byte, a three-byte unsigned offset multiplied by 256, and a four-byte
payload size. Resource records contain a name, a two-byte kind, an unknown byte,
a three-byte offset multiplied by 256, and a four-byte size. If the high byte
of kind is 0x04, another unknown byte, three-byte offset, and four-byte size follow.
The second unknown byte is currently discarded. Table byte counts must match
exactly; all payload spans must fit in the input file.

Resources may contain a direct Windows DIB or a four-byte payload length followed
by a DIB. Recognized header sizes are 12, 40, 108, and 124 bytes. Conversion adds
a BMP file header; this is not a complete image decoder or validation step.
Otherwise the raw payload is retained. Use --no-bmp to retain every raw payload,
including wrappers and trailing bytes normally omitted from BMP output.

The optional RIFF scan checks signature, declared length, and printable form
bytes. It does not validate the internal RIFF chunks or audio codec. WAVE
forms receive .wav; other forms receive .riff. False positives are possible.

The PDF utility separately decodes 8-bit paletted (BI_RGB/BI_RLE8) and 24-bit
BI_RGB BMPs. It writes image-only PDF 1.4 pages at one PDF point per source pixel.
OCR goes to Markdown, not a searchable text layer in the PDF. Unknown page
records, animation, video, interaction logic, external XVD/COL files, and the
trailer are not reconstructed.
