#!/usr/bin/python

'''
    Name: 
        Marvin Duro
    CWID: 
        891583437
    Filename: 
        stegaimage.py
    Description:
        This program demonstrates steganography in the form of
        hidden textual messages in images. View README.txt
        for more details.
'''

from PIL import Image
import sys
import argparse

class StegaImage:
    def __init__(self, filename):
        """Creates a new "steganography-enabled" image.
        
        Args:
            filename: A path of the image to be opened.

        Raises:
            ValueError: If the image is too small (<11 pixels).
        """

        self.image = Image.open(filename)
        self.data = list(self.image.getdata())
        if self._raw_bits_limit() < 32:
            raise ValueError("This image is too small. Image must have at least 11 pixels.")
    
    def _get_bit(self, offset):
        """Gets the value of the bit at a specified offset.

        Args:
            offset: Distance from the bottom-left "bit" of the image.

        Raises:
            IndexError: If the specified offset is outside of the image's bounds.
        """

        offset_max = self._raw_bits_limit()-1
        if offset > offset_max: 
            raise IndexError("Bit offset too large. Limit for this image is {}".format(offset_max))

        pixel_index = -(offset + 1) // 3
        pixel_data = self.data[pixel_index]
        band_index = offset%3
        return pixel_data[band_index] & 1

    def _set_bit(self, offset, new_value):
        """Sets the value of the bit at a specified offset.
        
        Args:
            offset: Distance from the bottom-left "bit" of the image.
            new_value: The new value for the bit. Must be 1 or 0.

        Raises:
            ValueError: If anything other than 1 or 0 is set as the new value.
            IndexError: If the specified offset is outside of the image's bounds.
        """

        offset_max = self._raw_bits_limit()-1
        if offset > offset_max: 
            raise IndexError("Bit offset too large. Limit for this image is {}".format(offset_max))

        pixel_index = -(offset + 1) // 3
        pixel_data = self.data[pixel_index]
        pixel_data_as_list = list(pixel_data)
        band_index = offset%3
        if new_value == 1:
            pixel_data_as_list[band_index] |= 1
        elif new_value == 0:
            pixel_data_as_list[band_index] &= ~1
        else:
            raise ValueError("A bit can only be set to 1 or 0.")

        self.data[pixel_index] = tuple(pixel_data_as_list)

    def _raw_bits_limit(self):
        """Gets the maximum number of raw encodable bits in the image."""

        return len(self.data) * 3

    def _message_bits_limit(self):
        """Gets the maximum number of encodable bits for the message in the image"""

        return self._raw_bits_limit() - 11*3

    def save(self, filename, filetype=None):
        """Saves the image at its current state to a new file.

        Note:
            A file type of PNG (.png) is recommended.

        Args:
            filename: A path to while the image will be saved.
                The file type is determined by the file extension.

        Raises:
            KeyError: If the filename doesn't have a valid file extension and filetype isn't set.
        """

        self.image.putdata(self.data)
        if filetype:
            self.image.save(filename, filetype)
        else:
            self.image.save(filename)

    def read(self):
        """Reads the message encoded in the image.
        
        Raises:
            RuntimeError: If the encoded length is longer than the longest possible message.
        """

        # Read the length of the embedded message.
        msg_length = 0
        for i in range(0, 32):
            bit = self._get_bit(i)
            msg_length += bit << (31-i)

        # Throw something if the message length is longer than what
        # the image can hold.
        # (this probably also means that there wasn't a message in the
        # image in the first place)
        if msg_length > self._raw_bits_limit() - 11*3:
            raise RuntimeError("The message length is {} bits, but the image can only store"
                "at most {} message bits".format(msg_length, self._message_bits_limit()))

        # Read the message character-by-character.
        message = ""
        for i in range(33, 33 + msg_length, 8):
            char_bits = 0
            for j in range(8):
                char_bits += self._get_bit(i+j) << (7-j)

            char = chr(char_bits)
            message += char

        return bytearray(message)

    def write(self, message):
        """Writes a new message onto the image.

        Args:
            message: The message that will be embedded onto the image.
        """

        # Length-encoding step.
        length_in_bits = len(message)*8
        for i in range(0, 32):
            self._set_bit(i, (length_in_bits >> (31-i)) & 1)
        
        # Message-encoding step.
        message_as_bytes = bytearray(message)
        for i in range(0, length_in_bits):
            byte_index = (i) // 8
            bit_offset = 7 - (i%8)
            self._set_bit(33 + i, (message_as_bytes[byte_index] >> (bit_offset)) & 1)

        return

    def message_will_fit(self, message):
        """Checks if a message will fit into the image.

        Args:
            message: The message we want to check.
        """

        return len(message) * 8 <= self._message_bits_limit()

# argparse setup starts here.
# Callback for the "write" mode.
def write_command(args):
    stega_img = None
    try:
        stega_img = StegaImage(args.input_image)
    except ValueError as e:
        print(e)
        exit(1)

    message = ""
    if args.phrase:
        message = bytearray(args.phrase)
    elif args.stdin:
        message = bytearray(sys.stdin.read())
    elif args.file:
        with open(args.file, "rb") as input_file:
            message = bytearray(input_file.read())

    if stega_img.message_will_fit(message):
        stega_img.write(message)

        output_dest = None
        filetype = None
        if args.output_image:
            output_dest = args.output_image
            if args.type:
                filetype = args.filetype
        else:
            output_dest = sys.stdout
            if args.type:
                filetype = args.type
            else:
                filetype = "png"

        try:
            stega_img.save(output_dest, filetype)
        except KeyError:
            stega_img.save(output_dest, "png")
            
        sys.exit(0)
    else:
        print("The message being hidden is too large.")
        sys.exit(1)

# Callback for the "read" mode.
def read_command(args):
    stega_img = None
    try:
        stega_img = StegaImage(args.input_image)
    except ValueError as e:
        print(e)
        exit(1)

    message = None
    try:
        message = stega_img.read()
    except RuntimeError as e:
        print(e)
        exit(1)
        
    if args.output_file:
        with open(args.output_file, "wb") as f:
            f.write(message)
    else:
        print(message)

    exit(0)

parser = argparse.ArgumentParser()

# This program has two modes: read and write.
subparsers = parser.add_subparsers()

# Read mode usage:
# $ stegaimage read INPUT_IMAGE
# -- Will print out the message embedded in INPUT_IMAGE
read_parser = subparsers.add_parser("read", 
    help="""reads the embedded message in an image and outputs the message to stdout.
    enter `./stegaimage.py read --help` for more info.""")
read_parser.set_defaults(func=read_command)
read_parser.add_argument("input_image", help="a path to an image from which a hidden message will be read.")
read_parser.add_argument("output_file", nargs="?", type=str, help="a path to a file into which the result will be saved")

# Write mode usage:
# $ stegaimage write INPUT_IMAGE OUTPUT_IMAGE [--phrase | --stdin | --file]
# -- Will embed a message into INPUT_IMAGE and saves the results into OUTPUT_IMAGE
# -- Input can be a phrase (from argv directly), from stdin, or from a file.
write_parser = subparsers.add_parser("write", 
    help="""embeds a message into an image.
    enter `./stegaimage.py write --help` for more info.""")
write_parser.set_defaults(func=write_command)
write_parser.add_argument("input_image", type=str, help="a path to an image into which the message will be embedded")
write_parser.add_argument("output_image", nargs="?", type=str, help="a path to an image into which the result will be saved")
write_parser.add_argument("-t", "--type", help="filetype hint. overrides the filetype of output_image.")
phrase_group = write_parser.add_mutually_exclusive_group()
phrase_group.add_argument("-p", "--phrase", help="embed a brief phrase into the image")
phrase_group.add_argument("-s", "--stdin", help="embed input from stdin into the image", action="store_true")
phrase_group.add_argument("-f", "--file", help="embed input from a file into the image")

args = parser.parse_args()
args.func(args)
