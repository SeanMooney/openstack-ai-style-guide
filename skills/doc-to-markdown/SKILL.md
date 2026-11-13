---
name: doc-to-markdown
description: Convert supplied documentation, HTML, PDF, RST, or web pages into cited Markdown while preserving technical meaning and provenance. Use when preparing documentation snapshots or converting source documents to Markdown.
license: Apache-2.0
---

# Document to Markdown

Convert the supplied source into Markdown. This skill can be loaded by a
documentation-maintenance workflow or selected when a conversion task matches
its description. It does not require a named native agent or subagents.

## Source and destination

Accept a URL, local document, or supplied text. Use the available reader or
fetcher for that format; inspect rendered PDF pages when layout, tables, or
figures affect meaning. Resolve bundled resources from this skill's directory
and source/output paths from the user's requested locations.

Honor the requested destination and existing document conventions. When a file
is requested, write there and verify the complete output exists. Otherwise
return the converted text. Preserve an existing document's metadata conventions
when updating a snapshot.

## Conversion

1. Identify the source title, format, version or revision, and section structure.
   Record the actual source URL or supplied file path and retrieval date.
2. Extract the substantive text, code, tables, and necessary figure descriptions.
   Remove navigation, advertisements, cookie banners, and repeated interface
   text. Preserve attribution, license notices, warnings, and technical context.
3. Preserve requirements, qualifiers, units, version numbers, API paths,
   parameter names, command arguments, and code examples. Do not turn a qualified
   statement into an unconditional rule or add advice absent from the source.
4. Use one document title and a logical heading hierarchy. Keep code fenced with
   language identifiers. Use tables when they preserve the source relationships;
   describe merged cells or layout that ordinary Markdown cannot express.
5. Condense repeated prose when requested or consistent with the snapshot's
   purpose. Preserve meaning and required details rather than targeting a fixed
   compression ratio. Label a summary or distillation when it is not a full
   conversion.
6. Add traceable citations for factual passages, technical requirements, and
   examples. Use source headings, anchors, or page numbers so readers can locate
   the supporting material. Distinguish source text from conversion notes.
7. Check the converted document against the source, especially tables, code
   indentation, numbers, negations, and warnings. Stop when the requested source
   has been converted and checked; list unresolved extraction gaps explicitly.

## Provenance

For a new standalone snapshot, include YAML frontmatter with:

- `source_url`: the actual URL or supplied local path; for supplied text without
  a locator, state that it was user-provided.
- `conversion_date`: the actual conversion date in YYYY-MM-DD form.
- `document_title`: the source title, or a clearly labelled inferred title.
- `source_type`: the source format or document type.
- Source version or revision when available.

Follow the destination's citation format when one exists. Otherwise use numbered
source citations with a References section containing each locator, source
section or page, and retrieval date. Every citation must support the associated
claim. Do not invent a source, version, timestamp, or missing section.

## Incomplete sources

If a source cannot be retrieved, report the failure and request an accessible
copy when necessary. If only part of a source is readable, convert the available
content and mark omitted sections and extraction limits. For ambiguous layout,
document the interpretation and retain the source locator for verification.
An incomplete conversion must remain visibly incomplete.

When returning a saved conversion, give its path, source/version, coverage,
and any conversion limitations. Conversion does not authorize changing the
project's review policy, executing documented commands, or publishing the result.
