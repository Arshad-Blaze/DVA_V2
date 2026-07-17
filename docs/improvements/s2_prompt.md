# Sprint 2.5 – Enterprise Detection Layer (Architecture First)

## Context

We are rebuilding the DVA Platform from scratch using the Architecture Bible as the ONLY source of truth.

The Connection Layer is complete and approved.

The next milestone is NOT the Canonical Layer.

Before any further development, the Detection Layer must become a production-grade enterprise data discovery engine capable of handling every retailer POS data scenario we have discussed.

Do NOT bypass the architecture.

Do NOT allow downstream layers to inspect raw files.

The Detection Layer runs exactly once and produces a complete DiscoveryResult consumed by every downstream layer.

Architecture order:

Connection
→ Detection
→ Canonical
→ Requirement
→ Processing
→ Validation
→ Output
→ Flush

Every downstream layer must consume ONLY the contract produced by the previous layer.

---

## Mission

Completely redesign and implement the Detection Layer so that it can correctly discover and describe virtually any retailer POS dataset before processing begins.

Detection is responsible ONLY for discovery.

No business logic.
No aggregation.
No validation.
No UI logic.

---

## Objectives

Implement the following capabilities.

### 1. File Type Detection

Support:

- Delimited
- Fixed Width
- Excel
- Multiline Delimited
- Multiline Fixed Width
- Mixed Record Files

Detection must return confidence.

Never assume.

---

### 2. Delimiter Detection

Automatically detect:

- comma
- pipe
- tab
- semicolon
- custom delimiter

Return delimiter confidence.

---

### 3. Encoding Detection

Detect:

- UTF-8
- UTF-16
- ANSI
- Latin-1

Return confidence.

---

### 4. Header Detection

Identify:

- header rows
- data start
- trailer start
- metadata rows

Return confidence.

---

### 5. Fixed Width Detection

Support:

- single record
- multiline
- header/detail
- trailer
- mixed layouts

Do not treat fixed width as fallback.

It must be a first-class format.

---

### 6. Record Type Detection

Automatically discover record types.

Examples include:

HDR

H

D

S

U

TRL

T

but NEVER hardcode these.

Discover dynamically using prefixes and statistics.

For every detected record type determine:

- prefix
- frequency
- average record length
- sample
- confidence

---

### 7. Record Hierarchy

Build relationships.

Example:

Header

↓

Store

↓

Item

↓

Promotion

↓

Trailer

Hierarchy must be generic.

No retailer-specific assumptions.

---

### 8. Layout Intelligence

For fixed-width files:

If layout already exists

→ use it

Otherwise

Generate suggested layout containing:

- column start
- width
- datatype
- probable column name
- confidence

If confidence is low

recommend manual layout builder.

---

### 9. Multiline Detection

Support:

Delimited multiline

Fixed-width multiline

Nested records

Store + Item

Header + Detail

Header + Trailer

Store:

start line

record type

flatten strategy

relationships

---

### 10. Preview Generation

Detection must produce:

Raw Preview

↓

Flatten Preview

↓

Canonical Preview

The UI must only render previews.

No preview generation inside UI.

---

### 11. Candidate Column Detection

Predict mappings for:

Store

UPC

Description

Brand

Department

Category

Units

Weighted Quantity

Price

Sales

Currency

Date

Time

Promotion

Store Type

Region

Division

Unit of Measure

Record Type

Return confidence for each.

Allow multiple candidates.

---

### 12. Quantity Intelligence

Implement quantity recommendations.

Detect:

Units column

Weighted quantity column

Unit of Measure

Quantity type

Mixed quantity datasets

Business recommendation:

Use Weighted Quantity whenever present.

Fallback to Units only when:

Weighted Quantity column missing

OR

Weighted Quantity is zero/null

AND Units contains value.

Store recommendation inside DiscoveryResult.

Do NOT perform aggregation here.

Only recommend.

---

### 13. Excel Discovery

Support workbook discovery.

Return:

sheet names

candidate sheet

header

preview

schema

confidence

---

### 14. Statistics

Collect:

estimated rows

record count

record length

average width

character distribution

delimiter statistics

record statistics

header confidence

schema confidence

encoding confidence

---

### 15. Discovery Report

Generate DiscoveryReport.

Include:

file type

delimiter

encoding

header

trailer

record hierarchy

layout recommendation

candidate columns

warnings

recommendations

confidence

sample preview

---

### 16. Discovery Context

Internally create DiscoveryContext.

Contains:

raw sample

character analysis

frequency maps

prefix maps

line analysis

layout statistics

record statistics

DiscoveryContext is INTERNAL ONLY.

Return only DiscoveryResult.

---

### 17. False Positive Reduction

If uncertain:

Return

Primary Candidate

Alternative Candidate

Confidence

Warnings

Never silently assume.

---

### 18. Detection Tests

Add comprehensive tests covering:

Delimited

Pipe

Tab

Semicolon

Excel

Fixed Width

Multiline

Header/Trailer

Nested records

Unknown record types

Mixed quantity

Malformed files

Large files

Regression suite

---

## Documentation

Update:

Architecture_Bible.md

docs/developer/detection.md

Detection Flow Diagram

DiscoveryResult Contract

Decision Tree

Supported Format Matrix

Known Limitations

---

## Deliverables

Produce:

Sprint2_5_Enterprise_Detection_Report.md

Detection_Test_Report.md

Updated Architecture_Bible.md

Detection Flow Diagram

Discovery Decision Tree

Test Coverage Report

Benchmark Results

---

## Acceptance Criteria

Sprint is complete only if:

✓ Detection runs exactly once.

✓ Downstream layers never inspect raw files.

✓ DiscoveryResult completely describes the dataset.

✓ Fixed-width detection is production ready.

✓ Multiline detection supports nested retailer data.

✓ Candidate mapping is comprehensive.

✓ Quantity intelligence recommendations are implemented.

✓ Confidence scoring exists for every decision.

✓ Discovery reports are generated.

✓ Existing tests pass.

✓ New detection tests pass.

✓ Architecture Bible remains valid.

Do NOT proceed to the Canonical Layer until every acceptance criterion above is satisfied.
