# QuACK

QuACK (**Qu**antum **A**nalog **C**ontrol **K**it) is a project written by students at Harvey Mudd College for HRL Laborartories, LLC as part of the HMC Engineering Clinic Program. It extends the open-source qick package to work with a custom Digital-to-Analog Converter (DAC) set-up.

## Contents
This repository contains firmware and software. The `firmware` directory has the source code for our newest block, axi_pvp_gen. The `qickquack_lib` directory contains the Python package and demo Jupyter Notebook.

## Setup instructions
To install qickquack on your ZCU216, clone this repository and copy the whole thing over to the RFSoC. (Something like pscp -r qickquack xilinx@192.168.2.99:/home/xilinx/jupyter_notebooks). **Rename** the directory `qickquack_dir`, because there is some bug where installing the package of the same name confuses the pip installer. Navigate to qickquack_demos and run the demo notebook to install qickquack locally.