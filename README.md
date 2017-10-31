* Marvin Duro
* 891583437
* CPSC 353-01
* Reza Nikoopour

# StegaImage: Hiding secrets in plain sight.

**StegaImage** is a program that allows a user to:

1. write a hidden message to an image, and
2. read a hidden message from an image.


## Architecture

A class called `StegaImage` encapsulates the functionalities required for
`read`ing from, `write`ing to, and `save`ing a "steganography-enabled" image. 

The command-line interface, powered by the `argparse` module, imitates 
the interface of popular command line tools, such as `apt` or `openssl`.

As an extension of the project, arbitrary binary data (read: other images!)
can be written into an image.


## Requirements

This program requires `Python 2` and the `Pillow` module to run.


## Instructions

This program can be run in two modes: `read` and `write`

### `read` Mode

`read` mode reads a message from an image. The following command:

    $ python stegaimage.py read input_image.png

Will output the message hidden in `input_image.png` to stdout.

To write output to a file instead, an optional third parameter can
be provided. The following command:

    $ python stegaimage.py read input_image.png output.txt

Will write the message hidden in `input_image.png` to the 
file `output.txt` instead.

for more help regarding `read` mode, run:

    $ python stegaimage.py read --help

### `write` Mode

`write` mode writes a message into an image. The following command:

    $ python stegaimage.py write input_image.png output_image.png --phrase "Hello, World!"

Will write the phrase "Hello, World!" into `input_image.png`, and saves the output
to `ouput_image.png`

The `output\_image` parameter is actually optional. Omitting this paramter will cause the image
to be outputed to stdout.

To specify the type of image to output, use the `--type` parameter, like so:

    $ python stegaimage.py write input_image.png output_image.png --type png --phrase "Hello, World!"

This will force the output's filetype into png, regardless of the file extension given for `output_image`    

The above example gets the input message from argv (via the `--phrase` argument.) The full
list of ways in which to input the message is as follows:

#### --stdin, -s

The following command:

    $ python stegaimage.py write input_image.png output_image.png --stdin < message_file.txt

will take input from stdin (in this case, the file `message_file.txt` is redirected as input) 
and hides the input into the image.

If a file isn't redirected into stdin, then the user can input into the console directly. 
Input can then be stopped with `EOF` (`Ctrl-D`).

#### --file, -f

The following command:

    $ python stegaimage.py write input_image.png output_image.png --file message_file.txt

will take input from the file called `message.txt` and hides the input into the image.

#### --phrase, -p

The following command:

    $ python stegaimage.py write input_image.png output_image.png --phrase "Hello, World!"

will hide the phrase "Hello, World!" into the image.

for more help regarding `write` mode, run:

    $ python stegaimage.py write --help

### Extra Features

Arbitrary data (not just textual data) can be written to an image.

The following command:

    $ python stegaimage.py write input_image.png output_image.png --file hidden_image.png

Will hide `hidden_image.png` in `input_image.png` and saves the output to `output_image.png`


To recover `hidden_image.png` from `output_image.png`, the following command can be run:

    $ python stegaimage.py read output_image.png recovered_hidden_image.png

