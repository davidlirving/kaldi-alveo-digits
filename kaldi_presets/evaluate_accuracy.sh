#!/bin/sh
# usage: $0 /path/to/decode.1.log
# Validates a decode.1.log against expected Alveo transcriptions
# Decode logs can be found in kaldi_prep/exp/mono/decode/log/
grep -Ev '^(LOG|#|add|gmm|apply)' $1 | \
  sed -e '
    s/\s\+/,/;
    s/\_\_\+/,/g;
    s/\_\-\_\+/,/g;
    s/zero/0/g;
    s/oh/0/g;
    s/one/1/g;
    s/two/2/g;
    s/three/3/g;
    s/four/4/g;
    s/five/4/g;
    s/six/4/g;
    s/seven/7/g;
    s/eight/8/g;
    s/nine/9/g;
    s/\s\+/_/g;
    s/.$//;
    ' | \
      awk -F',' '
      $2 != $4 {
          failed += 1
          print $3,"=> Fail. Expected",$2,"got",$4 ;
      }
      { total += 1 }
      END { print failed,"/",total, "transcriptions incorrect.","("(1-failed/total)*100"% accuracy)" ; } 
      '
