# Meeting 1 summary
In short: the tool is for aligning speech with text. It is used by two different audiences

1. Students from ‘letterkunde’
2. Instrument for researchers (e.g. AI researchers)

It is meant to be used for multiple modalities: language, text, signs. It teaches students for example how the process of aligning text with speech, but also the other named modalities. Once these have been aligned, one can segment the parts, and use them for further research. 
One can also look at the ‘signal’ (speech or different) of a word. You call this mandatory aligning functionality forced alignment (hence the name). Functionalities to support the process already exist as a ‘parts’ of the funnel. It is our task to align these parts with on another, intuitively. The sum of these parts is what we refer to as the complete ‘funnel’.

The sign language falls outside the scope of this assignment.

The big challenge of this assignment is making the whole process user friendly. That is, connect all the existing parts into a user friendly interface. That means, user friendly for a non-technical student that has absolutely no interest in CS. Working with a command line is not considered user friendly by these students. We will need to think about what the best way would be to make it user friendly. 
The individual parts that we will be connecting are in the material provided on GitHub. They make use of different coding languages. 
These two aspects will be the deciding factor in what programming language(s) we will decide to use.

**Must have**
A user friendly and intuitive user interface
All the individual parts working together, seamlessly.
The option to export data at each part of the stage
User must be able to manually (re-)align text with modalities at each stage.
Use the output of each stage automatically and seamlessly in the next stage

**Should have**
Support for Grapheenoneem (will get into later)
Support various export formats (e.g. CSV) - this is different from the feature in must have, because we would need to convert filetypes.

**Could have**
Automatic segmentation on ‘tone’ level
Manipulate data in some ways in the tool (detail to be specified)
Support various other variables like speech speed. 

**Won’t have time**
