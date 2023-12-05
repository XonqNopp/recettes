#!/bin/sh
set -ex
cd _build
mv html recettes
tar cJf recettes.tar.xz recettes
mv recettes html
scp recettes.tar.xz 10.64.75.1:.gi
rm recettes.tar.xz
ssh 10.64.75.1
