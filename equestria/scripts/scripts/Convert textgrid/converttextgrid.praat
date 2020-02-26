# convert short textgrid to full textgrid
# 19 June 2019, Xing Wei

form Obtain Path
    sentence tgdir
endform

Create Strings as file list... list 'tgdir$'/*.tg
filenum = Get number of strings

for i from 1 to filenum
    select Strings list
    file$ = Get string... i
    #basename$ = file$ - ".TextGrid" + ".tg"
    Read from file... 'tgdir$'/'file$'
    Save as text file... 'tgdir$'/'file$'-converted.tg
endfor
