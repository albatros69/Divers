#!/bin/bash

for f in * ; do
    ([ -d $f/.git ] && cd $f && echo "Mise à jour de $f..." && git pull);
done

