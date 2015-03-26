#!/bin/bash
echo 'removing files...'
echo '$ rm nums100encoded nums100decoded'
rm nums100encoded nums100decoded
echo 'encoding numbers in nums100 to nums100encoded file...'
echo '$ cat nums100 | python varbyte_encoder.py > nums100encoded'
cat nums100 | python varbyte_encoder.py > nums100encoded
echo 'decoding from nums100encoded to nums100decoded...'
echo '$ cat nums100encoded | python varbyte_decoder.py > nums100decoded'
cat nums100encoded | python varbyte_decoder.py > nums100decoded
echo 'checking...'
echo '$ diff nums100 nums100decoded'
diff nums100 nums100decoded