Pipeline - acoustic analysis atypical speech

Step 1: Manual orthographic transcription
- Script: praat-transcriptie.script
- Input: [name].wav
- Output: [name].tg

Loops through all wav files in the directory and creates empty textgrids to enter the orthographic transcriptions.

Step 2: Forced Alignment
- Manual: ManualFA.docx



Step 3: Checking the forced alignment
- Protocol: Protocol_Praat_check_alignment.docx
- Script: praat-check.script
- Input: [name].wav and [name].TextGrid files
- Output: [name]_checked.tg


Step 4: Acoustic analysis
- Script: LabeledSegmentAnalysis.praat
- Input: [name].wav and [name]_checked.tg
- Output: .txt file (results.txt) and analysis.info

Calculates duration, pitch variability, pitch (Min, Max, Mean), intensity (Min, Max, Mean), formants, and centre of gravity on the word level (tier 2) and the phoneme level (tier 3).

Step 5: Combine all data into one data file
- Script: extract_results.py
- Input: 
- Output: extracted_info.xlsx