#!/bin/sh
# Upload to website (only from job network)
set -e
cd _build
mv html recettes
tar cJf recettes.tar.xz recettes
mv recettes html
scp recettes.tar.xz 10.64.75.1:.gi/
rm recettes.tar.xz
cd ..
ssh 10.64.75.1
