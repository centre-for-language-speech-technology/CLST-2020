########################################################################
#                                                                      #
# FUNCTION: SCRIPT Calculation F0(min,max,mean,variability), Intensity #    
#                  Pitch variability, Formants, Centre of gravity      #
#  AUTHOR: J. Kerkhoff                                                 #
#                                                                      #
#  DATE: maart 2015                                                    #
#                                                                      #
#  COPYRIGHT:  University of Nijmegen                                  #
#              Department of Language and Speech                       #
#              Erasmusplein 1                                          #
#              P.O. Box 9103, 6500 HD  Nijmegen                        #
#              The Netherlands.                                        #
#                                                                      #
########################################################################
form Analysis of labeled Intervals
  comment Analysis files:
    sentence input_directory C:\
    sentence input_files *.wav
    sentence result_file results.txt
  comment Which segments should be analysed?
    positive tier_number 3
    sentence match_label_(interval) * (#:all intervals;*=not empty intervals)
    sentence begin_end_labels_(point) SIL (# - # = segments between all labels)
  comment Segment analysis options:
    boolean Duration yes
    boolean Pitch_variability yes
	 boolean Pitch_Min_Max_Mean yes
    boolean Intensity_Min_Max_Mean yes
    boolean Formants yes
    boolean Centre_of_gravity yes
  comment Settings Pitch Analysis
    real Time_step 0.0
    positive Pitch_floor_(Hz) 75
    positive Pitch_ceiling_(Hz) 600
  comment Settings Formant Analysis
    integer Max_number_of_formants 5
    positive Maximum_formant_(Hz) 5500 (= adult female)
    positive Window_length_(s) 0.025
    positive Preemphasis_from_(Hz) 50
endform

########### Preparations #############
semitones = 0
kill_octave_jumps = 0
smooth_pitch = 0
interpolate_pitch = 0
# determine directory:
if (right$(input_directory$,1) = "\")
  directory$ = input_directory$
else
  directory$ = input_directory$ + "\"
endif

# remove existing result file
resultFile$ = directory$ + result_file$
if fileReadable(resultFile$)
   pause Overwrite result file: continue
   filedelete 'resultFile$'
endif

# interval match label
interval$ = extractWord$("'match_label$'","")
startLabel$ = extractWord$("'begin_end_labels$'","")
endLabel$ = extractWord$("'begin_end_labels$'","-")

########### End Preparations #############

# clear info screen
clearinfo

##### Write settings to message screen #####
printline
printline Settings:
printline Input files 'tab$' 'directory$''input_files$'
printline Result file 'tab$' 'resultFile$'
printline Tier number 'tab$' 'tier_number'
printline label interval 'tab$' 'interval$'
printline labels 'tab$' 'startLabel$' - 'endLabel$'
printline
printline Results:
##### Write settings to result file #####
fileappend "'resultFile$'" 'directory$''input_files$', Tier number 'tier_number''newline$'
#fileappend "'resultFile$'" Results:'newline$'
##### End writing settings ##################

########### Make list of audio files #############
Create Strings as file list... list 'directory$''input_files$'
numberOfFiles = Get number of strings

##### Start reading and labeling for all files in the list #####
for ifile to numberOfFiles

   select Strings list
   fileName$ = Get string... ifile
   Read from file... 'directory$''fileName$'

   ### search last sound/grid file
   select all
   soundname$ = selected$ ("Sound",-1)
 
   Read from file... 'directory$''soundname$'_checked.tg
   select TextGrid 'soundname$'_checked
   plus Sound 'soundname$'


   ##### place or move existing labels #####
   #Edit
   #if 'pause' 
   #  pause Modify labels
   #endif

   ##### save TextGrid file #####
   #select TextGrid 'soundname$'_checked
   #Write to text file... 'directory$''soundname$'.TextGrid
   
   ### Write info ###
   printline
   printline File: 'soundname$'
   fileappend "'resultFile$'" 'newline$''soundname$'

   ###### Analyze audio file, calculate praat objects ############
   call AnalyzeAudio
   call ComputeAnalysis 'tier_number'

   ### remove used files ###
   select all
   minus Strings list
   Remove
endfor

##### End for all files in the list #####

### Write info screen ###
filedelete 'directory$'analysis.info
fappendinfo 'directory$'analysis.info

### remove rest 
select Strings list
Remove


#---------------Procedures-------------------#
##############################################
procedure AnalyzeAudio

   # Initilaize counters
    if (duration)
      interval_counter = 0
      interval_durations = 0
    endif  
    if (pitch_variability or pitch_Min_Max_Mean)
      select Sound 'soundname$'
      To Pitch... 'time_step' 'pitch_floor' 'pitch_ceiling'
   # for calculating curve-mean
      Down to PitchTier
   # Convert to semitones
      if (semitones)
         Formula... hertzToSemitones(self)
      endif
   # Remove octave jumps
      if (kill_octave_jumps)
         Kill octave jumps
         Rename... dummy
         select Pitch 'soundname$'
         Remove
         select Pitch dummy
         Rename... 'soundname$'
      endif
   # Smooth Pitch contour
      if (smooth_pitch)
         Smooth: 10
         Rename... dummy
         select Pitch 'soundname$'
         Remove
         select Pitch dummy
         Rename... 'soundname$'
      endif
   # Interpolate Pitch contour
      if (interpolate_pitch)
         Interpolate
         Rename... dummy
         select Pitch 'soundname$'
         Remove
         select Pitch dummy
         Rename... 'soundname$'
      endif

  # Calculate voided and unvoiced parts
#     To PointProcess
#     To TextGrid (vuv): 0.02, 0.01

   endif
   if intensity_Min_Max_Mean
      select Sound 'soundname$'
      To Intensity... 'pitch_floor' 0 yes
   endif
   if formants
      select Sound 'soundname$'
      To Formant (burg)... time_step max_number_of_formants maximum_formant window_length preemphasis_from
   endif
endproc


#############################################################
##### Calculate Pitch/Intensity/formants from interval tier             
#############################################################

procedure ComputeAnalysis tierNumber
 
  ##### check tier type #####
  select TextGrid 'soundname$'_checked
  tier = Is interval tier... 'tier_number'
   if (tier)
     tierType$ = "interval"
   else
     tierType$ = "point"
   endif

  ##### Analyze interval tier #####
  select TextGrid 'soundname$'_checked

  ##### if INTERVAL tier #####
   if (tierType$ = "interval") or (tierType$ = "Interval")
      numberOfIntervals = Get number of intervals... 'tierNumber'
      for interval from 2 to (numberOfIntervals-1)
         select TextGrid 'soundname$'_checked
         label$ = Get label of interval... 'tierNumber' interval
         labelSegment$ = label$
         index = rindex(label$,interval$)
         if (index>0) or (interval$ = "#") or ((interval$ = "*") and ((label$ <> "") and (label$ <> "<SIL>") and (label$ <> "SIL") and (label$ <> "<SPN>")))
            timeBegin = Get starting point... 'tierNumber' interval
	          timeEnd = Get end point... 'tierNumber' interval
            call AnalysisFunctions timeBegin timeEnd
         endif
     endfor 
   endif

   ##### if POINT tier #####
   if (tierType$ = "point") or (tierType$ = "Point")
      numpoints = Get number of points... 'tierNumber'
         
      # analyze all labeled segments
      if (startLabel$ = "#") and (endLabel$ = "#")
         for point from 1 to (numpoints-1)
            select TextGrid 'soundname$'_checked
            timeBegin = Get time of point... 'tierNumber' point
            timeEnd = Get time of point... 'tierNumber' (point+1)
            label1$ = Get label of point... 'tierNumber' (point)
            label2$ = Get label of point... 'tierNumber' (point+1)
            labelSegment$ = label1$ + "-" + label2$
            if labelSegment$ = ""
               labelSegment$ = "-"
            endif
            call AnalysisFunctions timeBegin timeEnd
         endfor
      endif

      # analyze all matched labeled segments 
      if (startLabel$ <> "#") and (endLabel$ <> "#")
         point = 1
         while point < (numpoints)
            firstFound = 0
            secondFound = 0
            select TextGrid 'soundname$'_checked
            label$ = Get label of point... 'tierNumber' point
            index = rindex(label$,startLabel$)
            while (index=0) and (point < numpoints)
               point = point + 1
               label$ = Get label of point... 'tierNumber' point
               index = rindex(label$,startLabel$)
            endwhile
            if (index>0)
              firstFound = 1
              labelSegment$ = label$
              timeBegin = Get time of point... 'tierNumber' point
            endif
            while (point < numpoints)
               point = point + 1
               label$ = Get label of point... 'tierNumber' point
               index = rindex(label$,endLabel$)
               while (index=0) and (point < numpoints)
                  point = point + 1
                  label$ = Get label of point... 'tierNumber' point
                  index = rindex(label$,endLabel$)
               endwhile
               if (index=0) and (point = numpoints)
                  printline Endlabel -'endLabel$'- not found......, endlabel = last label 
               endif
               if (index>0)
                 secondFound = 1
                 labelSegment$ = labelSegment$ + "-" + label$
                 timeEnd = Get time of point... 'tierNumber' point    
               endif
            endwhile

            if firstFound and secondFound
               if labelSegment$ = ""
                  labelSegment$ = "-"
               endif
               call AnalysisFunctions timeBegin timeEnd
            endif
            point = point + 1
         endwhile
      endif
   endif
   if (duration)
     ##### write results to console (in ms) #####
     printline Total intervals 'interval_counter:0' Total duration 'interval_durations:0'
     ##### write results to file (in ms/Hz) #####
     fileappend "'resultFile$'"  tot_int 'interval_counter:0' tot_dur 'interval_durations:0'
     ##### End writing #####
   endif  
endproc


#############################################################
##### Check analysis settings           
#############################################################
procedure AnalysisFunctions timeBegin timeEnd

#  ##### write label to console #####
#  printline Segment: 'labelSegment$'
#  ##### write label to file #####
#  fileappend "'resultFile$'"  'labelSegment$'
#  ##### End writing #####

  if duration
     call Durationvalues timeBegin timeEnd
  endif
  if pitch_Min_Max_Mean
     call PitchMinMaxMean timeBegin timeEnd
  endif
  if pitch_variability
     call PitchVariability timeBegin timeEnd
  endif
  if intensity_Min_Max_Mean
     call IntensityMinMaxMean timeBegin timeEnd
  endif
  if formants
      call Formantvalues timeBegin timeEnd
  endif
  if centre_of_gravity
     call Gravityvalue timeBegin timeEnd
  endif
endproc

#############################################################
##### Calculate Duration of an interval             
#############################################################
procedure Durationvalues timeBegin timeEnd

   intervalDuration = (timeEnd - timeBegin)*1000
   interval_counter = interval_counter + 1
   interval_durations = interval_durations + intervalDuration
   ##### write results to console (in ms) #####
   printline Duration 'labelSegment$' 'intervalDuration:0'
   ##### write results to file (in ms/Hz) #####
   fileappend "'resultFile$'"  'labelSegment$' 'intervalDuration:0'
   ##### End writing #####
endproc

#############################################################
##### Calculate Pitch of all labels             
#############################################################
procedure PitchAllLabels

   select TextGrid 'soundname$'
   ##### if INTERVAL tier #####
   if (tierType$ = "interval") or (tierType$ = "Interval")
      numberOfIntervals = Get number of intervals... 'tierNumber'
      for interval from 2 to (numberOfIntervals-1)
          select TextGrid 'soundname$'_checked
          label$ = Get label of interval... 'tierNumber' interval
          timeBegin = Get starting point... 'tierNumber' interval
          timeEnd = Get end point... 'tierNumber' interval
          select Pitch 'soundname$'
          pitchBegin = Get value at time... 'timeBegin' Hertz linear
          if pitchBegin = undefined
             pitchBegin = 0
          endif
          pitchEnd = Get value at time... 'timeEnd' Hertz linear
          if pitchEnd = undefined
             pitchEnd = 0
          endif
          timeBegin = timeBegin * 1000
          timeEnd = timeEnd * 1000
          ##### write results to console (in ms) #####
          printline 'label$': 'timeBegin:0' 'pitchBegin:2' 'timeEnd:0' 'pitchEnd:2'
          ##### write results to file (in ms/Hz) #####
          fileappend "'resultFile$'"  'label$' 'timeBegin:0' 'pitchBegin:2' 'timeEnd:0' 'pitchEnd:2'
          ##### End writing #####
      endfor
    endif
    
   ##### if POINT tier #####
   if (tierType$ = "point") or (tierType$ = "Point")
      numberOfSegments = Get number of points... 'tierNumber'
      for point from 1 to numberOfSegments
          select TextGrid 'soundname$'_checked
          label$ = Get label of point... 'tierNumber' point
          timeValue =  Get time of point... 'tierNumber' point
          select Pitch 'soundname$'
          pitchValue = Get value at time... 'timeValue' Hertz linear
          if pitchValue = undefined
             pitchValue = 0
          endif
          timeValue = timeValue * 1000
          ##### write results to console (in ms) #####
          printline 'label$': 'timeValue:0' 'pitchValue:2'
          ##### write results to file (in ms/Hz) #####
          fileappend "'resultFile$'"  'label$' 'timeValue:0' 'pitchValue:2'
          ##### End writing #####
     endfor
  endif
endproc

##############################################
procedure PitchVariability timeBegin timeEnd
   
    select Sound 'soundname$'
    Extract part: 'timeBegin', 'timeEnd', "rectangular", 1, "no"
	#samps = Get number of samples
	dur = (timeEnd - timeBegin) * 1000
	#x = ('samps' * 'dur')
	#printline 'x'
	nocheck To Pitch... 0 'pitch_floor' 'pitch_ceiling'
	if dur < 40
		meanSlope = undefined
	else
		meanSlope = Get mean absolute slope: "Hertz"
		select Sound 'soundname$'_part
		plus Pitch 'soundname$'_part
		Remove
	endif

   ##### write results to console (in Hz/sec) #####
   printline Pitch variability 'labelSegment$' 'meanSlope:2'
   ##### write results to file (in Hz/sec) #####
   fileappend "'resultFile$'"  'labelSegment$' 'meanSlope:2'
   ##### End writing #####

endproc

#############################################################
##### Calculate Pitch Min-Max-Mean of an interval             
#############################################################
procedure PitchMinMaxMean timeBegin timeEnd

   select Pitch 'soundname$'
   minPitch = Get minimum... timeBegin timeEnd Hertz Parabolic
   if minPitch = undefined
      minPitch = 0
   endif
   maxPitch = Get maximum... timeBegin timeEnd Hertz Parabolic
   if maxPitch = undefined
      maxPitch = 0
   endif
   meanPitch = Get mean... timeBegin timeEnd Hertz
   if meanPitch = undefined
      meanPitch = 0
   endif
   stdDevPitch = Get standard deviation: timeBegin, timeEnd, "Hertz"
   if minPitch = maxPitch
	  stdDevPitch = 0
   endif
   select PitchTier 'soundname$'
   meanPitchCurve = Get mean (curve)... timeBegin timeEnd

   ##### write results to console (in Hz) #####
#   printline Pitch (min, max, mean(points), mean(curves)) 'labelSegment$' 'minPitch:0' 'maxPitch:0' 'meanPitch:0' 'meanPitchCurve:0'
   printline Pitch (min, max, mean, stddev) 'labelSegment$' 'minPitch:2' 'maxPitch:2' 'meanPitch:2' 'stdDevPitch:2'
   ##### write results to file (in ms/Hz) #####
#   fileappend "'resultFile$'"  'labelSegment$' 'minPitch:0' 'maxPitch:0' 'meanPitch:0' 'meanPitchCurve:0'
   fileappend "'resultFile$'"  'labelSegment$' 'minPitch:2' 'maxPitch:2' 'meanPitch:2' 'stdDevPitch:2'
   ##### End writing #####
endproc


##############################################
procedure IntensityMinMaxMean timeBegin timeEnd

   select Intensity 'soundname$'
   minIntens =  Get minimum: timeBegin, timeEnd, "Parabolic"
   maxIntens = Get maximum: timeBegin, timeEnd, "Parabolic"
   meanIntens = Get mean: timeBegin, timeEnd, "energy"
   stDevIntens = Get standard deviation: timeBegin, timeEnd

   ##### write results to console (in Hz) #####
#   printline Pitch (min, max, mean(points), mean(curves)) 'labelSegment$' 'minPitch:0' 'maxPitch:0' 'meanPitch:0' 'meanPitchCurve:0'
   printline Intensity (min, max, mean, stdev) 'labelSegment$' 'minIntens:2' 'maxIntens:2' 'meanIntens:2' 'stDevIntens:2'
   ##### write results to file (in ms/Hz) #####
#   fileappend "'resultFile$'"  'labelSegment$' 'minPitch:0' 'maxPitch:0' 'meanPitch:0' 'meanPitchCurve:0'
   fileappend "'resultFile$'"  'labelSegment$' 'minIntens:2' 'maxIntens:2' 'meanIntens:2' 'stDevIntens:2'
   ##### End writing #####
 
endproc

##############################################
procedure Formantvalues timeBegin timeEnd
         
   ### calculation time point, middle of segment
   timePoint = (timeEnd + timeBegin)/2
   
   ### calculation formant values
   select Formant 'soundname$'
   formant1 = Get value at time... 1 'timePoint' Hertz Linear
   formant2 = Get value at time... 2 'timePoint' Hertz Linear
   formant3 = Get value at time... 3 'timePoint' Hertz Linear
   formant4 = Get value at time... 4 'timePoint' Hertz Linear

   ##### write results to console (in ms/Hz) #####
   timePoint = timePoint * 1000 
   printline Formants (F1, F2, F3, F4) 'labelSegment$' 'formant1:0' 'formant2:0' 'formant3:0' 'formant4:0' 
   ##### write results to file (in ms) #####
   fileappend "'resultFile$'"  'labelSegment$' 'formant1:0' 'formant2:0' 'formant3:0' 'formant4:0'
   ##### End writing #####

endproc

##############################################
procedure Gravityvalue timeBegin timeEnd

   select Sound 'soundname$'
   Extract part: 'timeBegin', 'timeEnd', "Hanning", 1, "no"
   To Spectrum... yes
    
   gravityValue = Get centre of gravity... 2
   select Sound 'soundname$'_part
   plus Spectrum 'soundname$'_part
   Remove

   
   ##### write results to console (Hz)#####
   printline Centre of gravity 'labelSegment$' 'gravityValue:0'
   ##### write results to file #####
   fileappend "'resultFile$'"  'labelSegment$' 'gravityValue:0'
   ##### End writing #####
   
endproc
##############################################
