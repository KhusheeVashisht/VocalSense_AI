# VocalSense AI — Tableau Analytics & Dashboard Integration Guide

This guide provides technical specifications, schema definitions, calculated-field formulas, and step-by-step instructions for visualizing VocalSense AI data using **Tableau Desktop**, **Tableau Public**, or **Tableau Cloud**.

---

## 1. Overview & Data Pipeline

VocalSense AI automatically persists audio processing metrics to an embedded SQLite database (`vocalsense.db`) whenever voice cloning, speech synthesis, or audio transcription is performed.

The application exports an analytical dataset directly to:
```
outputs/vocalsense_analytics_export.csv
```
This export is sanitized against spreadsheet-formula injection, formatted in UTF-8 with BOM (`utf-8-sig`) for instant recognition by Tableau, and structured with **one row per unique recording event**. Raw audio binary and full transcripts are excluded from the analytics export to protect privacy and optimize analytical query speeds.

---

## 2. Export Schema & Data Dictionary

| Column Name | Data Type | Tableau Role | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `recording_id` | String | Dimension | Unique UUID/Identifier for the recording event | `f47ac10b-58cc-4372-a567-0e02b2c3d479` |
| `created_at` | DateTime | Dimension | UTC ISO 8601 Timestamp of processing | `2026-10-24T10:15:30Z` |
| `operation_type` | String | Dimension | Type of operation (`voice_cloning`, `transcription`) | `voice_cloning` |
| `file_name` | String | Dimension | Source or generated audio filename | `sample_speaker_male.wav` |
| `duration_seconds` | Float | Measure | Length of the audio recording in seconds | `4.13` |
| `word_count` | Integer | Measure | Total words in transcript or synthesized text | `14` |
| `character_count` | Integer | Measure | Total characters in processed text | `88` |
| `language_code` | String | Dimension | ISO 639-1 language code (`en`, `es`, `fr`, etc.) | `en` |
| `processing_status`| String | Dimension | Operational outcome (`success`, `failed`) | `success` |
| `processing_duration_ms` | Float | Measure | Total end-to-end processing latency in milliseconds | `3420.5` |
| `estimated_words_per_minute`| Float | Measure | Estimated speaking pace (WPM) based on duration | `165.2` |
| `mean_pitch_hz` | Float | Measure | Estimated fundamental frequency ($F_0$) in Hertz | `124.8` |
| `rms_energy` | Float | Measure | Root Mean Square signal energy | `0.0824` |
| `spectral_centroid_hz` | Float | Measure | Timbral spectral centroid brightness in Hertz | `2450.1` |
| `speaker_similarity` | Float | Measure | Cosine similarity score between speaker embeddings | `0.8412` |

---

## 3. Step-by-Step Tableau Connection & Setup

Follow these steps in **Tableau Desktop** or **Tableau Public**:

### Step 1: Connect to the Dataset
1. Open Tableau.
2. Under **Connect** $\to$ **To a File**, select **Text file**.
3. Navigate to your VocalSense AI directory and select:
   ```
   outputs/vocalsense_analytics_export.csv
   ```
4. Verify the Data Source preview. Tableau will display all 15 columns.

### Step 2: Verify Field Types
Verify that Tableau has assigned the correct data types:
* `created_at`: Click the icon above the header $\to$ Ensure it is **Date & Time**.
* `recording_id`, `operation_type`, `file_name`, `language_code`, `processing_status`: Ensure **String / Abc**.
* `duration_seconds`, `processing_duration_ms`, `estimated_words_per_minute`, `mean_pitch_hz`, `rms_energy`, `spectral_centroid_hz`, `speaker_similarity`: Ensure **Number (decimal) / #**.
* `word_count`, `character_count`: Ensure **Number (whole) / #**.

### Step 3: Create Tableau Calculated Fields
In the left Data pane, click the drop-down arrow next to the search bar and select **Create Calculated Field...** to add the following standardized formulas:

1. **Total Unique Recordings (`[Total Recordings]`):**
   ```tableau
   COUNTD([recording_id])
   ```

2. **Processing Duration in Seconds (`[Processing Time (Sec)]`):**
   ```tableau
   [processing_duration_ms] / 1000.0
   ```

3. **Real-Time Factor / Latency Ratio (`[Real-Time Factor]`):**
   ```tableau
   ([processing_duration_ms] / 1000.0) / NULLIF([duration_seconds], 0)
   ```

4. **Success Indicator (`[Is Success]`):**
   ```tableau
   IF [processing_status] = 'success' THEN 1 ELSE 0 END
   ```

5. **Failure Indicator (`[Is Failed]`):**
   ```tableau
   IF [processing_status] = 'failed' THEN 1 ELSE 0 END
   ```

6. **Speaking Pace Categorization (`[Speaking Pace Category]`):**
   ```tableau
   IF ISNULL([estimated_words_per_minute]) THEN "No Transcript"
   ELSEIF [estimated_words_per_minute] < 120 THEN "Slow (<120 WPM)"
   ELSEIF [estimated_words_per_minute] <= 160 THEN "Conversational (120-160 WPM)"
   ELSE "Rapid (>160 WPM)"
   END
   ```

---

## 4. Tableau Dashboard Specifications

### Dashboard 1: Speech Activity Overview
* **Target Audience:** Engineering Leads, Project Managers, ML Operations
* **Key Business Questions:**
  * How many speech recordings have been processed across operations?
  * What is the cumulative audio volume processed (in minutes and hours)?
  * How does speech activity trend day-over-day?
  * How are recording lengths distributed?

#### Recommended Visualizations:
1. **KPI Banner (Top Row):**
   * *Card 1:* Total Unique Recordings (`COUNTD([recording_id])`).
   * *Card 2:* Total Audio Duration (`SUM([duration_seconds]) / 60` minutes).
   * *Card 3:* Total Words Processed (`SUM([word_count])`).
   * *Card 4:* Success Rate (`SUM([Is Success]) / COUNTD([recording_id]) * 100%`).
2. **Daily Activity & Volume Trend (Middle Left):**
   * *Type:* Dual-axis line and bar chart.
   * *Columns:* `DAY([created_at])`.
   * *Rows (Axis 1):* `COUNTD([recording_id])` (Bars).
   * *Rows (Axis 2):* `SUM([duration_seconds]) / 60` (Line).
   * *Color:* By `[operation_type]`.
3. **Audio Duration Distribution (Middle Right):**
   * *Type:* Histogram / Binned Bar Chart.
   * *Bins:* `duration_seconds` (bin size: 2.0 seconds).
   * *Rows:* `COUNTD([recording_id])`.
4. **Duration vs. Word Count Relationship (Bottom):**
   * *Type:* Scatter Plot.
   * *Columns:* `[duration_seconds]`.
   * *Rows:* `[word_count]`.
   * *Marks:* Circle (Color: `[operation_type]`, Detail: `[file_name]`).
   * *Trendline:* Linear regression line illustrating speech density.

---

### Dashboard 2: Speech Characteristics & Acoustics
* **Target Audience:** Speech Researchers, Linguists, Quality Assurance Engineers
* **Key Business Questions:**
  * How does estimated speaking pace (WPM) vary across recordings?
  * What are the pitch distributions ($F_0$) between different speaker profiles?
  * What is the language distribution across uploaded recordings?

#### Recommended Visualizations:
1. **Estimated Speaking Pace Distribution:**
   * *Type:* Box Plot / Jitter Scatter Plot.
   * *Columns:* `[Speaking Pace Category]`.
   * *Rows:* `[estimated_words_per_minute]`.
   * *Tooltip:* File name, duration, and exact WPM.
2. **Pitch ($F_0$) vs. Spectral Centroid Acoustic Mapping:**
   * *Type:* Scatter Plot.
   * *Columns:* `[mean_pitch_hz]`.
   * *Rows:* `[spectral_centroid_hz]`.
   * *Color:* `[operation_type]`.
   * *Interpretation:* Clusters indicate distinct speaker pitch registers (e.g., Male ~70-130 Hz vs. Female ~180-240 Hz).
3. **Language Breakdown:**
   * *Type:* Donut Chart or Horizontal Treemap.
   * *Dimension:* `[language_code]`.
   * *Measure:* `COUNTD([recording_id])`.

---

### Dashboard 3: Processing Performance & MLOps
* **Target Audience:** Backend Developers, DevOps, AI Engineers
* **Key Business Questions:**
  * How does inference latency relate to recording duration (Real-Time Factor)?
  * Are processing latencies stable or degrading over time?
  * What is the operational failure rate?

#### Recommended Visualizations:
1. **Processing Latency vs. Recording Duration:**
   * *Type:* Scatter Plot with Reference Line.
   * *Columns:* `[duration_seconds]`.
   * *Rows:* `[Processing Time (Sec)]`.
   * *Reference Line:* 45-degree line representing 1.0x Real-Time Factor (RTF). Points below the line are faster than real-time; points above indicate CPU compute overhead.
2. **Real-Time Factor (RTF) Histogram:**
   * *Type:* Distribution Histogram.
   * *Measure:* `[Real-Time Factor]`.
   * *Average Line:* Reference line displaying mean RTF across all successful jobs.
3. **Success vs. Failure Status:**
   * *Type:* Stacked Bar Chart.
   * *Columns:* `DAY([created_at])`.
   * *Rows:* `COUNTD([recording_id])`.
   * *Color:* `[processing_status]` (Green: `success`, Red: `failed`).

---

## 5. Dataset Refresh Procedure

Whenever new speech synthesis or transcription operations occur in VocalSense AI:

1. Click **Export Tableau Analytics Dataset (CSV)** in the VocalSense AI web interface (Tab 4), or send a GET request to `/api/analytics/export`.
2. In Tableau:
   * Go to **Data** menu $\to$ Select `vocalsense_analytics_export` $\to$ Click **Refresh** (or press `F5`).
   * Tableau immediately re-reads the updated CSV file, updating all KPIs, scatter plots, and time-series charts dynamically.

---

## 6. Privacy & Data Integrity Rules
* **No Raw Audio in Exports:** The CSV export contains only metadata and acoustic/temporal metrics. Raw WAV bytes are never stored or exported.
* **No Full Transcripts:** Full sentence transcripts are omitted from analytics exports to prevent PII exposure.
* **Anti-CSV Injection:** Text fields are sanitized against formula execution.
