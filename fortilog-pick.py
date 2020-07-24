import argparse
import csv
import glob
import gzip
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter_plus as tkp
from collections import OrderedDict
from datetime import datetime as dt
from pathlib import Path
import threading


class LogFile():
    ''' logfile management class '''
    def __init__(self, filename: str, mode: str = 'rt', *args, **kwargs):
        ''' Initialise a new object.
            open the file "filename"
            if filename is "*.gz", open by gzip.open(), else by open().
            if filename is "-", input from sys.stdin

        Args:
            filename: (str), filename
        Raises:
            ValueError: If "filename" is directory'
            FileExistsError: If "filename" does not exist
        '''
        self.filename = Path(filename)

        # if filename is directory, raise Exception
        if self.filename.exists():
            if self.filename.is_dir():
                raise ValueError(f'"{filename}" is directory')
        # if filename dose not exist, raise Exception
        elif self.filename.name != '-':
            raise FileExistsError(f'"{filename}" not found')

        # if filename is "-", input from sys.stdin
        if self.filename.name == '-':
            self.input_fh = sys.stdin
        # if filename is "*.gz", open by gzip.open()
        elif self.filename.suffix == '.gz':
            self.input_fh = gzip.open(self.filename, mode, *args, **kwargs)
        # otherwise, open by open()
        else:
            self.input_fh = open(self.filename, mode, *args, **kwargs)
        self.csv_in = csv.reader(self.input_fh)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.input_fh != sys.stdin:
            self.input_fh.close()

    def pickup_columns(self, fields_list: list, lines: int, file=sys.stdout):
        csv_out = csv.writer(file, lineterminator='\n')
        csv_out.writerow(fields_list)
        if lines == 0:
            for columns_list in self.csv_in:
                columns_dict = dict([col.split('=') for col in columns_list if col and '=' in col])
                csv_out.writerow([columns_dict.get(key) for key in fields_list])
        else:
            for columns_list, i in zip(self.csv_in, range(lines)):
                columns_dict = dict([col.split('=') for col in columns_list if col and '=' in col])
                csv_out.writerow([columns_dict.get(key) for key in fields_list])

    def create_items(self, lines=99):
        if self.input_fh == sys.stdin:
            return {}
        pos = self.input_fh.tell()    # Save the current pos of a file
        self.input_fh.seek(0)
        fields_dict = OrderedDict()
        for columns_list, i in zip(self.csv_in, range(lines)):
            fields_dict.update(
                dict([col.split('=') for col in columns_list if col and '=' in col]))
        self.input_fh.seek(pos)       # Restore the file pos
        return fields_dict


class GUI():
    def __init__(self, items_list):
        class Checkbutton(tk.Checkbutton):
            def __init__(self, *args, variable=False, **kwargs):
                self.var = tk.BooleanVar(value=variable)
                kwargs['variable'] = self.var
                super().__init__(*args, **kwargs)

        class Button(ttk.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        root = tk.Tk()
        root.title('fortilog picker')
        self.lb = tkp.ItemSelectionListbox(root, items_list, pickup_fields)
        self.lb.pack(fill=tk.BOTH, expand=1)
        fr = tk.Frame(root)
        fr.pack()

        self.cb1 = Checkbutton(fr, text='output to csv file', variable=args.csv)
        self.cb1.pack(side=tk.LEFT, padx=3, pady=3)
        self.cb2 = Checkbutton(fr, text='output first 5 lines', variable=True)
        self.cb2.pack(side=tk.LEFT, padx=3, pady=3)
        self.bt = ttk.Button(root, width=20, text='Exec', command=self.__thread)
        self.bt.pack()
        root.mainloop()

    def __thread(self):
        fields = self.lb.get_var()
        if fields == []:
            return
        th = threading.Thread(target=self.__output, args=(fields,))
        th.start()

    def __output(self, fields: list):
        text = self.bt["text"]
        lines = 5 if self.cb2.var.get() else args.lines
        self.bt.config(state=tk.DISABLED, text="Running")
        output(fields, self.cb1.var.get(), lines)
        self.bt.config(state=tk.NORMAL, text=text)


def gen_filename(*args):
    ''' filename generator '''
    for pattern in args:
        for fname in glob.iglob(pattern, recursive=True):
            yield Path(fname)


def output(fields: list, csv_bool: bool, lines: int):
    if fields == []:
        raise ValueError('specified fields are empty')
    suffix = dt.now().strftime(r'-%Y%m%d-%H%M%S.csv')   # Suffix name
    for fname in gen_filename(*args.filename):
        if not fname.is_file():
            continue
        print('Read:', fname, file=sys.stderr)
        with LogFile(fname) as log:
            # If "-o" or "--csv" option is specified, output to csv file.
            if csv_bool:
                output_fh = open(str(fname) + suffix, 'wt', newline='\r\n')
            else:
                output_fh = sys.stdout
            log.pickup_columns(fields, lines, output_fh)
            if csv_bool:
                output_fh.close()


def read_fields(filename: str) -> list:
    ''' read field_file

    Args:
        filename: (str), filename
    Returns:
        list: list(str), fileds list
    Rises:
        FileNotFoundError: filename is not found
        ValueError: filename is empty
    '''
    try:
        with open(filename, 'rt') as f:
            fields = [row.rstrip() for i, row in zip(range(1000), f.readlines())]
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(0)
    if fields == []:
        raise ValueError('f{filename} is empty')
        sys.exit(0)
    return fields


def read_items(fname_pattern: str):
    ''' read items from csv file

    Args:
        fname_pattern: (str), filename pattern (wildcard)
    Returns:
        OrderedDict:
    Raises:
        FileNotFoundError: glob(fname_pattern) is empty
    '''
    # If first specified filename is not found, sys.exit
    for fname in gen_filename(fname_pattern):
        with LogFile(fname) as f:
            return f.create_items()
    else:
        print(f'No such file or directory: \'{fname_pattern}\'', file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    # command line argument
    parser = argparse.ArgumentParser(
        description='Output specified fields from CSV file (format: "field1=value","field2=value",)')
    parser.add_argument(
        'filename', type=str, nargs='*', help='CSV filename (accept wildcards and gzip file)')
    parser.add_argument(
        '-f', '--field', type=str, metavar='field_file', help='fields description file')
    parser.add_argument(
        '-o', '--csv', action='store_true', help='output to CSV file (filename-yyyymmdd-hhmmss.csv)')
    parser.add_argument(
        '-l', '--lines', type=int, metavar='num', default=0, help='output lines')
    args = parser.parse_args()

    # If "-f" or "--field" option is specified, read pickup_fields from file
    pickup_fields = read_fields(args.field) if args.field else None

    # If the filename is not specified and pickup_fields is specified, input from sys.stdin
    if args.filename == []:
        if pickup_fields is None:
            parser.error('If input from STDIN, "-f" or "--fields" option is required.\n')
        with LogFile('-') as f:
            f.pickup_columns(pickup_fields, args.lines)

    # If the filename is specified and pickup_fields is not specified, goto GUI mode
    elif pickup_fields is None:
        GUI(list(read_items(args.filename[0]).keys()))
    # Standard mode
    else:
        output(pickup_fields, args.csv, args.lines)
