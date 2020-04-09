@echo off
echo Runnig Kaldi from Dragonfly CLI

set currentpath=%~dp0

TITLE Caster: Status Window

python kaldi_module_loader_plus.py
